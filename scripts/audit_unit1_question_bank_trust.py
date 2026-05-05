#!/usr/bin/env python3
"""Audit the Unit 1 live question bank for student-facing trust risks.

This is not a replacement for teacher source review. It is a mechanical safety
net for defects that can be detected consistently across the whole bank:
scaffold leakage, missing required visuals, brittle automarking, duplicate
wording, and weak/generic prompts.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "supabase/imports/unit1_stage5_approved_live_payload.json"
STRICT_VISUAL_REPORT = ROOT / "docs/stage-5-strict-visual-context-repair-2026-05-04.json"
CSV_OUT = ROOT / "docs/unit1-question-bank-trust-audit-2026-05-04.csv"
MD_OUT = ROOT / "docs/unit1-question-bank-trust-audit-2026-05-04.md"
JSON_OUT = ROOT / "docs/unit1-question-bank-trust-audit-2026-05-04.json"

SCAFFOLD_RE = re.compile(r"\bPairs:\s|→\s*\?", re.IGNORECASE)
GENERIC_STEM_RE = re.compile(r"^\s*(complete the sentence|complete the sentences)\s*$", re.IGNORECASE)
VISUAL_REQUIRED_RE = re.compile(
    r"\b("
    r"shown|shown above|shown below|refer to|sample view|diagram|chart of|bar chart|pie chart|line chart|"
    r"scatter graph|query that returns|criteria entered|criteria row|sort the data|sorted|relationship shown|"
    r"cell range|x-axis|y-axis|data series|VLOOKUP formula|complete the VLOOKUP|tbl[A-Z0-9]+|"
    r"cell\s+[A-Z]+\d+|cells\s+[A-Z]+\d+|"
    r"[A-Z]+\d+\s*:\s*[A-Z]+\d+"
    r")\b",
    re.IGNORECASE,
)
OPEN_ENDED_RE = re.compile(
    r"\b(state|give|name|list|identify)\s+(one|another|two|three)\s+"
    r"(advantage|disadvantage|benefit|limitation|impact|method|reason|example|feature|measure|use|source|task)",
    re.IGNORECASE,
)
MULTI_ITEM_RE = re.compile(r"\b(state|give|name|list)\s+(two|three|2|3|TWO|THREE)\b|\bdifferent\b", re.IGNORECASE)


def qid(question: dict[str, Any]) -> str:
    return question.get("question_external_id") or question.get("external_id") or ""


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def question_blob(question: dict[str, Any]) -> str:
    return "\n".join(
        [
            str(question.get("stem") or ""),
            json.dumps(question.get("content_blocks_json") or [], ensure_ascii=False),
            json.dumps(question.get("response_schema_json") or {}, ensure_ascii=False),
            json.dumps(question.get("autograde_rules_json") or {}, ensure_ascii=False),
        ]
    )


def load_effective_visual_links(payload: dict[str, Any]) -> dict[str, set[str]]:
    links: dict[str, set[str]] = defaultdict(set)
    for link in payload.get("question_asset_links", []):
        links[link.get("question_external_id", "")].add(link.get("asset_storage_path") or link.get("asset_external_id") or "")

    if STRICT_VISUAL_REPORT.exists():
        strict = json.loads(STRICT_VISUAL_REPORT.read_text(encoding="utf-8"))
        for link in strict.get("links", []):
            links[link.get("question_external_id", "")].add(link.get("asset_storage_path") or link.get("asset_external_id") or "")

    return links


def accepted_values_from_rules(rules: Any) -> list[str]:
    values: list[str] = []
    if not isinstance(rules, dict):
        return values

    if isinstance(rules.get("accepted"), list):
        values.extend(str(item) for item in rules["accepted"])

    for gap in rules.get("gaps") or []:
        if not isinstance(gap, dict):
            continue
        if isinstance(gap.get("accepted"), list):
            values.extend(str(item) for item in gap["accepted"])
        for group in gap.get("accepted_groups") or []:
            if isinstance(group, dict):
                values.append(str(group.get("canonical") or ""))
                values.extend(str(item) for item in group.get("accepted") or [])
    return [value for value in values if value]


def has_unnumbered_alias(group_values: list[str], numbered_value: str) -> bool:
    cleaned = re.sub(r"^\(\d+\)\s*", "", numbered_value).strip()
    return bool(cleaned) and norm(cleaned) in {norm(value) for value in group_values}


def slash_alias_risk(values: list[str]) -> bool:
    slash_values = [value for value in values if "/" in value and not value.lower().startswith(("http://", "https://"))]
    if not slash_values:
        return False
    normalized_values = {norm(value) for value in values}
    for value in slash_values:
        pieces = [piece.strip(" ()") for piece in re.split(r"/", value) if piece.strip(" ()")]
        if len(pieces) >= 2 and not any(norm(piece) in normalized_values for piece in pieces):
            return True
    return False


def add_issue(issues: list[dict[str, Any]], question: dict[str, Any], severity: str, category: str, detail: str) -> None:
    issues.append(
        {
            "severity": severity,
            "category": category,
            "question_external_id": qid(question),
            "topic_slug": question.get("topic_slug", ""),
            "difficulty": question.get("difficulty", ""),
            "format": question.get("format", ""),
            "source_type": question.get("source_type", ""),
            "source_ref": question.get("source_ref", ""),
            "stem": question.get("stem", ""),
            "detail": detail,
        }
    )


def main() -> None:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    questions = payload["live_questions"]
    visual_links = load_effective_visual_links(payload)
    issues: list[dict[str, Any]] = []

    stems: dict[str, list[str]] = defaultdict(list)

    for question in questions:
        question_id = qid(question)
        stem = str(question.get("stem") or "")
        blob = question_blob(question)
        stems[norm(stem)].append(question_id)

        if SCAFFOLD_RE.search(blob):
            add_issue(issues, question, "blocker", "student_scaffold_leak", "Student-facing text still contains generator scaffold such as Pairs: or -> ?.")

        if GENERIC_STEM_RE.match(stem):
            add_issue(issues, question, "high", "generic_prompt", "Prompt is too generic to be meaningful without relying on hidden/generated context.")

        requires_visual = (
            question.get("source_type") == "adapted_exam"
            and question.get("topic_slug") in {"spreadsheet-applications", "database-applications"}
            and VISUAL_REQUIRED_RE.search(stem)
        )
        if requires_visual and not visual_links.get(question_id):
            add_issue(issues, question, "blocker", "missing_visual_context", "Question wording depends on a table/query/chart/cell range but no effective visual link is recorded.")

        rules = question.get("autograde_rules_json") or {}
        accepted = accepted_values_from_rules(rules)
        if question.get("format") == "fill_gap":
            numbered = [value for value in accepted if re.match(r"^\(\d+\)\s+", value)]
            if numbered:
                for value in numbered:
                    if not has_unnumbered_alias(accepted, value):
                        add_issue(issues, question, "blocker", "numbered_answer_without_alias", f"Accepted answer {value!r} lacks a plain student-typed alias.")
                        break
            if MULTI_ITEM_RE.search(stem) and not bool(rules.get("require_distinct")):
                add_issue(issues, question, "high", "missing_distinct_multi_answer_rule", "Question asks for multiple items but repeat answers are not explicitly blocked.")
            if slash_alias_risk(accepted):
                add_issue(issues, question, "high", "slash_answer_alias_risk", "Slash-style mark-scheme answer may not accept the individual student-typed alternatives.")

        if question.get("format") == "short_text":
            if OPEN_ENDED_RE.search(stem):
                add_issue(issues, question, "high", "open_ended_exact_marking", "Open-ended short-answer wording is marked by exact accepted terms; this is brittle without AI/human marking.")
            elif any(" " in value.strip() for value in accepted) and (rules.get("match_mode") == "exact"):
                add_issue(issues, question, "medium", "phrase_exact_marking", "Multi-word short answer uses exact phrase matching; acceptable for key terms, but worth checking aliases.")

    for normalized_stem, ids in stems.items():
        if normalized_stem and len(ids) > 1:
            # One issue row is enough per duplicate cluster.
            question = next(q for q in questions if qid(q) == ids[0])
            add_issue(issues, question, "medium", "duplicate_stem", f"Same stem appears {len(ids)} times: {', '.join(ids[:8])}.")

    severity_rank = {"blocker": 0, "high": 1, "medium": 2, "low": 3}
    issues.sort(key=lambda row: (severity_rank.get(row["severity"], 99), row["topic_slug"], row["question_external_id"], row["category"]))

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "severity",
                "category",
                "question_external_id",
                "topic_slug",
                "difficulty",
                "format",
                "source_type",
                "source_ref",
                "detail",
                "stem",
            ],
        )
        writer.writeheader()
        writer.writerows(issues)

    counts = Counter(row["severity"] for row in issues)
    by_category = Counter(row["category"] for row in issues)
    by_topic = Counter(row["topic_slug"] for row in issues)
    summary = {
        "question_count": len(questions),
        "issue_count": len(issues),
        "severity_counts": dict(counts),
        "category_counts": dict(by_category),
        "topic_counts": dict(by_topic),
        "effective_visual_link_questions": len(visual_links),
        "csv": str(CSV_OUT.relative_to(ROOT)),
    }
    JSON_OUT.write_text(json.dumps({"summary": summary, "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Unit 1 Question Bank Trust Audit",
        "",
        "Date: 2026-05-04",
        "",
        "This mechanical audit checks the live payload for student-facing reliability risks. It does not claim human-level source validation; it identifies defects that should be fixed or deliberately accepted before publication.",
        "",
        "## Summary",
        "",
        f"- Questions checked: `{len(questions)}`",
        f"- Issues found: `{len(issues)}`",
        f"- Blockers: `{counts.get('blocker', 0)}`",
        f"- High: `{counts.get('high', 0)}`",
        f"- Medium: `{counts.get('medium', 0)}`",
        f"- Effective visual-link question count: `{len(visual_links)}`",
        "",
        "## Category Counts",
        "",
    ]
    for category, count in by_category.most_common():
        lines.append(f"- `{category}`: `{count}`")
    lines.extend(["", "## Highest Priority Issues", ""])
    for issue in issues[:80]:
        lines.append(
            f"- `{issue['severity']}` `{issue['category']}` `{issue['question_external_id']}`: {issue['detail']}"
        )
    lines.extend(["", f"Full CSV: `{CSV_OUT.relative_to(ROOT)}`", ""])
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
