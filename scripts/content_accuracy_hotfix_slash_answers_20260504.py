#!/usr/bin/env python3
"""Widen slash-style fill-gap accepted answers from mark-scheme shorthand.

CCEA-style notes often use slash notation to mean alternatives. A literal exact
match against the full slash phrase is unfair in an auto-marked app, so this pass
adds sensible individual accepted forms while preserving canonical grouping.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "supabase/imports/unit1_stage5_approved_live_payload.json"
MIGRATION = ROOT / "supabase/migrations/20260504173500_widen_slash_fill_gap_answers.sql"
REPORT = ROOT / "docs/content-accuracy-slash-answer-hotfix-2026-05-04.json"

ALIASES: dict[str, list[str]] = {
    "left/centre/right/full justification": [
        "left/centre/right/full justification",
        "justification",
        "left justification",
        "centre justification",
        "center justification",
        "right justification",
        "full justification",
        "alignment",
        "text alignment",
    ],
    "password protection / digital signatures": [
        "password protection / digital signatures",
        "password protection",
        "digital signatures",
        "digital signature",
    ],
    "antivirus / virus checking": [
        "antivirus / virus checking",
        "antivirus",
        "anti-virus",
        "virus checking",
        "virus checker",
    ],
    "generating gas/electricity billing information": [
        "generating gas/electricity billing information",
        "gas billing information",
        "electricity billing information",
        "generating gas billing information",
        "generating electricity billing information",
        "utility billing information",
    ],
    "text/images/videos uploaded to social media": [
        "text/images/videos uploaded to social media",
        "text uploaded to social media",
        "images uploaded to social media",
        "videos uploaded to social media",
        "social media uploads",
        "social media posts",
    ],
    "financial markets / share prices / currencies": [
        "financial markets / share prices / currencies",
        "financial markets",
        "share prices",
        "currencies",
        "currency data",
    ],
    "device logs (Internet of Things) / CCTV": [
        "device logs (Internet of Things) / CCTV",
        "device logs",
        "internet of things",
        "iot device logs",
        "CCTV",
        "cctv footage",
    ],
    "rename/insert/move sheet tabs": [
        "rename/insert/move sheet tabs",
        "rename sheet tabs",
        "insert sheet tabs",
        "move sheet tabs",
        "sheet tabs",
    ],
    "keylogger / key logger": [
        "keylogger / key logger",
        "keylogger",
        "key logger",
    ],
    "(2) keylogger / key logger": [
        "(2) keylogger / key logger",
        "keylogger / key logger",
        "keylogger",
        "key logger",
    ],
}


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


def expand_answer_value(value: str) -> list[str]:
    if value in ALIASES:
        return ALIASES[value]
    return [value]


def widen_question(question: dict[str, Any]) -> bool:
    changed = False
    rules = question.get("autograde_rules_json")
    if not isinstance(rules, dict) or rules.get("kind") != "fill_gap":
        return False

    for gap in rules.get("gaps", []):
        if not isinstance(gap, dict):
            continue
        for group in gap.get("accepted_groups", []):
            if not isinstance(group, dict) or not isinstance(group.get("accepted"), list):
                continue
            next_values: list[str] = []
            for accepted in group["accepted"]:
                if isinstance(accepted, str):
                    next_values.extend(expand_answer_value(accepted))
            next_values = unique(next_values)
            if next_values != group["accepted"]:
                group["accepted"] = next_values
                changed = True

    correct = question.get("correct_answer_json")
    if isinstance(correct, dict) and isinstance(correct.get("accepted"), list):
        next_accepted = []
        for answer_group in correct["accepted"]:
            if isinstance(answer_group, list):
                next_values: list[str] = []
                for accepted in answer_group:
                    if isinstance(accepted, str):
                        next_values.extend(expand_answer_value(accepted))
                next_values = unique(next_values)
                changed = changed or next_values != answer_group
                next_accepted.append(next_values)
            else:
                next_accepted.append(answer_group)
        correct["accepted"] = next_accepted

    return changed


def sql_literal_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("'", "''")


def write_migration(changed: list[dict[str, Any]]) -> None:
    rows = [
        {
            "external_id": q["question_external_id"],
            "correct_answer_json": q.get("correct_answer_json", {}),
            "autograde_rules_json": q.get("autograde_rules_json", {}),
        }
        for q in changed
    ]
    MIGRATION.write_text(
        "-- Widen slash-style fill-gap answer aliases after teacher verification on 2026-05-04.\n"
        "\n"
        "begin;\n"
        "\n"
        "with patch_payload as (\n"
        f"  select '{sql_literal_json(rows)}'::jsonb as data\n"
        "),\n"
        "patch_rows as (\n"
        "  select *\n"
        "  from patch_payload,\n"
        "  jsonb_to_recordset(patch_payload.data) as row(\n"
        "    external_id text,\n"
        "    correct_answer_json jsonb,\n"
        "    autograde_rules_json jsonb\n"
        "  )\n"
        ")\n"
        "update public.questions q\n"
        "set correct_answer_json = p.correct_answer_json,\n"
        "    autograde_rules_json = p.autograde_rules_json,\n"
        "    teacher_notes = concat_ws(' | ', nullif(q.teacher_notes, ''), 'Content accuracy hotfix 2026-05-04: widened slash-style fill-gap accepted answers.')\n"
        "from patch_rows p\n"
        "where q.external_id = p.external_id;\n"
        "\n"
        "do $$\n"
        "declare\n"
        "  keylogger_ok boolean;\n"
        "  password_ok boolean;\n"
        "  chart_ok boolean;\n"
        "begin\n"
        "  select public.answer_text_match_group('keylogger', autograde_rules_json -> 'gaps' -> 1 -> 'accepted_groups', 'phrase', 'exact') is not null\n"
        "  into keylogger_ok\n"
        "  from public.questions\n"
        "  where external_id = 'cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q020';\n"
        "\n"
        "  if not coalesce(keylogger_ok, false) then\n"
        "    raise exception 'Slash alias hotfix failed: keylogger is not accepted';\n"
        "  end if;\n"
        "\n"
        "  select public.answer_text_match_group('password protection', autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups', 'phrase', 'exact') is not null\n"
        "    and public.answer_text_match_group('digital signature', autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups', 'phrase', 'exact') is not null\n"
        "  into password_ok\n"
        "  from public.questions\n"
        "  where external_id = 'digital-data.practice_bank.topic_01_digital_data.q095';\n"
        "\n"
        "  if not coalesce(password_ok, false) then\n"
        "    raise exception 'Slash alias hotfix failed: PDF feature aliases are not accepted';\n"
        "  end if;\n"
        "\n"
        "  select public.answer_text_match_group('left justification', autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups', 'phrase', 'exact') is not null\n"
        "    and public.answer_text_match_group('text alignment', autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups', 'phrase', 'exact') is not null\n"
        "  into chart_ok\n"
        "  from public.questions\n"
        "  where external_id = 'digital-data.practice_bank.topic_01_digital_data.q094';\n"
        "\n"
        "  if not coalesce(chart_ok, false) then\n"
        "    raise exception 'Slash alias hotfix failed: RTF justification aliases are not accepted';\n"
        "  end if;\n"
        "end $$;\n"
        "\n"
        "commit;\n"
    )


def main() -> None:
    payload = json.loads(PAYLOAD.read_text())
    changed: list[dict[str, Any]] = []
    for question in payload["live_questions"]:
        before = json.dumps(question, sort_keys=True, ensure_ascii=False)
        if widen_question(question):
            after = json.dumps(question, sort_keys=True, ensure_ascii=False)
            if before != after:
                changed.append(question)
    PAYLOAD.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    write_migration(changed)
    report = {
        "changed_count": len(changed),
        "changed_question_ids": [q["question_external_id"] for q in changed],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
