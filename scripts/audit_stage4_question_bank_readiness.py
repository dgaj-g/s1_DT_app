#!/usr/bin/env python3
"""Audit Stage 4 question-bank readiness for review and runtime use."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "supabase" / "imports" / "unit1_stage4_staging_payload.json"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "unit1-question-bank-readiness-audit-2026-05-04.md"
DEFAULT_JSON = REPO_ROOT / "docs" / "unit1-question-bank-readiness-audit-2026-05-04.json"

DIFFICULTIES = ["easy", "medium", "expert"]
FORMATS = ["mcq", "match_table", "fill_gap", "true_false", "short_text", "drag_drop"]
MIN_SESSION_QUESTIONS = 10
DEPTH_TARGET_PER_DIFFICULTY = 30


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()


def review_flags(question: dict[str, Any]) -> list[str]:
    metadata = question.get("metadata_json") or {}
    flags = metadata.get("review_flags") or []
    return [clean(flag) for flag in flags if clean(flag)]


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(clean(cell).replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def audit(payload: dict[str, Any]) -> dict[str, Any]:
    questions = payload.get("staged_questions", [])
    assets = payload.get("staged_question_assets", [])
    assets_by_question = Counter(asset["question_external_id"] for asset in assets)

    topic_titles: dict[str, str] = {}
    by_topic: dict[str, dict[str, Any]] = {}
    family_by_topic_difficulty: dict[tuple[str, str], set[str]] = defaultdict(set)
    question_by_topic_difficulty: Counter[tuple[str, str]] = Counter()
    flag_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    format_counts: Counter[str] = Counter()
    difficulty_counts: Counter[str] = Counter()
    priority_counts: Counter[str] = Counter()

    for question in questions:
        topic_slug = clean(question.get("topic_slug"))
        topic_title = clean(question.get("topic_title"))
        difficulty = clean(question.get("difficulty"))
        format_name = clean(question.get("format"))
        family = clean(question.get("question_family_code")) or clean(question.get("question_external_id"))
        priority = clean((question.get("metadata_json") or {}).get("review_priority"))
        status = clean(question.get("staging_status"))
        qid = question["question_external_id"]

        topic_titles[topic_slug] = topic_title
        if topic_slug not in by_topic:
            by_topic[topic_slug] = {
                "topic_slug": topic_slug,
                "topic_title": topic_title,
                "total": 0,
                "difficulty_counts": Counter(),
                "format_counts": Counter(),
                "priority_counts": Counter(),
                "flag_counts": Counter(),
                "questions_with_assets": 0,
                "asset_count": 0,
            }

        topic = by_topic[topic_slug]
        topic["total"] += 1
        topic["difficulty_counts"][difficulty] += 1
        topic["format_counts"][format_name] += 1
        topic["priority_counts"][priority] += 1
        if assets_by_question.get(qid, 0):
            topic["questions_with_assets"] += 1
            topic["asset_count"] += assets_by_question[qid]

        question_by_topic_difficulty[(topic_slug, difficulty)] += 1
        family_by_topic_difficulty[(topic_slug, difficulty)].add(family)

        difficulty_counts[difficulty] += 1
        format_counts[format_name] += 1
        priority_counts[priority] += 1
        status_counts[status] += 1

        for flag in review_flags(question):
            flag_counts[flag] += 1
            topic["flag_counts"][flag] += 1

    difficulty_readiness = []
    for topic_slug in sorted(topic_titles):
        for difficulty in DIFFICULTIES:
            question_count = question_by_topic_difficulty[(topic_slug, difficulty)]
            family_count = len(family_by_topic_difficulty[(topic_slug, difficulty)])
            if question_count < MIN_SESSION_QUESTIONS:
                status = "blocking_for_level"
                note = "Fewer than 10 questions means a full session cannot be reliably offered."
            elif family_count < MIN_SESSION_QUESTIONS:
                status = "family_depth_risk"
                note = "At least 10 questions exist, but fewer than 10 families risks repeated question styles."
            elif question_count < DEPTH_TARGET_PER_DIFFICULTY:
                status = "thin_depth"
                note = "Usable for a session, but below the 30-question depth target for repeated revision."
            else:
                status = "healthy"
                note = "Meets the depth target for this difficulty."

            difficulty_readiness.append(
                {
                    "topic_slug": topic_slug,
                    "topic_title": topic_titles[topic_slug],
                    "difficulty": difficulty,
                    "question_count": question_count,
                    "family_count": family_count,
                    "status": status,
                    "note": note,
                }
            )

    return {
        "generated_on": date.today().isoformat(),
        "total_questions": len(questions),
        "asset_count": len(assets),
        "questions_with_assets": len(assets_by_question),
        "difficulty_counts": dict(difficulty_counts),
        "format_counts": dict(format_counts),
        "priority_counts": dict(priority_counts),
        "status_counts": dict(status_counts),
        "flag_counts": dict(flag_counts),
        "topic_summaries": [
            {
                "topic_slug": topic["topic_slug"],
                "topic_title": topic["topic_title"],
                "total": topic["total"],
                "difficulty_counts": dict(topic["difficulty_counts"]),
                "format_counts": dict(topic["format_counts"]),
                "priority_counts": dict(topic["priority_counts"]),
                "flag_counts": dict(topic["flag_counts"]),
                "questions_with_assets": topic["questions_with_assets"],
                "asset_count": topic["asset_count"],
            }
            for topic in sorted(by_topic.values(), key=lambda item: item["topic_slug"])
        ],
        "difficulty_readiness": difficulty_readiness,
    }


def render_report(result: dict[str, Any], input_path: Path) -> str:
    readiness_counts = Counter(item["status"] for item in result["difficulty_readiness"])
    blocking = [item for item in result["difficulty_readiness"] if item["status"] == "blocking_for_level"]
    thin = [
        item
        for item in result["difficulty_readiness"]
        if item["status"] in {"family_depth_risk", "thin_depth"}
    ]

    topic_rows = []
    for topic in result["topic_summaries"]:
        difficulty = topic["difficulty_counts"]
        flags = topic["flag_counts"]
        topic_rows.append(
            [
                topic["topic_title"],
                topic["total"],
                difficulty.get("easy", 0),
                difficulty.get("medium", 0),
                difficulty.get("expert", 0),
                topic["questions_with_assets"],
                flags.get("transformed_exam_item", 0),
                flags.get("practice_question_needs_source_normalization", 0),
            ]
        )

    level_rows = [
        [
            item["topic_title"],
            item["difficulty"],
            item["question_count"],
            item["family_count"],
            item["status"],
        ]
        for item in result["difficulty_readiness"]
        if item["status"] != "healthy"
    ]

    lines = [
        "# Unit 1 Question Bank Readiness Audit",
        "",
        f"- Generated: {result['generated_on']}",
        f"- Source payload: `{input_path}`",
        f"- Total staged questions: `{result['total_questions']}`",
        f"- Linked visual assets: `{result['asset_count']}` across `{result['questions_with_assets']}` questions",
        "",
        "## Current Position",
        "",
        "The staged Unit 1 bank is technically structured and reviewable, but it should not be treated as fully student-ready yet.",
        "",
        "- All staged questions are currently `ready_for_review`, not approved/live.",
        "- A dry-run runtime promotion has already shown that the bank can technically convert into runtime questions.",
        "- The content still needs teacher approval, especially transformed past-paper items and practice-bank items whose source labels were normalized from the source pack.",
        "- Difficulty depth is uneven. This is the main pedagogical blocker for a genuinely adaptive app.",
        "",
        "## Overall Counts",
        "",
        table(
            ["Measure", "Value"],
            [
                ["Questions", result["total_questions"]],
                ["Visual assets", result["asset_count"]],
                ["Questions with visual assets", result["questions_with_assets"]],
                ["Status counts", json.dumps(result["status_counts"], ensure_ascii=False)],
                ["Difficulty counts", json.dumps(result["difficulty_counts"], ensure_ascii=False)],
                ["Format counts", json.dumps(result["format_counts"], ensure_ascii=False)],
                ["Review priority counts", json.dumps(result["priority_counts"], ensure_ascii=False)],
                ["Review flag counts", json.dumps(result["flag_counts"], ensure_ascii=False)],
            ],
        ),
        "",
        "## Topic Coverage",
        "",
        table(
            [
                "Topic",
                "Total",
                "Easy",
                "Medium",
                "Expert",
                "Asset Qs",
                "Transformed Exam",
                "Practice Needs Source Normalisation",
            ],
            topic_rows,
        ),
        "",
        "## Difficulty-Depth Findings",
        "",
        f"- Healthy topic/difficulty buckets: `{readiness_counts.get('healthy', 0)}`",
        f"- Thin-depth buckets: `{readiness_counts.get('thin_depth', 0)}`",
        f"- Family-depth risk buckets: `{readiness_counts.get('family_depth_risk', 0)}`",
        f"- Blocking buckets with fewer than 10 questions: `{readiness_counts.get('blocking_for_level', 0)}`",
        "",
        "A topic/difficulty bucket needs at least 10 questions to support one 10-question session. The practical depth target is 30+ questions per topic/difficulty so students can repeat sessions without seeing the same material too often.",
        "",
    ]

    if level_rows:
        lines.extend(
            [
                table(["Topic", "Difficulty", "Questions", "Families", "Status"], level_rows),
                "",
            ]
        )

    if blocking:
        recommended_step = [
            "Apply and test the weighted family-aware picker migration, then add a content balancing pass to create or promote enough questions for blocking topic/difficulty buckets.",
            "",
            "The picker improves session variety, but it cannot invent depth. Buckets below 10 questions still need more approved questions before they can reliably offer full sessions.",
        ]
    else:
        recommended_step = [
            "Apply and test the weighted family-aware picker migration, then move into teacher review/approval using the generated review CSV.",
            "",
            "There are no longer any topic/difficulty buckets below 10 questions. The remaining content-depth issue is family variety in thinner buckets, especially expert buckets, so a later polish pass should add more distinct scenario families where time allows.",
        ]

    lines.extend(
        [
            "## Infrastructure Findings",
            "",
            "- `question_family_code` and `selection_weight` now exist in the staging/live payload design.",
            "- The repo includes a weighted family-aware picker migration: `supabase/migrations/20260504114500_weighted_family_session_picker.sql`.",
            "- That migration must still be applied to Supabase before the live app benefits from family-aware selection.",
            "- The picker must continue to prevent duplicate questions in a session.",
            "- The picker should prevent duplicate families in a session where enough family depth exists, then relax that rule only when the approved bucket is thin.",
            "- Expert sessions should not simply mean harder wording. They need scenario, source, diagram/table, or multi-step reasoning depth.",
            "",
            "## Recommended Next Build Step",
            "",
            *recommended_step,
        ]
    )

    if blocking:
        lines.extend(
            [
                "",
                "## Blocking Buckets",
                "",
                "These topic/difficulty combinations cannot yet support a full 10-question session without fallback or repeated material:",
                "",
            ]
        )
        lines.extend(
            f"- {item['topic_title']} / {item['difficulty']}: {item['question_count']} questions, {item['family_count']} families"
            for item in blocking
        )

    if thin:
        lines.extend(
            [
                "",
                "## Thin Buckets",
                "",
                "These buckets can potentially run a session but need more depth for strong adaptive revision:",
                "",
            ]
        )
        lines.extend(
            f"- {item['topic_title']} / {item['difficulty']}: {item['question_count']} questions, {item['family_count']} families, {item['status']}"
            for item in thin
        )

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_payload(args.input)
    result = audit(payload)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(result, args.input), encoding="utf-8")
    args.json_output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote readiness audit to {args.output}")
    print(f"Wrote readiness audit JSON to {args.json_output}")


if __name__ == "__main__":
    main()
