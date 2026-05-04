#!/usr/bin/env python3
"""Build teacher-friendly CSV review reports from the Stage 4 staging payload.

The staging payload is intentionally machine-shaped. This script creates
spreadsheet-friendly review files so the content owner can inspect each
question's topic, difficulty, prompt, options, correct answer, explanation,
source context, objectives, and any linked visual assets before approval.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "supabase" / "imports" / "unit1_stage4_staging_payload.json"
DEFAULT_REPORT = REPO_ROOT / "docs" / "unit1-teacher-question-review.csv"
DEFAULT_SUMMARY_CSV = REPO_ROOT / "docs" / "unit1-teacher-question-review-summary.csv"
DEFAULT_SUMMARY_JSON = REPO_ROOT / "docs" / "unit1-teacher-question-review-summary.json"


DETAIL_COLUMNS = [
    "teacher_decision",
    "teacher_comment",
    "row_number",
    "question_external_id",
    "topic_slug",
    "topic_title",
    "difficulty",
    "format",
    "adaptive_tier",
    "review_priority",
    "review_flags",
    "staging_status",
    "source_kind",
    "source_file_name",
    "source_locator",
    "objective_codes",
    "question_family_code",
    "selection_weight",
    "asset_count",
    "assets",
    "stem",
    "options_or_prompt",
    "correct_answer",
    "markscheme_points",
    "explanation",
    "teacher_notes",
    "tags",
    "max_marks",
    "dedupe_fingerprint",
]


SUMMARY_COLUMNS = [
    "topic_slug",
    "topic_title",
    "total_questions",
    "easy",
    "medium",
    "expert",
    "mcq",
    "match_table",
    "fill_gap",
    "true_false",
    "short_text",
    "drag_drop",
    "questions_with_assets",
    "asset_count",
    "high_priority",
    "medium_priority",
    "low_priority",
    "transformed_exam_item",
    "practice_question_needs_source_normalization",
    "supplementary_derived_item",
]


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    return " ".join(str(value).split())


def join_list(values: list[Any], sep: str = " | ") -> str:
    return sep.join(clean_cell(value) for value in values if clean_cell(value))


def option_label_lookup(options: Any) -> dict[str, str]:
    if isinstance(options, list):
        lookup: dict[str, str] = {}
        for option in options:
            if not isinstance(option, dict):
                continue
            key = clean_cell(option.get("key"))
            text = clean_cell(option.get("text"))
            if key:
                lookup[key] = text
            if text:
                lookup[text] = text
        return lookup

    if isinstance(options, dict):
        lookup = {}
        for choice in options.get("choices", []):
            if not isinstance(choice, dict):
                continue
            choice_id = clean_cell(choice.get("id"))
            key = clean_cell(choice.get("key"))
            label = clean_cell(choice.get("label"))
            for identifier in (choice_id, key, label):
                if identifier:
                    lookup[identifier] = label
        for row in options.get("rows", []):
            if not isinstance(row, dict):
                continue
            row_id = clean_cell(row.get("id"))
            label = clean_cell(row.get("label"))
            if row_id:
                lookup[row_id] = label
        return lookup

    return {}


def options_preview(options: Any) -> str:
    if isinstance(options, list):
        parts = []
        for option in options:
            if isinstance(option, dict):
                key = clean_cell(option.get("key"))
                text = clean_cell(option.get("text"))
                parts.append(f"{key}. {text}" if key else text)
            else:
                parts.append(clean_cell(option))
        return join_list(parts)

    if isinstance(options, dict):
        if isinstance(options.get("items"), list):
            return "Order items: " + join_list(options["items"])

        rows = []
        for row in options.get("rows", []):
            if isinstance(row, dict):
                rows.append(clean_cell(row.get("label")))

        choices = []
        for choice in options.get("choices", []):
            if isinstance(choice, dict):
                key = clean_cell(choice.get("key"))
                label = clean_cell(choice.get("label"))
                choices.append(f"{key}. {label}" if key else label)

        sections = []
        if rows:
            sections.append("Rows: " + join_list(rows))
        if choices:
            sections.append("Choices: " + join_list(choices))
        return " || ".join(sections)

    return clean_cell(options)


def answer_preview(question: dict[str, Any]) -> str:
    answer = question.get("correct_answer_json") or {}
    options = question.get("options_json")
    lookup = option_label_lookup(options)

    if isinstance(answer.get("pairs"), list):
        pair_previews = []
        for pair in answer["pairs"]:
            if not isinstance(pair, dict):
                continue
            row = lookup.get(clean_cell(pair.get("row_id")), clean_cell(pair.get("row_id")))
            choice = lookup.get(clean_cell(pair.get("choice_id")), clean_cell(pair.get("choice_id")))
            pair_previews.append(f"{row} -> {choice}")
        if pair_previews:
            return join_list(pair_previews)

    if isinstance(answer.get("gaps"), list):
        gap_previews = []
        for gap in answer["gaps"]:
            if not isinstance(gap, dict):
                continue
            accepted = gap.get("accepted_texts") or []
            if accepted:
                gap_previews.append(f"{clean_cell(gap.get('id'))}: {join_list(accepted, ' / ')}")
        if gap_previews:
            return join_list(gap_previews)

    if isinstance(answer.get("order"), list):
        return "Correct order: " + join_list(answer["order"], " -> ")

    raw = clean_cell(answer.get("raw"))
    if raw and raw in lookup:
        return f"{raw}. {lookup[raw]}"
    return raw


def asset_preview(assets: list[dict[str, Any]]) -> str:
    parts = []
    for asset in sorted(assets, key=lambda item: item.get("display_order", 0)):
        kind = clean_cell(asset.get("asset_kind"))
        path = clean_cell(asset.get("storage_path"))
        caption = clean_cell(asset.get("caption"))
        alt = clean_cell(asset.get("alt_text"))
        label = caption or alt
        parts.append(f"{kind}: {path}" + (f" ({label})" if label else ""))
    return join_list(parts)


def review_flags(question: dict[str, Any]) -> list[str]:
    metadata = question.get("metadata_json") or {}
    flags = metadata.get("review_flags") or []
    return [clean_cell(flag) for flag in flags if clean_cell(flag)]


def build_detail_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    assets_by_question: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for asset in payload.get("staged_question_assets", []):
        assets_by_question[asset["question_external_id"]].append(asset)

    rows: list[dict[str, Any]] = []
    questions = sorted(
        payload.get("staged_questions", []),
        key=lambda q: (
            clean_cell(q.get("topic_slug")),
            {"easy": 1, "medium": 2, "expert": 3}.get(clean_cell(q.get("difficulty")), 99),
            int(q.get("row_number") or 0),
            clean_cell(q.get("question_external_id")),
        ),
    )

    for question in questions:
        metadata = question.get("metadata_json") or {}
        qid = question["question_external_id"]
        flags = review_flags(question)
        assets = assets_by_question.get(qid, [])
        row = {
            "teacher_decision": "",
            "teacher_comment": "",
            "row_number": question.get("row_number"),
            "question_external_id": qid,
            "topic_slug": question.get("topic_slug"),
            "topic_title": question.get("topic_title"),
            "difficulty": question.get("difficulty"),
            "format": question.get("format"),
            "adaptive_tier": question.get("adaptive_tier"),
            "review_priority": metadata.get("review_priority"),
            "review_flags": join_list(flags),
            "staging_status": question.get("staging_status"),
            "source_kind": question.get("source_kind"),
            "source_file_name": question.get("source_file_name"),
            "source_locator": question.get("source_locator"),
            "objective_codes": join_list(question.get("objective_codes_json") or []),
            "question_family_code": question.get("question_family_code"),
            "selection_weight": question.get("selection_weight"),
            "asset_count": len(assets),
            "assets": asset_preview(assets),
            "stem": question.get("stem"),
            "options_or_prompt": options_preview(question.get("options_json")),
            "correct_answer": answer_preview(question),
            "markscheme_points": join_list(question.get("markscheme_points_json") or []),
            "explanation": question.get("explanation"),
            "teacher_notes": question.get("teacher_notes"),
            "tags": join_list(question.get("tags_json") or []),
            "max_marks": question.get("max_marks"),
            "dedupe_fingerprint": question.get("dedupe_fingerprint"),
        }
        rows.append({column: clean_cell(row.get(column)) for column in DETAIL_COLUMNS})
    return rows


def build_summary_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    assets_by_question: dict[str, int] = Counter()
    for asset in payload.get("staged_question_assets", []):
        assets_by_question[asset["question_external_id"]] += 1

    topic_rows: dict[str, dict[str, Any]] = {}
    overall = {
        "total_questions": 0,
        "asset_count": len(payload.get("staged_question_assets", [])),
        "questions_with_assets": 0,
        "difficulty_counts": Counter(),
        "format_counts": Counter(),
        "priority_counts": Counter(),
        "flag_counts": Counter(),
        "staging_status_counts": Counter(),
    }

    for question in payload.get("staged_questions", []):
        topic_slug = clean_cell(question.get("topic_slug"))
        if topic_slug not in topic_rows:
            topic_rows[topic_slug] = {
                "topic_slug": topic_slug,
                "topic_title": clean_cell(question.get("topic_title")),
                "total_questions": 0,
                "easy": 0,
                "medium": 0,
                "expert": 0,
                "mcq": 0,
                "match_table": 0,
                "fill_gap": 0,
                "true_false": 0,
                "short_text": 0,
                "drag_drop": 0,
                "questions_with_assets": 0,
                "asset_count": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0,
                "transformed_exam_item": 0,
                "practice_question_needs_source_normalization": 0,
                "supplementary_derived_item": 0,
            }

        row = topic_rows[topic_slug]
        qid = question["question_external_id"]
        difficulty = clean_cell(question.get("difficulty"))
        format_name = clean_cell(question.get("format"))
        priority = clean_cell((question.get("metadata_json") or {}).get("review_priority"))
        flags = review_flags(question)
        asset_count = assets_by_question.get(qid, 0)

        row["total_questions"] += 1
        overall["total_questions"] += 1
        if difficulty in {"easy", "medium", "expert"}:
            row[difficulty] += 1
        if format_name in {"mcq", "match_table", "fill_gap", "true_false", "short_text", "drag_drop"}:
            row[format_name] += 1
        if priority in {"high", "medium", "low"}:
            row[f"{priority}_priority"] += 1
        if asset_count:
            row["questions_with_assets"] += 1
            overall["questions_with_assets"] += 1
        row["asset_count"] += asset_count

        for flag in flags:
            if flag in row:
                row[flag] += 1
            overall["flag_counts"][flag] += 1

        overall["difficulty_counts"][difficulty] += 1
        overall["format_counts"][format_name] += 1
        overall["priority_counts"][priority] += 1
        overall["staging_status_counts"][clean_cell(question.get("staging_status"))] += 1

    summary_rows = sorted(topic_rows.values(), key=lambda row: row["topic_slug"])
    summary_rows = [
        {column: clean_cell(row.get(column)) for column in SUMMARY_COLUMNS}
        for row in summary_rows
    ]
    serializable_overall = {
        "total_questions": overall["total_questions"],
        "asset_count": overall["asset_count"],
        "questions_with_assets": overall["questions_with_assets"],
        "difficulty_counts": dict(overall["difficulty_counts"]),
        "format_counts": dict(overall["format_counts"]),
        "priority_counts": dict(overall["priority_counts"]),
        "flag_counts": dict(overall["flag_counts"]),
        "staging_status_counts": dict(overall["staging_status_counts"]),
    }
    return summary_rows, serializable_overall


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY_CSV)
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_payload(args.input)
    detail_rows = build_detail_rows(payload)
    summary_rows, overall = build_summary_rows(payload)

    write_csv(args.report, DETAIL_COLUMNS, detail_rows)
    write_csv(args.summary_csv, SUMMARY_COLUMNS, summary_rows)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(
            {
                "source_payload": str(args.input),
                "detail_report": str(args.report),
                "summary_csv": str(args.summary_csv),
                "overall": overall,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(detail_rows)} question rows to {args.report}")
    print(f"Wrote {len(summary_rows)} topic summary rows to {args.summary_csv}")
    print(f"Wrote summary JSON to {args.summary_json}")


if __name__ == "__main__":
    main()
