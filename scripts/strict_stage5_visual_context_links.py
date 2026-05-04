#!/usr/bin/env python3
"""Replace broad Stage 5 visual links with stricter, topic-aware links.

The first visual repair was intentionally aggressive: if a question came from the
same past-paper root, it linked the first available figure. That repaired many
spreadsheet/database questions, but it was unsafe for topics where sibling
subquestions use unrelated visuals. This generator removes those broad repair
links and rebuilds only links that are defensible.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import repair_stage5_visual_context_links as base

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MIGRATION = REPO_ROOT / "supabase" / "migrations" / "20260504163500_strict_visual_context_links.sql"
DEFAULT_SUMMARY = REPO_ROOT / "docs" / "stage-5-strict-visual-context-repair-2026-05-04.json"
DEFAULT_REPORT = REPO_ROOT / "docs" / "stage-5-strict-visual-context-repair-2026-05-04.md"

SHARED_CONTEXT_TOPICS = {"spreadsheet-applications", "database-applications"}

CONTEXT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bcell(?:s)?\s+[A-Z]+\d+",
        r"\b[A-Z]+\d+\s*:\s*[A-Z]+\d+\b",
        r"\bcell range\b",
        r"\bVLOOKUP\b",
        r"\bIF\s+(?:statement|formula)\b",
        r"\bformula\b",
        r"\bchart\b",
        r"\bgraph\b",
        r"\bx-axis\b",
        r"\by-axis\b",
        r"\bdata series\b",
        r"\btable\b",
        r"\btbl[A-Z0-9]+\b",
        r"\bquery\b",
        r"\bcriteria\b",
        r"\bsample view\b",
        r"\bsort(?:ed|ing)?\b",
        r"\brelationship\b",
        r"\bfield(?:s)?\b",
        r"\bprimary key\b",
    ]
]

AXIS_OR_SERIES_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"\bx-axis\b", r"\by-axis\b", r"\bdata series\b", r"\bcell range\b"]
]

REQUIRES_VISUAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bcell(?:s)?\s+[A-Z]+\d+",
        r"\b[A-Z]+\d+\s*:\s*[A-Z]+\d+\b",
        r"\bcell range\b",
        r"\bchart\b",
        r"\bgraph\b",
        r"\bx-axis\b",
        r"\by-axis\b",
        r"\bdata series\b",
        r"\btbl[A-Z0-9]+\b",
        r"\bquery\b",
        r"\bcriteria\b",
        r"\bsample view\b",
        r"\bsort(?:ed|ing)?\b",
        r"\brelationship\b",
    ]
]


def sql_literal(value: Any) -> str:
    if value is None:
        return "null"
    return "'" + str(value).replace("'", "''") + "'"


def json_sql(name: str, value: Any) -> str:
    return f"{name} as (select $${json.dumps(value, ensure_ascii=False)}$${'::jsonb'} as data)"


def question_text(question: dict[str, Any]) -> str:
    return "\n".join(
        str(question.get(key) or "")
        for key in ["stem", "source_ref", "format", "difficulty"]
    )


def wants_shared_context(question: dict[str, Any]) -> bool:
    if question.get("topic_slug") not in SHARED_CONTEXT_TOPICS:
        return False
    text = question_text(question)
    return any(pattern.search(text) for pattern in CONTEXT_PATTERNS)


def wants_base_plus_specific(question: dict[str, Any]) -> bool:
    text = question_text(question)
    return any(pattern.search(text) for pattern in AXIS_OR_SERIES_PATTERNS)


def requires_visual_context_for_student(question: dict[str, Any]) -> bool:
    qid = question.get("question_external_id", "")
    if ".past_paper." not in qid:
        return False
    if question.get("topic_slug") not in SHARED_CONTEXT_TOPICS:
        return False
    text = question_text(question)
    return any(pattern.search(text) for pattern in REQUIRES_VISUAL_PATTERNS)


def unique_assets(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for asset in assets:
        asset_id = asset["asset_external_id"]
        if asset_id in seen:
            continue
        seen.add(asset_id)
        result.append(asset)
    return result[:2]


def choose_assets_for_question(question: dict[str, Any], assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    q_ref = base.parse_question_ref(question.get("source_ref", ""))
    if not q_ref:
        return []

    topic_slug = question.get("topic_slug", "")
    candidates = sorted(
        [
            asset
            for asset in assets
            if asset["topic_slug"] == topic_slug and asset["ref"]["root"] == q_ref["root"]
        ],
        key=lambda asset: asset["order"],
    )
    if not candidates:
        return []

    exact = [asset for asset in candidates if asset["ref"]["full"].lower() == q_ref["full"].lower()]
    same_first_part = [
        asset
        for asset in candidates
        if q_ref["first_part"] and asset["ref"].get("first_part") == q_ref["first_part"]
    ]

    # Exact and same-part matches are defensible across all topics.
    if topic_slug not in SHARED_CONTEXT_TOPICS:
        return unique_assets(exact or same_first_part)

    chosen: list[dict[str, Any]] = []
    base_context = candidates[0]

    if wants_shared_context(question):
        if wants_base_plus_specific(question):
            chosen.append(base_context)
        chosen.extend(exact or same_first_part)
        if not chosen:
            chosen.append(base_context)
    else:
        chosen.extend(exact or same_first_part)

    return unique_assets(chosen)


def build_strict_links(payload: dict[str, Any], assets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    original_links = base.existing_link_map(payload)
    effective_links: dict[str, set[str]] = {qid: set(values) for qid, values in original_links.items()}
    planned_links: list[dict[str, Any]] = []
    reason_counter: Counter[str] = Counter()

    for question in payload.get("live_questions", []):
        qid = question["question_external_id"]
        chosen_assets = choose_assets_for_question(question, assets)
        for display_order, asset in enumerate(chosen_assets, start=1):
            asset_id = asset["asset_external_id"]
            if asset_id in effective_links.get(qid, set()):
                continue
            reason = "strict_exact_or_shared_context"
            if question.get("topic_slug") in SHARED_CONTEXT_TOPICS and asset == chosen_assets[0] and wants_shared_context(question):
                reason = "strict_shared_spreadsheet_database_context"
            planned_links.append(
                {
                    "question_external_id": qid,
                    "asset_external_id": asset_id,
                    "asset_bucket": asset["storage_bucket"],
                    "asset_storage_path": asset["storage_path"],
                    "asset_role": "prompt",
                    "display_order": display_order,
                    "block_key": None,
                    "link_reason": reason,
                }
            )
            effective_links.setdefault(qid, set()).add(asset_id)
            reason_counter[reason] += 1

    quarantined: list[dict[str, Any]] = []
    for question in payload.get("live_questions", []):
        qid = question["question_external_id"]
        if effective_links.get(qid):
            continue
        if requires_visual_context_for_student(question):
            quarantined.append(
                {
                    "question_external_id": qid,
                    "topic_slug": question.get("topic_slug"),
                    "difficulty": question.get("difficulty"),
                    "format": question.get("format"),
                    "source_ref": question.get("source_ref"),
                    "stem": question.get("stem"),
                    "reason": "shared-context spreadsheet/database question still lacks a visual",
                }
            )

    summary = {
        "asset_records": len(assets),
        "strict_links": len(planned_links),
        "original_payload_links": sum(len(values) for values in original_links.values()),
        "effective_linked_questions_after_strict_repair": len([qid for qid, values in effective_links.items() if values]),
        "quarantined_questions": len(quarantined),
        "strict_link_reasons": dict(reason_counter),
        "links_by_topic": dict(Counter(link["question_external_id"].split(".past_paper", 1)[0].split(".practice_bank", 1)[0] for link in planned_links)),
    }
    return planned_links, quarantined, summary


def render_migration(assets: list[dict[str, Any]], links: list[dict[str, Any]], quarantined: list[dict[str, Any]]) -> str:
    asset_payload = [
        {k: asset[k] for k in [
            "asset_external_id",
            "asset_kind",
            "storage_bucket",
            "storage_path",
            "mime_type",
            "alt_text",
            "caption",
            "source_name",
            "source_locator",
            "metadata_json",
        ]}
        for asset in assets
    ]
    quarantine_ids = [item["question_external_id"] for item in quarantined]

    return f"""-- Replace broad Stage 5 visual-context links with stricter topic-aware links.
-- This removes unsafe same-paper visual inference, keeps exact visual matches,
-- and uses shared root visuals only for spreadsheet/database questions where a
-- table, query, chart, cell range, or relationship is part of the prompt.

begin;

alter table public.question_asset_links
  add column if not exists metadata_json jsonb not null default '{{}}'::jsonb;

with removed as (
  delete from public.question_asset_links qal
  where coalesce(qal.metadata_json ->> 'stage5_visual_context_repair', 'false') = 'true'
     or coalesce(qal.metadata_json ->> 'stage5_visual_context_strict_repair', 'false') = 'true'
  returning qal.question_id
)
select count(*) as removed_broad_visual_context_links from removed;

with
{json_sql('asset_payload', asset_payload)},
asset_rows as (
  select *
  from asset_payload p,
  jsonb_to_recordset(p.data) as r(
    asset_external_id text,
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
  r.asset_external_id,
  r.asset_kind::public.question_asset_kind,
  r.storage_bucket,
  r.storage_path,
  r.mime_type,
  r.alt_text,
  r.caption,
  r.source_name,
  r.source_locator,
  r.metadata_json || jsonb_build_object('stage5_visual_context_strict_available', true)
from asset_rows r
on conflict (storage_path) do update
set asset_kind = excluded.asset_kind,
    mime_type = coalesce(public.question_assets.mime_type, excluded.mime_type),
    alt_text = coalesce(public.question_assets.alt_text, excluded.alt_text),
    caption = coalesce(public.question_assets.caption, excluded.caption),
    source_name = coalesce(public.question_assets.source_name, excluded.source_name),
    source_locator = coalesce(public.question_assets.source_locator, excluded.source_locator),
    metadata_json = public.question_assets.metadata_json || excluded.metadata_json,
    external_id = coalesce(public.question_assets.external_id, excluded.external_id);

with
{json_sql('link_payload', links)},
link_rows as (
  select *
  from link_payload p,
  jsonb_to_recordset(p.data) as r(
    question_external_id text,
    asset_external_id text,
    asset_bucket text,
    asset_storage_path text,
    asset_role text,
    display_order integer,
    block_key text,
    link_reason text
  )
)
insert into public.question_asset_links (
  question_id,
  asset_id,
  asset_role,
  display_order,
  block_key,
  metadata_json
)
select
  q.id,
  qa.id,
  r.asset_role::public.question_asset_role,
  coalesce(r.display_order, 1),
  r.block_key,
  jsonb_build_object('stage5_visual_context_strict_repair', true, 'reason', r.link_reason)
from link_rows r
join public.questions q on q.external_id = r.question_external_id
join public.question_assets qa on qa.storage_bucket = r.asset_bucket and qa.storage_path = r.asset_storage_path
on conflict (question_id, asset_id, asset_role, display_order) do update
set block_key = excluded.block_key,
    metadata_json = public.question_asset_links.metadata_json || excluded.metadata_json;

update public.questions q
set is_active = false,
    qa_status = 'draft',
    teacher_notes = concat_ws(chr(10), q.teacher_notes, 'Auto-quarantined on 2026-05-04: spreadsheet/database question still lacked visual context after strict visual repair.')
where q.external_id in (
  {', '.join(sql_literal(item) for item in quarantine_ids) if quarantine_ids else 'select null::text where false'}
);

-- Active in-progress sessions keep JSON snapshots. Refresh them so a session
-- started before this repair receives the corrected visual links immediately.
update public.session_questions sq
set question_snapshot_json = public.build_runtime_question_payload(sq.question_id, sq.id)
from public.sessions s
where s.id = sq.session_id
  and s.completed_at is null
  and sq.question_id is not null;

commit;
"""


def write_report(path: Path, summary: dict[str, Any], quarantined: list[dict[str, Any]]) -> None:
    lines = [
        "# Stage 5 Strict Visual Context Repair",
        "",
        "Date: 2026-05-04",
        "",
        "## What Changed",
        "",
        "- Removed the unsafe broad repair links marked `stage5_visual_context_repair`.",
        "- Rebuilt visual links using exact source references and topic-aware shared context.",
        "- Allowed same-root shared visuals only for spreadsheet/database questions with cells, ranges, charts, queries, fields, or relationships in the prompt.",
        "- Refreshed incomplete session snapshots so old in-progress sessions do not keep stale no-image payloads.",
        "",
        "## Counts",
        "",
        f"- Extracted image records available: `{summary['asset_records']}`",
        f"- Strict question-image links planned: `{summary['strict_links']}`",
        f"- Original payload links retained separately: `{summary['original_payload_links']}`",
        f"- Questions with effective visual context after strict repair: `{summary['effective_linked_questions_after_strict_repair']}`",
        f"- Questions quarantined: `{summary['quarantined_questions']}`",
        "",
        "## Link Reasons",
        "",
    ]
    for reason, count in sorted(summary["strict_link_reasons"].items()):
        lines.append(f"- `{reason}`: `{count}`")
    lines.extend(["", "## Quarantined Questions", ""])
    if quarantined:
        for item in quarantined:
            lines.append(f"- `{item['question_external_id']}` ({item['topic_slug']}, {item['difficulty']}, {item['format']}): {item['source_ref']}")
    else:
        lines.append("- None.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", type=Path, default=base.DEFAULT_PAYLOAD)
    parser.add_argument("--image-mapping", type=Path, default=base.DEFAULT_IMAGE_MAPPING)
    parser.add_argument("--figures-dir", type=Path, default=base.DEFAULT_FIGURES_DIR)
    parser.add_argument("--asset-package-dir", type=Path, default=base.DEFAULT_ASSET_PACKAGE_DIR)
    parser.add_argument("--migration", type=Path, default=DEFAULT_MIGRATION)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    payload = base.load_payload(args.payload)
    assets = base.build_asset_records(args.image_mapping, args.figures_dir, args.asset_package_dir)
    links, quarantined, summary = build_strict_links(payload, assets)

    args.migration.write_text(render_migration(assets, links, quarantined), encoding="utf-8")
    args.summary.write_text(json.dumps({"summary": summary, "links": links, "quarantined": quarantined}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(args.report, summary, quarantined)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Migration: {args.migration}")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
