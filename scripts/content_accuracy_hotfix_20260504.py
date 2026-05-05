#!/usr/bin/env python3
"""Apply the first content-accuracy hotfix pass to the Stage 5 Unit 1 payloads.

This pass fixes mechanical defects discovered during teacher testing:
- remove imported "Pairs: ... -> ?" helper text from public stems/content blocks;
- accept student answers without numbered prefixes such as "(1) B12";
- widen spreadsheet chart-type accepted answers to include short forms;
- clarify a hardware clock-speed stem and an HDD-disadvantage option.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAYLOADS = [
    ROOT / "supabase/imports/unit1_stage5_approved_live_payload.json",
]
MIGRATION = ROOT / "supabase/migrations/20260504172000_content_accuracy_hotfixes.sql"
REPORT = ROOT / "docs/content-accuracy-hotfix-2026-05-04.json"

NUM_PREFIX_RE = re.compile(r"^\s*\(\d+\)\s*(.+?)\s*$")
PAIRS_RE = re.compile(r"(?:^|\s+)Pairs:\s.*$", re.IGNORECASE | re.DOTALL)


def clean_pairs_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    return PAIRS_RE.sub("", value).strip()


def strip_number_prefix(value: str) -> str | None:
    match = NUM_PREFIX_RE.match(value)
    if not match:
        return None
    return match.group(1).strip()


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


def expand_numbered_accepted(question: dict[str, Any]) -> bool:
    changed = False

    correct = question.get("correct_answer_json")
    if isinstance(correct, dict) and isinstance(correct.get("accepted"), list):
        next_accepted = []
        for answer_group in correct["accepted"]:
            if isinstance(answer_group, list):
                additions = []
                for item in answer_group:
                    if isinstance(item, str):
                        stripped = strip_number_prefix(item)
                        if stripped:
                            additions.append(stripped)
                next_group = unique([*answer_group, *additions])
                changed = changed or next_group != answer_group
                next_accepted.append(next_group)
            else:
                next_accepted.append(answer_group)
        correct["accepted"] = next_accepted

    rules = question.get("autograde_rules_json")
    if isinstance(rules, dict) and rules.get("kind") == "fill_gap":
        for gap in rules.get("gaps", []):
            if not isinstance(gap, dict):
                continue
            if isinstance(gap.get("accepted"), list):
                additions = []
                for item in gap["accepted"]:
                    if isinstance(item, str):
                        stripped = strip_number_prefix(item)
                        if stripped:
                            additions.append(stripped)
                next_accepted = unique([*gap["accepted"], *additions])
                changed = changed or next_accepted != gap["accepted"]
                gap["accepted"] = next_accepted
            for group in gap.get("accepted_groups", []):
                if not isinstance(group, dict) or not isinstance(group.get("accepted"), list):
                    continue
                additions = []
                for item in group["accepted"]:
                    if isinstance(item, str):
                        stripped = strip_number_prefix(item)
                        if stripped:
                            additions.append(stripped)
                next_accepted = unique([*group["accepted"], *additions])
                changed = changed or next_accepted != group["accepted"]
                group["accepted"] = next_accepted
                if isinstance(group.get("canonical"), str):
                    stripped = strip_number_prefix(group["canonical"])
                    if stripped:
                        group["canonical"] = stripped
                        changed = True
    return changed


def set_text_blocks(question: dict[str, Any], old_text: str, new_text: str) -> None:
    blocks = question.get("content_blocks_json")
    if isinstance(blocks, list):
        for block in blocks:
            if isinstance(block, dict) and block.get("text") == old_text:
                block["text"] = new_text


def patch_specific_question(question: dict[str, Any]) -> bool:
    qid = question.get("question_external_id")
    changed = False

    if qid == "spreadsheet-applications.past_paper.topics_03_04.q034":
        question["correct_answer_json"] = {"accepted": [["B12"], ["3"]]}
        question["markscheme_points_json"] = ["B12", "3"]
        question["explanation"] = (
            "An accepted answer is B12 for answer 1 and 3 for answer 2. "
            "This question checks whether you can use built-in functions and lookup formulas appropriately. "
            "It also checks whether you can recognise cells, rows, columns, worksheets and cell references."
        )
        question["autograde_rules_json"] = {
            "kind": "fill_gap",
            "gaps": [
                {
                    "id": "gap1",
                    "normalization": "phrase",
                    "match_mode": "exact",
                    "accepted_groups": [{"canonical": "B12", "accepted": ["B12"]}],
                },
                {
                    "id": "gap2",
                    "normalization": "phrase",
                    "match_mode": "exact",
                    "accepted_groups": [{"canonical": "3", "accepted": ["3"]}],
                },
            ],
            "require_all": True,
            "require_distinct": False,
        }
        changed = True

    if qid == "spreadsheet-applications.practice_bank.topic_04_spreadsheet.q040":
        accepted_groups = [
            {"canonical": "Bar Chart", "accepted": ["Bar Chart", "Bar"]},
            {"canonical": "Column Chart", "accepted": ["Column Chart", "Column"]},
            {"canonical": "Line Chart", "accepted": ["Line Chart", "Line"]},
            {"canonical": "Pie Chart", "accepted": ["Pie Chart", "Pie"]},
            {"canonical": "Scatter Graph", "accepted": ["Scatter Graph", "Scatter", "Scatter Chart", "Scatter Plot"]},
        ]
        any_three = [g["canonical"] for g in accepted_groups]
        question["correct_answer_json"] = {"accepted": [any_three, any_three, any_three]}
        question["markscheme_points_json"] = any_three
        question["explanation"] = (
            "Accepted chart types include bar, column, line, pie and scatter charts/graphs. "
            "This question checks whether you can choose and interpret spreadsheet charts and graphs."
        )
        question["autograde_rules_json"] = {
            "kind": "fill_gap",
            "gaps": [
                {
                    "id": f"gap{i}",
                    "normalization": "phrase",
                    "match_mode": "exact",
                    "accepted_groups": copy.deepcopy(accepted_groups),
                }
                for i in range(1, 4)
            ],
            "require_all": True,
            "require_distinct": True,
        }
        changed = True

    if qid == "computer-hardware.practice_bank.topic_05_06_hardware_networks.q030":
        old = "Can crash and damage the surface"
        new = "A head crash can damage the disk surface"
        choices = question.get("options_json", {}).get("choices")
        if isinstance(choices, list):
            question["options_json"]["choices"] = [new if choice == old else choice for choice in choices]
        schema_choices = question.get("response_schema_json", {}).get("choices")
        if isinstance(schema_choices, list):
            for choice in schema_choices:
                if isinstance(choice, dict) and choice.get("label") == old:
                    choice["label"] = new
        question["correct_answer_json"] = {"choice": new}
        question["explanation"] = (
            "The correct option is: A head crash can damage the disk surface. "
            "The hardware fact file states that an HDD can crash and that regular crashes damage the surface. "
            "This question checks whether you can compare storage devices and media such as SSDs and hard drives."
        )
        changed = True

    if qid == "computer-hardware.practice_bank.topic_05_06_hardware_networks.q009":
        old = question["stem"]
        new = "A typical desktop computer runs at approximately 3 billion cycles per second. This is equal to:"
        question["stem"] = new
        set_text_blocks(question, old, new)
        changed = True

    return changed


def patch_payload(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(path.read_text())
    question_key = "live_questions" if "live_questions" in payload else "staged_questions"
    changed_questions: list[dict[str, Any]] = []

    for question in payload[question_key]:
        before = json.dumps(question, sort_keys=True, ensure_ascii=False)

        question["stem"] = clean_pairs_text(question.get("stem", ""))
        blocks = question.get("content_blocks_json")
        if isinstance(blocks, list):
            next_blocks = []
            for block in blocks:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    block["text"] = clean_pairs_text(block["text"])
                    if not block["text"]:
                        continue
                next_blocks.append(block)
            question["content_blocks_json"] = next_blocks

        expand_numbered_accepted(question)
        patch_specific_question(question)

        after = json.dumps(question, sort_keys=True, ensure_ascii=False)
        if before != after:
            changed_questions.append(question)

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return payload, changed_questions


def sql_literal_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("'", "''")


def write_migration(changed_questions: list[dict[str, Any]]) -> None:
    rows = [
        {
            "external_id": q["question_external_id"],
            "stem": q["stem"],
            "options_json": q.get("options_json", {}),
            "correct_answer_json": q.get("correct_answer_json", {}),
            "markscheme_points_json": q.get("markscheme_points_json", []),
            "explanation": q.get("explanation", ""),
            "content_blocks_json": q.get("content_blocks_json", []),
            "response_schema_json": q.get("response_schema_json", {}),
            "autograde_rules_json": q.get("autograde_rules_json", {}),
        }
        for q in changed_questions
    ]
    rows_json = sql_literal_json(rows)
    MIGRATION.write_text(
        "-- Content-accuracy hotfix pass after teacher verification on 2026-05-04.\n"
        "-- Fixes public helper text in match-table stems, brittle numbered fill-gap answers,\n"
        "-- spreadsheet chart short answers, HDD wording, and clock-speed wording.\n"
        "\n"
        "begin;\n"
        "\n"
        "with patch_payload as (\n"
        f"  select '{rows_json}'::jsonb as data\n"
        "),\n"
        "patch_rows as (\n"
        "  select *\n"
        "  from patch_payload,\n"
        "  jsonb_to_recordset(patch_payload.data) as row(\n"
        "    external_id text,\n"
        "    stem text,\n"
        "    options_json jsonb,\n"
        "    correct_answer_json jsonb,\n"
        "    markscheme_points_json jsonb,\n"
        "    explanation text,\n"
        "    content_blocks_json jsonb,\n"
        "    response_schema_json jsonb,\n"
        "    autograde_rules_json jsonb\n"
        "  )\n"
        ")\n"
        "update public.questions q\n"
        "set stem = p.stem,\n"
        "    options_json = p.options_json,\n"
        "    correct_answer_json = p.correct_answer_json,\n"
        "    markscheme_points_json = p.markscheme_points_json,\n"
        "    explanation = p.explanation,\n"
        "    content_blocks_json = p.content_blocks_json,\n"
        "    response_schema_json = p.response_schema_json,\n"
        "    autograde_rules_json = p.autograde_rules_json,\n"
        "    teacher_notes = concat_ws(' | ', nullif(q.teacher_notes, ''), 'Content accuracy hotfix 2026-05-04: removed public Pairs helper text where present, widened fill-gap accepted answers, and corrected tested wording defects.')\n"
        "from patch_rows p\n"
        "where q.external_id = p.external_id;\n"
        "\n"
        "do $$\n"
        "declare\n"
        "  remaining_pairs integer;\n"
        "  vlookup_accepts_b12 boolean;\n"
        "  chart_accepts_short_forms boolean;\n"
        "  clock_wording_ok boolean;\n"
        "begin\n"
        "  select count(*) into remaining_pairs\n"
        "  from public.questions\n"
        "  where is_active = true\n"
        "    and stem ilike '%Pairs:%';\n"
        "\n"
        "  if remaining_pairs <> 0 then\n"
        "    raise exception 'Content hotfix failed: % active questions still contain public Pairs helper text', remaining_pairs;\n"
        "  end if;\n"
        "\n"
        "  select public.answer_text_match_group(\n"
        "    'b12',\n"
        "    autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups',\n"
        "    'phrase',\n"
        "    'exact'\n"
        "  ) is not null into vlookup_accepts_b12\n"
        "  from public.questions\n"
        "  where external_id = 'spreadsheet-applications.past_paper.topics_03_04.q034';\n"
        "\n"
        "  if not coalesce(vlookup_accepts_b12, false) then\n"
        "    raise exception 'Content hotfix failed: VLOOKUP answer b12 is not accepted';\n"
        "  end if;\n"
        "\n"
        "  select public.answer_text_match_group(\n"
        "    'column',\n"
        "    autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups',\n"
        "    'phrase',\n"
        "    'exact'\n"
        "  ) is not null\n"
        "  and public.answer_text_match_group(\n"
        "    'bar',\n"
        "    autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups',\n"
        "    'phrase',\n"
        "    'exact'\n"
        "  ) is not null\n"
        "  and public.answer_text_match_group(\n"
        "    'pie',\n"
        "    autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups',\n"
        "    'phrase',\n"
        "    'exact'\n"
        "  ) is not null into chart_accepts_short_forms\n"
        "  from public.questions\n"
        "  where external_id = 'spreadsheet-applications.practice_bank.topic_04_spreadsheet.q040';\n"
        "\n"
        "  if not coalesce(chart_accepts_short_forms, false) then\n"
        "    raise exception 'Content hotfix failed: chart short-form answers are not accepted';\n"
        "  end if;\n"
        "\n"
        "  select stem ilike '%3 billion cycles per second%' into clock_wording_ok\n"
        "  from public.questions\n"
        "  where external_id = 'computer-hardware.practice_bank.topic_05_06_hardware_networks.q009';\n"
        "\n"
        "  if not coalesce(clock_wording_ok, false) then\n"
        "    raise exception 'Content hotfix failed: clock-speed wording was not corrected';\n"
        "  end if;\n"
        "end $$;\n"
        "\n"
        "commit;\n"
    )


if __name__ == "__main__":
    canonical_changed: list[dict[str, Any]] | None = None
    report: dict[str, Any] = {"payloads": {}, "changed_question_ids": []}
    for path in PAYLOADS:
        _, changed = patch_payload(path)
        report["payloads"][str(path.relative_to(ROOT))] = len(changed)
        if path.name == "unit1_stage5_approved_live_payload.json":
            canonical_changed = changed
            report["changed_question_ids"] = [q["question_external_id"] for q in changed]
    if canonical_changed is None:
        raise RuntimeError("Canonical live payload was not processed")
    write_migration(canonical_changed)
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
