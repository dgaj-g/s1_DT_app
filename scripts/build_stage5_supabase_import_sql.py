#!/usr/bin/env python3
"""Generate SQL to import the approved Unit 1 live question payload.

The generated SQL is intentionally idempotent:

- questions are upserted by stable external_id;
- old active Unit 1 questions not in the approved payload are retired, not deleted;
- question/source/asset/objective links are rebuilt for imported questions;
- existing auth users, student accounts, passwords, and session history are untouched.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "supabase" / "imports" / "unit1_stage5_approved_live_payload.json"
DEFAULT_MIGRATION = REPO_ROOT / "supabase" / "migrations" / "20260504131500_import_unit1_approved_question_bank.sql"
DEFAULT_MANUAL_SQL = REPO_ROOT / "supabase" / "manual" / "import_unit1_approved_question_bank.sql"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_objective_rows() -> list[dict[str, Any]]:
    from unit1_objectives import OBJECTIVES_BY_CODE

    grouped: dict[str, list[Any]] = defaultdict(list)
    for objective in OBJECTIVES_BY_CODE.values():
        topic_slug = objective.code.rsplit(".", 1)[0]
        grouped[topic_slug].append(objective)

    rows: list[dict[str, Any]] = []
    for topic_slug in sorted(grouped):
        for display_order, objective in enumerate(sorted(grouped[topic_slug], key=lambda item: item.code), start=1):
            rows.append(
                {
                    "topic_slug": topic_slug,
                    "objective_code": objective.code,
                    "title": objective.title,
                    "description": objective.description,
                    "display_order": display_order,
                }
            )
    return rows


def build_topic_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    topic_titles: dict[str, str] = {}
    for question in payload.get("live_questions", []):
        topic_slug = question["topic_slug"]
        metadata = question.get("metadata_json", {}) if isinstance(question.get("metadata_json"), dict) else {}
        # The topic title is not needed by the runtime payload, so infer the
        # human-readable fallback from the slug if no metadata title exists.
        title = metadata.get("topic_title") or topic_slug.replace("-", " ").title()
        topic_titles[topic_slug] = title

    display_order = {
        "digital-data": 1,
        "software": 2,
        "database-applications": 3,
        "spreadsheet-applications": 4,
        "computer-hardware": 5,
        "network-technologies": 6,
        "cyberspace-network-security-and-data-transfer": 7,
        "cloud-technology": 8,
        "ethical-legal-and-environmental-impact": 9,
        "changes-in-employment-opportunities-skills-requirements-and-work-practices": 10,
        "health-and-safety": 11,
        "digital-applications": 12,
    }
    preferred_titles = {
        "digital-data": "Digital data",
        "software": "Software",
        "database-applications": "Database applications",
        "spreadsheet-applications": "Spreadsheet applications",
        "computer-hardware": "Computer hardware",
        "network-technologies": "Network technologies",
        "cyberspace-network-security-and-data-transfer": "Cyberspace, network security and data transfer",
        "cloud-technology": "Cloud technology",
        "ethical-legal-and-environmental-impact": "Ethical, legal and environmental impact",
        "changes-in-employment-opportunities-skills-requirements-and-work-practices": "Changes in employment opportunities, skills requirements and work practices",
        "health-and-safety": "Health and safety",
        "digital-applications": "Digital applications",
    }

    return [
        {
            "slug": slug,
            "title": preferred_titles.get(slug, topic_titles[slug]),
            "is_enabled": True,
            "display_order": display_order.get(slug, 999),
        }
        for slug in sorted(topic_titles, key=lambda item: display_order.get(item, 999))
    ]


def question_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for question in payload.get("live_questions", []):
        metadata = question.get("metadata_json") if isinstance(question.get("metadata_json"), dict) else {}
        metadata = {
            **metadata,
            "stage5_import": {
                "approved_payload": "unit1_stage5_approved_live_payload.json",
                "question_external_id": question["question_external_id"],
            },
        }
        rows.append(
            {
                "external_id": question["question_external_id"],
                "topic_slug": question["topic_slug"],
                "difficulty": question["difficulty"],
                "format": question["format"],
                "adaptive_tier": question["adaptive_tier"],
                "question_family_code": question.get("question_family_code"),
                "selection_weight": question.get("selection_weight", 1),
                "stem": question["stem"],
                "options_json": question.get("options_json") or {},
                "correct_answer_json": question.get("correct_answer_json") or {},
                "markscheme_points_json": question.get("markscheme_points_json") or [],
                "explanation": question.get("explanation") or "",
                "max_marks": question.get("max_marks", 1),
                "content_blocks_json": question.get("content_blocks_json") or [],
                "response_schema_json": question.get("response_schema_json") or {},
                "autograde_rules_json": question.get("autograde_rules_json") or {},
                "tags_json": question.get("tags_json") or [],
                "source_type": question.get("source_type") or "new_original",
                "source_ref": question.get("source_ref") or "",
                "teacher_notes": question.get("teacher_notes") or "",
                "metadata_json": metadata,
            }
        )
    return rows


def unique_asset_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    by_path: dict[tuple[str, str], dict[str, Any]] = {}
    for asset in payload.get("question_assets", []):
        key = (asset["storage_bucket"], asset["storage_path"])
        by_path.setdefault(
            key,
            {
                "external_id": asset["asset_external_id"],
                "asset_kind": asset["asset_kind"],
                "storage_bucket": asset["storage_bucket"],
                "storage_path": asset["storage_path"],
                "mime_type": asset.get("mime_type"),
                "alt_text": asset["alt_text"],
                "caption": asset.get("caption"),
                "source_name": asset.get("source_name"),
                "source_locator": asset.get("source_locator"),
                "metadata_json": asset.get("metadata_json") or {},
            },
        )
    return list(by_path.values())


def sql_json(name: str, value: Any) -> str:
    return f"{name} as (\n  select $unit1_json${json.dumps(value, ensure_ascii=False)}$unit1_json$::jsonb as data\n)"


def build_sql(payload: dict[str, Any]) -> str:
    topics = build_topic_rows(payload)
    objectives = build_objective_rows()
    questions = question_rows(payload)
    sources = payload.get("content_sources", [])
    assets = unique_asset_rows(payload)
    asset_lookup = {
        asset["asset_external_id"]: (asset["storage_bucket"], asset["storage_path"])
        for asset in payload.get("question_assets", [])
    }
    asset_links = []
    for link in payload.get("question_asset_links", []):
        bucket, path = asset_lookup[link["asset_external_id"]]
        asset_links.append({**link, "asset_bucket": bucket, "asset_storage_path": path})

    summary = payload.get("summary", {})

    return f"""-- Generated by scripts/build_stage5_supabase_import_sql.py.
-- Approved Unit 1 question bank import.
-- This is a soft replacement: old questions are retired, not deleted.

begin;

insert into storage.buckets (id, name, public)
values ('question-imports', 'question-imports', true)
on conflict (id) do update
set public = true;

with
{sql_json("topic_payload", topics)},
topic_rows as (
  select *
  from topic_payload,
  jsonb_to_recordset(topic_payload.data) as row(
    slug text,
    title text,
    is_enabled boolean,
    display_order integer
  )
)
insert into public.topics (slug, title, is_enabled, display_order)
select slug, title, is_enabled, display_order
from topic_rows
on conflict (slug) do update
set title = excluded.title,
    is_enabled = excluded.is_enabled,
    display_order = excluded.display_order;

with
{sql_json("objective_payload", objectives)},
objective_rows as (
  select *
  from objective_payload,
  jsonb_to_recordset(objective_payload.data) as row(
    topic_slug text,
    objective_code text,
    title text,
    description text,
    display_order integer
  )
)
insert into public.learning_objectives (
  topic_id,
  objective_code,
  title,
  description,
  display_order,
  is_active
)
select
  t.id,
  r.objective_code,
  r.title,
  r.description,
  r.display_order,
  true
from objective_rows r
join public.topics t on t.slug = r.topic_slug
on conflict (topic_id, objective_code) do update
set title = excluded.title,
    description = excluded.description,
    display_order = excluded.display_order,
    is_active = true;

with
{sql_json("question_payload", questions)},
question_rows as (
  select *
  from question_payload,
  jsonb_to_recordset(question_payload.data) as row(
    external_id text,
    topic_slug text,
    difficulty text,
    format text,
    adaptive_tier text,
    question_family_code text,
    selection_weight numeric,
    stem text,
    options_json jsonb,
    correct_answer_json jsonb,
    markscheme_points_json jsonb,
    explanation text,
    max_marks integer,
    content_blocks_json jsonb,
    response_schema_json jsonb,
    autograde_rules_json jsonb,
    tags_json jsonb,
    source_type text,
    source_ref text,
    teacher_notes text,
    metadata_json jsonb
  )
),
retired as (
  update public.questions q
  set is_active = false,
      qa_status = 'draft',
      reviewed_at = null
  where q.topic_id in (select t.id from public.topics t join question_rows r on r.topic_slug = t.slug)
    and (
      q.external_id is null
      or q.external_id not in (select external_id from question_rows)
    )
  returning q.id
)
insert into public.questions (
  external_id,
  topic_id,
  difficulty,
  format,
  adaptive_tier,
  question_family_code,
  selection_weight,
  stem,
  options_json,
  correct_answer_json,
  markscheme_points_json,
  explanation,
  max_marks,
  content_blocks_json,
  response_schema_json,
  autograde_rules_json,
  tags_json,
  source_type,
  source_ref,
  teacher_notes,
  qa_status,
  is_active,
  reviewed_at
)
select
  r.external_id,
  t.id,
  r.difficulty::public.difficulty_level,
  r.format::public.question_format,
  r.adaptive_tier::public.adaptive_tier,
  r.question_family_code,
  coalesce(r.selection_weight, 1),
  r.stem,
  coalesce(r.options_json, '{{}}'::jsonb),
  coalesce(r.correct_answer_json, '{{}}'::jsonb),
  coalesce(r.markscheme_points_json, '[]'::jsonb),
  r.explanation,
  greatest(1, least(20, coalesce(r.max_marks, 1)))::smallint,
  coalesce(r.content_blocks_json, '[]'::jsonb),
  coalesce(r.response_schema_json, '{{}}'::jsonb),
  coalesce(r.autograde_rules_json, '{{}}'::jsonb),
  coalesce(r.tags_json, '[]'::jsonb),
  r.source_type::public.question_source,
  r.source_ref,
  r.teacher_notes,
  'published',
  true,
  timezone('utc'::text, now())
from question_rows r
join public.topics t on t.slug = r.topic_slug
on conflict (external_id) do update
set topic_id = excluded.topic_id,
    difficulty = excluded.difficulty,
    format = excluded.format,
    adaptive_tier = excluded.adaptive_tier,
    question_family_code = excluded.question_family_code,
    selection_weight = excluded.selection_weight,
    stem = excluded.stem,
    options_json = excluded.options_json,
    correct_answer_json = excluded.correct_answer_json,
    markscheme_points_json = excluded.markscheme_points_json,
    explanation = excluded.explanation,
    max_marks = excluded.max_marks,
    content_blocks_json = excluded.content_blocks_json,
    response_schema_json = excluded.response_schema_json,
    autograde_rules_json = excluded.autograde_rules_json,
    tags_json = excluded.tags_json,
    source_type = excluded.source_type,
    source_ref = excluded.source_ref,
    teacher_notes = excluded.teacher_notes,
    qa_status = 'published',
    is_active = true,
    reviewed_at = timezone('utc'::text, now());

with
{sql_json("source_payload", sources)},
source_rows as (
  select *
  from source_payload,
  jsonb_to_recordset(source_payload.data) as row(
    content_source_external_id text,
    topic_slug text,
    source_kind text,
    title text,
    file_name text,
    year_label text,
    locator_text text,
    metadata_json jsonb
  )
)
insert into public.content_sources (
  external_id,
  topic_id,
  source_kind,
  title,
  file_name,
  year_label,
  locator_text,
  metadata_json
)
select
  r.content_source_external_id,
  t.id,
  r.source_kind::public.content_source_kind,
  r.title,
  r.file_name,
  r.year_label,
  r.locator_text,
  coalesce(r.metadata_json, '{{}}'::jsonb)
from source_rows r
left join public.topics t on t.slug = r.topic_slug
on conflict (external_id) do update
set topic_id = excluded.topic_id,
    source_kind = excluded.source_kind,
    title = excluded.title,
    file_name = excluded.file_name,
    year_label = excluded.year_label,
    locator_text = excluded.locator_text,
    metadata_json = excluded.metadata_json;

with
{sql_json("asset_payload", assets)},
asset_rows as (
  select *
  from asset_payload,
  jsonb_to_recordset(asset_payload.data) as row(
    external_id text,
    asset_kind text,
    storage_bucket text,
    storage_path text,
    mime_type text,
    alt_text text,
    caption text,
    source_name text,
    source_locator text,
    metadata_json jsonb
  )
)
insert into public.question_assets (
  external_id,
  asset_kind,
  storage_bucket,
  storage_path,
  mime_type,
  alt_text,
  caption,
  source_name,
  source_locator,
  metadata_json
)
select
  r.external_id,
  r.asset_kind::public.question_asset_kind,
  r.storage_bucket,
  r.storage_path,
  r.mime_type,
  r.alt_text,
  r.caption,
  r.source_name,
  r.source_locator,
  coalesce(r.metadata_json, '{{}}'::jsonb)
from asset_rows r
on conflict (storage_path) do update
set asset_kind = excluded.asset_kind,
    storage_bucket = excluded.storage_bucket,
    mime_type = excluded.mime_type,
    alt_text = excluded.alt_text,
    caption = excluded.caption,
    source_name = excluded.source_name,
    source_locator = excluded.source_locator,
    metadata_json = excluded.metadata_json,
    external_id = coalesce(public.question_assets.external_id, excluded.external_id);

with
{sql_json("question_payload", questions)},
question_rows as (
  select *
  from question_payload,
  jsonb_to_recordset(question_payload.data) as row(external_id text)
)
delete from public.question_source_links qsl
using public.questions q, question_rows r
where qsl.question_id = q.id
  and q.external_id = r.external_id;

with
{sql_json("question_payload", questions)},
question_rows as (
  select *
  from question_payload,
  jsonb_to_recordset(question_payload.data) as row(external_id text)
)
delete from public.question_asset_links qal
using public.questions q, question_rows r
where qal.question_id = q.id
  and q.external_id = r.external_id;

with
{sql_json("question_payload", questions)},
question_rows as (
  select *
  from question_payload,
  jsonb_to_recordset(question_payload.data) as row(external_id text)
)
delete from public.question_objectives qo
using public.questions q, question_rows r
where qo.question_id = q.id
  and q.external_id = r.external_id;

with
{sql_json("source_link_payload", payload.get("question_source_links", []))},
source_link_rows as (
  select *
  from source_link_payload,
  jsonb_to_recordset(source_link_payload.data) as row(
    question_external_id text,
    content_source_external_id text,
    source_role text,
    note text
  )
)
insert into public.question_source_links (
  question_id,
  content_source_id,
  source_role,
  note
)
select
  q.id,
  cs.id,
  r.source_role,
  r.note
from source_link_rows r
join public.questions q on q.external_id = r.question_external_id
join public.content_sources cs on cs.external_id = r.content_source_external_id
on conflict (question_id, content_source_id, source_role) do update
set note = excluded.note;

with
{sql_json("asset_link_payload", asset_links)},
asset_link_rows as (
  select *
  from asset_link_payload,
  jsonb_to_recordset(asset_link_payload.data) as row(
    question_external_id text,
    asset_external_id text,
    asset_bucket text,
    asset_storage_path text,
    asset_role text,
    display_order integer,
    block_key text
  )
)
insert into public.question_asset_links (
  question_id,
  asset_id,
  asset_role,
  display_order,
  block_key
)
select
  q.id,
  qa.id,
  r.asset_role::public.question_asset_role,
  coalesce(r.display_order, 1),
  r.block_key
from asset_link_rows r
join public.questions q on q.external_id = r.question_external_id
join public.question_assets qa on qa.storage_bucket = r.asset_bucket and qa.storage_path = r.asset_storage_path
on conflict (question_id, asset_id, asset_role, display_order) do update
set block_key = excluded.block_key;

with
{sql_json("objective_link_payload", payload.get("question_objectives", []))},
objective_link_rows as (
  select *
  from objective_link_payload,
  jsonb_to_recordset(objective_link_payload.data) as row(
    question_external_id text,
    objective_code text,
    is_primary boolean,
    display_order integer
  )
)
insert into public.question_objectives (
  question_id,
  objective_id,
  is_primary,
  display_order
)
select
  q.id,
  lo.id,
  coalesce(r.is_primary, false),
  coalesce(r.display_order, 1)
from objective_link_rows r
join public.questions q on q.external_id = r.question_external_id
join public.learning_objectives lo on lo.objective_code = r.objective_code
on conflict (question_id, objective_id) do update
set is_primary = excluded.is_primary,
    display_order = excluded.display_order;

do $$
declare
  imported_count integer;
begin
  select count(*)
  into imported_count
  from public.questions
  where external_id is not null
    and is_active = true
    and qa_status = 'published';

  if imported_count < {summary.get("promoted_question_count", 938)} then
    raise exception 'Unit 1 import expected at least {summary.get("promoted_question_count", 938)} active imported questions, found %', imported_count;
  end if;
end
$$;

commit;
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--migration-output", type=Path, default=DEFAULT_MIGRATION)
    parser.add_argument("--manual-output", type=Path, default=DEFAULT_MANUAL_SQL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_json(args.input)
    sql = build_sql(payload)

    for output in (args.migration_output, args.manual_output):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(sql, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
