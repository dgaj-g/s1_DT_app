#!/usr/bin/env python3
"""Repair visual-context links for the approved Stage 5 Unit 1 bank.

The original import linked only the visual assets explicitly carried through the
staging payload. That missed later subquestions from the same past-paper item,
for example spreadsheet/database questions that refer to a chart, query design,
sample view, relationship diagram, or spreadsheet cells.

This script builds a migration that:
- registers every extracted past-paper figure from image_mapping.json;
- links the best matching visual to every live question from the same paper item;
- quarantines any remaining high-risk, context-dependent question that still has
  no visual after the repair links are applied.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT.parent / "GCSE Unit 1 Revision Project"
DEFAULT_PAYLOAD = REPO_ROOT / "supabase" / "imports" / "unit1_stage5_approved_live_payload.json"
DEFAULT_IMAGE_MAPPING = SOURCE_ROOT / "_automark" / "figures" / "image_mapping.json"
DEFAULT_FIGURES_DIR = SOURCE_ROOT / "_automark" / "figures"
DEFAULT_ASSET_PACKAGE_DIR = REPO_ROOT / "supabase" / "imports" / "question_assets_upload" / "question-imports"
DEFAULT_MIGRATION = REPO_ROOT / "supabase" / "migrations" / "20260504152000_repair_stage5_visual_context_links.sql"
DEFAULT_SUMMARY = REPO_ROOT / "docs" / "stage-5-visual-context-repair-2026-05-04.json"
DEFAULT_REPORT = REPO_ROOT / "docs" / "stage-5-visual-context-repair-2026-05-04.md"

TOPIC_TO_SLUG = {
    "topic 1: digital data": "digital-data",
    "topic 2: digital applications": "digital-applications",
    "topic 3: database applications": "database-applications",
    "topic 4: spreadsheet applications": "spreadsheet-applications",
    "topic 5: computer hardware": "computer-hardware",
    "topic 6: network technologies": "network-technologies",
    "topic 7: cyberspace, network security and data transfer": "cyberspace-network-security-and-data-transfer",
    "topic 8: cloud technology": "cloud-technology",
    "topic 9: ethical, legal and environmental impact": "ethical-legal-and-environmental-impact",
    "topic 10: software": "software",
    "topic 11: health and safety": "health-and-safety",
    "topic 12: changes in employment opportunities, skills requirements and work practices": "changes-in-employment-opportunities-skills-requirements-and-work-practices",
}

QUESTION_REF_RE = re.compile(r"(?P<year>20\d{2})\s+Q(?P<num>\d+)(?P<parts>(?:\([a-zivx0-9]+\))*)", re.IGNORECASE)
PART_RE = re.compile(r"\(([a-zivx0-9]+)\)", re.IGNORECASE)

HIGH_RISK_CONTEXT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\brefer to (?:the|a|this|that)?\s*(?:diagram|figure|table|spreadsheet|screenshot|chart|image|sample view)\b",
        r"\bshown (?:above|below|in)\b",
        r"\bsample view\b",
        r"\bscreenshot\b",
        r"\bchart\b",
        r"\bgraph\b",
        r"\bquery\b",
        r"\breport\b",
        r"\bcriteria\b",
        r"\bsort(?:ed|ing)?\b",
        r"\brelationship\b",
        r"\btbl[A-Z0-9]+\b",
        r"\bcell(?:s)?\s+[A-Z]+\d+",
        r"\bcell range\b",
        r"\brange\s+[A-Z]+\d+",
        r"\bworksheet\b",
    ]
]


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def parse_question_ref(text: str) -> dict[str, Any] | None:
    match = QUESTION_REF_RE.search(text or "")
    if not match:
        return None
    parts = [part.lower() for part in PART_RE.findall(match.group("parts") or "")]
    year = match.group("year")
    number = match.group("num")
    return {
        "year": year,
        "number": number,
        "root": f"{year} Q{number}",
        "first_part": parts[0] if parts else "",
        "parts": parts,
        "full": f"{year} Q{number}{''.join(f'({p})' for p in parts)}",
    }


def topic_slug_for_mapping(topic: str) -> str:
    topic_key = normalize_text(topic).lower()
    if topic_key in TOPIC_TO_SLUG:
        return TOPIC_TO_SLUG[topic_key]
    raise ValueError(f"No topic slug mapping for image topic: {topic}")


def infer_asset_kind(topic_slug: str, caption: str) -> str:
    text = f"{topic_slug} {caption}".lower()
    if "chart" in text or "graph" in text:
        return "chart"
    if "spreadsheet" in text or "table" in text or "sample" in text or "form" in text:
        return "table_image"
    if "diagram" in text or "relationship" in text or "topology" in text:
        return "diagram"
    return "figure"


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def existing_link_map(payload: dict[str, Any]) -> dict[str, set[str]]:
    links: dict[str, set[str]] = defaultdict(set)
    for link in payload.get("question_asset_links", []):
        links[link["question_external_id"]].add(link["asset_external_id"])
    return links


def build_asset_records(mapping_path: Path, figures_dir: Path, package_dir: Path) -> list[dict[str, Any]]:
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    assets: list[dict[str, Any]] = []
    for item in mapping:
        order = int(item["order"])
        source_path = figures_dir / f"image{order}.png"
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        topic_slug = topic_slug_for_mapping(item["topic"])
        caption = normalize_text(item["question"])
        ref = parse_question_ref(caption)
        if not ref:
            raise ValueError(f"Could not parse source ref from mapping caption: {caption}")
        storage_path = f"{topic_slug}/image{order}.png"
        packaged_path = package_dir / topic_slug / f"image{order}.png"
        packaged_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, packaged_path)
        assets.append(
            {
                "asset_external_id": f"unit1.visual_context.image{order}",
                "asset_kind": infer_asset_kind(topic_slug, caption),
                "storage_bucket": "question-imports",
                "storage_path": storage_path,
                "mime_type": "image/png",
                "alt_text": caption,
                "caption": caption,
                "source_name": f"image{order}.png",
                "source_locator": caption,
                "metadata_json": {
                    "stage5_visual_context_repair": True,
                    "source_relative_path": f"_automark/figures/image{order}.png",
                    "source_question_ref": ref,
                },
                "topic_slug": topic_slug,
                "ref": ref,
                "order": order,
            }
        )
    return assets


def choose_asset_for_question(question: dict[str, Any], assets: list[dict[str, Any]]) -> dict[str, Any] | None:
    q_ref = parse_question_ref(question.get("source_ref", ""))
    if not q_ref:
        return None
    topic_slug = question.get("topic_slug", "")
    candidates = [
        asset
        for asset in assets
        if asset["topic_slug"] == topic_slug and asset["ref"]["root"] == q_ref["root"]
    ]
    if not candidates:
        return None

    exact = [asset for asset in candidates if asset["ref"]["full"].lower() == q_ref["full"].lower()]
    if exact:
        return exact[0]

    same_first_part = [
        asset
        for asset in candidates
        if q_ref["first_part"] and asset["ref"].get("first_part") == q_ref["first_part"]
    ]
    if same_first_part:
        return same_first_part[0]

    # Fall back to the first visual for the same paper question. This is safer
    # than presenting a question that names fields/cells/relationships with no
    # context at all.
    return sorted(candidates, key=lambda asset: asset["order"])[0]


def is_high_risk_without_visual(question: dict[str, Any]) -> bool:
    if question.get("source_type") != "adapted_exam":
        return False
    text_parts = [
        question.get("stem", ""),
        question.get("source_ref", ""),
        json.dumps(question.get("content_blocks_json", []), ensure_ascii=False),
        json.dumps(question.get("response_schema_json", {}), ensure_ascii=False),
    ]
    combined = "\n".join(text_parts)
    return any(pattern.search(combined) for pattern in HIGH_RISK_CONTEXT_PATTERNS)


def build_repair(payload: dict[str, Any], assets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    existing_links = existing_link_map(payload)
    planned_links: list[dict[str, Any]] = []
    effective_links: dict[str, set[str]] = {qid: set(values) for qid, values in existing_links.items()}

    for question in payload.get("live_questions", []):
        asset = choose_asset_for_question(question, assets)
        if not asset:
            continue
        qid = question["question_external_id"]
        asset_id = asset["asset_external_id"]
        if asset_id in effective_links.get(qid, set()):
            continue
        planned_links.append(
            {
                "question_external_id": qid,
                "asset_external_id": asset_id,
                "asset_bucket": asset["storage_bucket"],
                "asset_storage_path": asset["storage_path"],
                "asset_role": "prompt",
                "display_order": 1,
                "block_key": None,
                "link_reason": "visual_context_repair_by_source_question",
            }
        )
        effective_links.setdefault(qid, set()).add(asset_id)

    quarantined: list[dict[str, Any]] = []
    for question in payload.get("live_questions", []):
        qid = question["question_external_id"]
        if effective_links.get(qid):
            continue
        if is_high_risk_without_visual(question):
            quarantined.append(
                {
                    "question_external_id": qid,
                    "topic_slug": question.get("topic_slug"),
                    "difficulty": question.get("difficulty"),
                    "format": question.get("format"),
                    "source_ref": question.get("source_ref"),
                    "stem": question.get("stem"),
                    "reason": "high_risk_context_without_visual_after_repair",
                }
            )

    summary = {
        "asset_records": len(assets),
        "new_links": len(planned_links),
        "existing_links": sum(len(v) for v in existing_links.values()),
        "effective_linked_questions": len(effective_links),
        "quarantined_questions": len(quarantined),
        "quarantine_by_topic_difficulty": {
            f"{topic_slug}/{difficulty}": count
            for (topic_slug, difficulty), count in Counter(
                (item["topic_slug"], item["difficulty"]) for item in quarantined
            ).items()
        },
    }
    return planned_links, quarantined, summary


def sql_literal(value: str | None) -> str:
    if value is None:
        return "null"
    return "'" + str(value).replace("'", "''") + "'"


def json_sql(name: str, value: Any) -> str:
    return f"{name} as (select $unit1_json${json.dumps(value, ensure_ascii=False)}$unit1_json$::jsonb as data)"


def build_migration_sql(assets: list[dict[str, Any]], links: list[dict[str, Any]], quarantined: list[dict[str, Any]]) -> str:
    asset_rows = [
        {
            key: asset[key]
            for key in [
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
            ]
        }
        for asset in assets
    ]
    quarantine_ids = [item["question_external_id"] for item in quarantined]
    return f"""-- Repair Stage 5 visual context links after teacher testing.
--
-- The previous import uploaded available figures but did not attach shared
-- spreadsheet/database visual context to every dependent subquestion. This
-- migration registers all extracted figures, links sibling questions to the
-- relevant visual by source question, and removes any remaining high-risk
-- no-context items from student sessions.

begin;

with
{json_sql('asset_payload', asset_rows)},
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
  coalesce(r.metadata_json, '{{}}'::jsonb)
from asset_rows r
on conflict (storage_path) do update
set asset_kind = excluded.asset_kind,
    storage_bucket = excluded.storage_bucket,
    mime_type = excluded.mime_type,
    alt_text = coalesce(nullif(public.question_assets.alt_text, ''), excluded.alt_text),
    caption = coalesce(public.question_assets.caption, excluded.caption),
    source_name = coalesce(public.question_assets.source_name, excluded.source_name),
    source_locator = coalesce(public.question_assets.source_locator, excluded.source_locator),
    metadata_json = public.question_assets.metadata_json || excluded.metadata_json,
    external_id = coalesce(public.question_assets.external_id, excluded.external_id);

alter table public.question_asset_links
  add column if not exists metadata_json jsonb not null default '{{}}'::jsonb;

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
  jsonb_build_object('stage5_visual_context_repair', true, 'reason', r.link_reason)
from link_rows r
join public.questions q on q.external_id = r.question_external_id
join public.question_assets qa on qa.storage_bucket = r.asset_bucket and qa.storage_path = r.asset_storage_path
on conflict (question_id, asset_id, asset_role, display_order) do update
set block_key = excluded.block_key,
    metadata_json = public.question_asset_links.metadata_json || excluded.metadata_json;

update public.questions q
set is_active = false,
    qa_status = 'draft',
    teacher_notes = concat_ws(chr(10), q.teacher_notes, 'Auto-quarantined on 2026-05-04: high-risk question still lacked required visual/context after Stage 5 visual repair.')
where q.external_id in (
  {', '.join(sql_literal(item) for item in quarantine_ids) if quarantine_ids else "select null::text where false"}
);

commit;
"""


def write_report(path: Path, summary: dict[str, Any], quarantined: list[dict[str, Any]]) -> None:
    lines = [
        "# Stage 5 Visual Context Repair",
        "",
        "Date: 2026-05-04",
        "",
        "## Result",
        "",
        f"- Extracted image records registered: `{summary['asset_records']}`",
        f"- New question-image links planned: `{summary['new_links']}`",
        f"- Existing question-image links before repair: `{summary['existing_links']}`",
        f"- Questions with effective visual context after repair: `{summary['effective_linked_questions']}`",
        f"- Questions quarantined because context was still missing: `{summary['quarantined_questions']}`",
        "",
        "## Quarantined Questions",
        "",
    ]
    if not quarantined:
        lines.append("None.")
    else:
        for item in quarantined:
            lines.append(
                f"- `{item['question_external_id']}` ({item['topic_slug']} / {item['difficulty']}): {item['stem']}"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", type=Path, default=DEFAULT_PAYLOAD)
    parser.add_argument("--image-mapping", type=Path, default=DEFAULT_IMAGE_MAPPING)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES_DIR)
    parser.add_argument("--asset-package-dir", type=Path, default=DEFAULT_ASSET_PACKAGE_DIR)
    parser.add_argument("--migration", type=Path, default=DEFAULT_MIGRATION)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    payload = load_payload(args.payload)
    assets = build_asset_records(args.image_mapping, args.figures_dir, args.asset_package_dir)
    links, quarantined, summary = build_repair(payload, assets)

    args.migration.parent.mkdir(parents=True, exist_ok=True)
    args.migration.write_text(build_migration_sql(assets, links, quarantined), encoding="utf-8")
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps({"summary": summary, "quarantined": quarantined}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_report(args.report, summary, quarantined)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
