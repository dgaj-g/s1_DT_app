#!/usr/bin/env python3
"""Generate smaller Supabase migrations for the approved Unit 1 import.

The first all-in-one import migration was too large for the remote migration
connection. This generator splits the import into safe chunks:

1. foundation data, bucket and objectives;
2. inactive question chunks;
3. sources/assets;
4. links;
5. final activation.

Until the final activation migration succeeds, imported questions remain
inactive and old live questions are left untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_stage5_supabase_import_sql import (
    DEFAULT_INPUT,
    REPO_ROOT,
    build_objective_rows,
    build_topic_rows,
    question_rows,
    sql_json,
    unique_asset_rows,
)


MIGRATION_DIR = REPO_ROOT / "supabase" / "migrations"
MANUAL_DIR = REPO_ROOT / "supabase" / "manual" / "stage5_chunked_import"
LEGACY_IMPORT_MIGRATION = MIGRATION_DIR / "20260504131500_import_unit1_approved_question_bank.sql"


def chunks(values: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [values[index:index + size] for index in range(0, len(values), size)]


def write_sql(path: Path, sql: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sql, encoding="utf-8")
    print(f"Wrote {path} ({path.stat().st_size} bytes)")


def foundation_sql(payload: dict[str, Any]) -> str:
    topics = build_topic_rows(payload)
    objectives = build_objective_rows()
    # Do not enable every topic until final activation succeeds.
    for topic in topics:
        topic["is_enabled"] = False

    return f"""-- Stage 5 Unit 1 import foundation.
-- Imported questions remain inactive until the final activation migration.

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

commit;
"""


def question_chunk_sql(rows: list[dict[str, Any]], part_number: int) -> str:
    return f"""-- Stage 5 Unit 1 question import chunk {part_number:02d}.
-- Questions are inserted inactive/draft first. Final activation happens later.

begin;

with
{sql_json("question_payload", rows)},
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
  'draft',
  false,
  null
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
    qa_status = 'draft',
    is_active = false,
    reviewed_at = null;

commit;
"""


def sources_assets_sql(payload: dict[str, Any]) -> str:
    sources = payload.get("content_sources", [])
    assets = unique_asset_rows(payload)
    return f"""-- Stage 5 Unit 1 source and asset metadata import.

begin;

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

commit;
"""


def links_sql(payload: dict[str, Any]) -> str:
    question_ids = [{"external_id": q["question_external_id"]} for q in payload.get("live_questions", [])]
    asset_lookup = {
        asset["asset_external_id"]: (asset["storage_bucket"], asset["storage_path"])
        for asset in payload.get("question_assets", [])
    }
    asset_links = []
    for link in payload.get("question_asset_links", []):
        bucket, path = asset_lookup[link["asset_external_id"]]
        asset_links.append({**link, "asset_bucket": bucket, "asset_storage_path": path})

    return f"""-- Stage 5 Unit 1 link import.

begin;

with
{sql_json("question_id_payload", question_ids)},
question_rows as (
  select *
  from question_id_payload,
  jsonb_to_recordset(question_id_payload.data) as row(external_id text)
)
delete from public.question_source_links qsl
using public.questions q, question_rows r
where qsl.question_id = q.id
  and q.external_id = r.external_id;

with
{sql_json("question_id_payload", question_ids)},
question_rows as (
  select *
  from question_id_payload,
  jsonb_to_recordset(question_id_payload.data) as row(external_id text)
)
delete from public.question_asset_links qal
using public.questions q, question_rows r
where qal.question_id = q.id
  and q.external_id = r.external_id;

with
{sql_json("question_id_payload", question_ids)},
question_rows as (
  select *
  from question_id_payload,
  jsonb_to_recordset(question_id_payload.data) as row(external_id text)
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

commit;
"""


def activation_sql(payload: dict[str, Any]) -> str:
    topics = build_topic_rows(payload)
    question_ids = [{"external_id": q["question_external_id"]} for q in payload.get("live_questions", [])]
    expected_count = payload.get("summary", {}).get("promoted_question_count", len(question_ids))

    return f"""-- Stage 5 Unit 1 final activation.
-- This is the only migration that makes the imported bank student-facing.

begin;

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
update public.topics t
set title = r.title,
    is_enabled = true,
    display_order = r.display_order
from topic_rows r
where t.slug = r.slug;

with
{sql_json("question_id_payload", question_ids)},
question_rows as (
  select *
  from question_id_payload,
  jsonb_to_recordset(question_id_payload.data) as row(external_id text)
),
payload_topics as (
  select distinct q.topic_id
  from public.questions q
  join question_rows r on r.external_id = q.external_id
)
update public.questions q
set is_active = false,
    qa_status = 'draft',
    reviewed_at = null
where q.topic_id in (select topic_id from payload_topics)
  and (
    q.external_id is null
    or q.external_id not in (select external_id from question_rows)
  );

with
{sql_json("question_id_payload", question_ids)},
question_rows as (
  select *
  from question_id_payload,
  jsonb_to_recordset(question_id_payload.data) as row(external_id text)
)
update public.questions q
set is_active = true,
    qa_status = 'published',
    reviewed_at = timezone('utc'::text, now())
from question_rows r
where q.external_id = r.external_id;

do $$
declare
  imported_count integer;
begin
  with
  question_id_payload as (
    select $unit1_json${json.dumps(question_ids, ensure_ascii=False)}$unit1_json$::jsonb as data
  ),
  question_rows as (
    select *
    from question_id_payload,
    jsonb_to_recordset(question_id_payload.data) as row(external_id text)
  )
  select count(*)
  into imported_count
  from public.questions q
  join question_rows r on r.external_id = q.external_id
  where q.is_active = true
    and q.qa_status = 'published';

  if imported_count <> {expected_count} then
    raise exception 'Unit 1 import expected {expected_count} active approved questions, found %', imported_count;
  end if;
end
$$;

commit;
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--chunk-size", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    rows = question_rows(payload)

    write_sql(LEGACY_IMPORT_MIGRATION, foundation_sql(payload))

    for part_number, part_rows in enumerate(chunks(rows, args.chunk_size), start=1):
        migration = MIGRATION_DIR / f"202605041316{part_number:02d}_import_unit1_questions_part_{part_number:02d}.sql"
        write_sql(migration, question_chunk_sql(part_rows, part_number))

    write_sql(MIGRATION_DIR / "20260504132700_import_unit1_sources_assets.sql", sources_assets_sql(payload))
    write_sql(MIGRATION_DIR / "20260504132800_import_unit1_links.sql", links_sql(payload))
    write_sql(MIGRATION_DIR / "20260504132900_activate_unit1_approved_bank.sql", activation_sql(payload))

    write_sql(MANUAL_DIR / "20260504131500_import_unit1_foundation.sql", foundation_sql(payload))
    for part_number, part_rows in enumerate(chunks(rows, args.chunk_size), start=1):
        write_sql(
            MANUAL_DIR / f"202605041316{part_number:02d}_import_unit1_questions_part_{part_number:02d}.sql",
            question_chunk_sql(part_rows, part_number),
        )
    write_sql(MANUAL_DIR / "20260504132700_import_unit1_sources_assets.sql", sources_assets_sql(payload))
    write_sql(MANUAL_DIR / "20260504132800_import_unit1_links.sql", links_sql(payload))
    write_sql(MANUAL_DIR / "20260504132900_activate_unit1_approved_bank.sql", activation_sql(payload))


if __name__ == "__main__":
    main()
