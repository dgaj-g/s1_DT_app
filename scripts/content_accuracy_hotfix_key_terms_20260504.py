#!/usr/bin/env python3
"""Tighten remaining exact-marked short answers after the trust audit.

This pass converts remaining open-ended exact answers to MCQ and widens/cleans
fixed-term aliases where exact marking is appropriate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "supabase/imports/unit1_stage5_approved_live_payload.json"
MIGRATION = ROOT / "supabase/migrations/20260504182500_key_term_alias_and_open_answer_hotfix.sql"
REPORT = ROOT / "docs/content-accuracy-key-term-hotfix-2026-05-04.json"

MCQ_PATCHES: dict[str, dict[str, Any]] = {
    "changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q004": {
        "stem": "Which employment impact is shown when robots replace low-skilled workers in car manufacturing and warehousing?",
        "choices": ["Job displacement or job losses", "Improved ergonomic seating", "Data portability", "Cloud storage backup"],
        "correct": "Job displacement or job losses",
        "explanation": "When robots replace workers, the employment impact is job displacement or job losses.",
    },
    "changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q005": {
        "stem": "Which option is a positive impact of digital technology on employment?",
        "choices": ["Creation of new skilled jobs", "Removal of all retraining needs", "No change to work patterns", "Less need for ICT skills"],
        "correct": "Creation of new skilled jobs",
        "explanation": "Digital technology can create new skilled job opportunities, including jobs in the ICT sector.",
    },
    "changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q006": {
        "stem": "Which option is a work-pattern change caused by digital technology?",
        "choices": ["Remote working or flexible working", "Only paper-based communication", "No use of online meetings", "All jobs must be done in one office"],
        "correct": "Remote working or flexible working",
        "explanation": "Digital technology can support teleworking, remote working and more flexible work patterns.",
    },
    "changes-in-employment-opportunities-skills-requirements-and-work-practices.practice_bank.topic_09_12_wider_impact.q016": {
        "stem": "Which work pattern can result from organisations operating 24/7?",
        "choices": ["Shift work", "Batch processing", "Data compression", "Cell formatting"],
        "correct": "Shift work",
        "explanation": "If an organisation operates 24/7, workers may work shifts, including night shifts.",
    },
    "cloud-technology.practice_bank.topic_07_08_cyberspace_cloud.q014": {
        "stem": "How can cloud gaming help game designers gather feedback in real time?",
        "choices": [
            "By monitoring user behaviour, performance and preferences",
            "By removing all internet connections from games",
            "By forcing every game to run from a DVD",
            "By preventing updates after release",
        ],
        "correct": "By monitoring user behaviour, performance and preferences",
        "explanation": "Cloud gaming can allow designers to monitor user behaviour, performance and preferences in real time.",
    },
    "database-applications.past_paper.topics_03_04.q003": {
        "stem": "What is the purpose of a primary key in a database table?",
        "choices": ["To uniquely identify each record", "To store every field as currency", "To remove the need for tables", "To sort records into descending order only"],
        "correct": "To uniquely identify each record",
        "explanation": "A primary key uniquely identifies each record in a database table.",
    },
    "database-applications.past_paper.topics_03_04.q006": {
        "stem": "Which option is a technique used in data analytics to identify patterns in data?",
        "choices": ["Statistical analysis or AI algorithms", "Formatting all text in bold", "Deleting the primary key", "Turning off validation"],
        "correct": "Statistical analysis or AI algorithms",
        "explanation": "Data analytics can use techniques such as statistical analysis, AI or algorithms to identify patterns in data.",
    },
    "digital-applications.past_paper.topics_10_11_12.q007": {
        "stem": "Which option is a security-related disadvantage of online shopping?",
        "choices": ["Payment or personal details may be stolen", "The customer can inspect every item physically", "The shop must close at 5 pm", "Delivery is always instant"],
        "correct": "Payment or personal details may be stolen",
        "explanation": "A security risk of online shopping is that payment details or personal details may be stolen.",
    },
    "digital-applications.past_paper.topics_10_11_12.q011": {
        "stem": "Which option is a security-related disadvantage of online banking for customers?",
        "choices": ["A bank account or financial details may be stolen", "The customer must always visit a branch", "The service cannot use passwords", "The bank cannot update records"],
        "correct": "A bank account or financial details may be stolen",
        "explanation": "A security risk of online banking is that accounts may be hacked or financial details may be stolen.",
    },
    "digital-applications.past_paper.topics_10_11_12.q012": {
        "stem": "Which option is a technical disadvantage of online banking?",
        "choices": ["The website or service may be unavailable", "It always works without an internet connection", "It removes all authentication", "It requires only paper forms"],
        "correct": "The website or service may be unavailable",
        "explanation": "Online banking may be affected by technical glitches, maintenance or service outages.",
    },
}

ALIASES: dict[str, list[str]] = {
    "computer-hardware.past_paper.topics_05_06.q007": ["16 GB", "16GB", "16 gigabytes", "16 gigabyte"],
    "computer-hardware.past_paper.topics_05_06.q010": ["Arithmetic Logic Unit", "Arithmetic and Logic Unit"],
    "computer-hardware.past_paper.topics_05_06.q013": ["Central Processing Unit"],
    "computer-hardware.past_paper.topics_05_06.q024": ["3D Printer", "3-D Printer", "3D printer", "three dimensional printer"],
    "computer-hardware.past_paper.topics_05_06.q029": ["Central Processing Unit"],
    "computer-hardware.past_paper.topics_05_06.q040": ["Immediate Access Store", "IAS"],
    "computer-hardware.practice_bank.topic_05_06_hardware_networks.q027": ["Immediate Access Store", "IAS"],
    "cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q037": ["TCP/IP", "TCPIP", "Transmission Control Protocol/Internet Protocol", "Transmission Control Protocol Internet Protocol"],
    "database-applications.practice_bank.topic_02_03_software_database.q058": ["Entity-Relationship (ER) diagram", "Entity-Relationship diagram", "Entity Relationship diagram", "ER diagram", "E-R diagram"],
    "digital-data.practice_bank.topic_01_digital_data.q021": ["Megabyte (MB)", "Megabyte", "Megabytes", "MB"],
    "digital-data.practice_bank.topic_01_digital_data.q065": ["Data portability", "Portability"],
    "digital-data.practice_bank.topic_01_digital_data.q119": ["Colour depth", "Color depth", "Bit depth"],
    "ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q017": ["Data Protection Act", "DPA", "Data Protection Act 2018"],
    "network-technologies.past_paper.topics_05_06.q006": ["Local Area Network", "LAN"],
    "network-technologies.past_paper.topics_05_06.q022": ["Internet of Things", "IoT", "IOT"],
    "network-technologies.past_paper.topics_05_06.q028": ["Wide Area Network", "WAN"],
    "network-technologies.past_paper.topics_05_06.q031": ["Local Area Network", "LAN"],
    "network-technologies.past_paper.topics_05_06.q044": ["Internet of Things", "IoT", "IOT"],
    "network-technologies.practice_bank.topic_05_06_hardware_networks.q029": ["Twisted pair", "Twisted-pair", "Twisted pair cable", "Twisted-pair cable"],
    "software.past_paper.topics_01_02.q017": ["Booting", "Booting up", "Bootup", "Boot up", "Start up sequence", "Startup sequence", "Start-up sequence"],
    "software.practice_bank.topic_02_03_software_database.q032": ["ROM (Read Only Memory)", "ROM", "Read Only Memory", "Read-Only Memory"],
    "software.practice_bank.topic_02_03_software_database.q033": ["Cache (memory)", "Cache", "Cache memory"],
}


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        key = text.lower()
        if key not in seen:
            out.append(text)
            seen.add(key)
    return out


def schema_choice(label: str, index: int) -> dict[str, str]:
    return {"id": chr(ord("a") + index), "label": label}


def apply_mcq(question: dict[str, Any], patch: dict[str, Any]) -> None:
    choices = patch["choices"]
    correct = patch["correct"]
    schema_choices = [schema_choice(choice, i) for i, choice in enumerate(choices)]
    correct_id = schema_choices[choices.index(correct)]["id"]
    question["format"] = "mcq"
    question["stem"] = patch["stem"]
    question["options_json"] = {"choices": choices}
    question["correct_answer_json"] = {"choice": correct}
    question["markscheme_points_json"] = [correct]
    question["explanation"] = patch["explanation"]
    question["max_marks"] = 1
    question["content_blocks_json"] = [{"kind": "text", "text": patch["stem"], "block_key": None}]
    question["response_schema_json"] = {"kind": "single_choice", "choices": schema_choices}
    question["autograde_rules_json"] = {"kind": "single_choice", "correct_choice_id": correct_id}
    question["tags_json"] = unique([*(question.get("tags_json") or []), "multiple-choice", "objective-marking-hotfix"])


def apply_aliases(question: dict[str, Any], accepted: list[str]) -> None:
    accepted = unique(accepted)
    question["correct_answer_json"] = {"accepted": accepted}
    question["markscheme_points_json"] = [accepted[0]]
    question["autograde_rules_json"] = {
        "kind": "accepted_terms",
        "accepted": accepted,
        "normalization": "phrase",
        "match_mode": "exact",
    }
    if question.get("question_external_id") == "software.practice_bank.topic_02_03_software_database.q033":
        question["explanation"] = "An accepted answer is cache memory. This question checks whether you can identify the type of memory used to store frequently accessed instructions or data."


def patch_payload() -> list[dict[str, Any]]:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    changed: list[dict[str, Any]] = []
    for question in payload["live_questions"]:
        external_id = question["question_external_id"]
        before = json.dumps(question, sort_keys=True, ensure_ascii=False)
        if external_id in MCQ_PATCHES:
            apply_mcq(question, MCQ_PATCHES[external_id])
        if external_id in ALIASES:
            apply_aliases(question, ALIASES[external_id])
        after = json.dumps(question, sort_keys=True, ensure_ascii=False)
        if before != after:
            question["teacher_notes"] = (
                (question.get("teacher_notes") or "").rstrip()
                + " | Content accuracy hotfix 2026-05-04: checked exact-marked answer and improved objective reliability or aliases."
            ).strip(" |")
            changed.append(question)
    PAYLOAD.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def sql_literal(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return "'" + text.replace("'", "''") + "'::jsonb"


def sql_text_array(values: list[str]) -> str:
    return "array[" + ", ".join("'" + value.replace("'", "''") + "'" for value in values) + "]"


def write_migration(changed: list[dict[str, Any]]) -> None:
    rows = [
        {
            "external_id": q["question_external_id"],
            "format": q["format"],
            "stem": q["stem"],
            "options_json": q.get("options_json") or {},
            "correct_answer_json": q.get("correct_answer_json") or {},
            "markscheme_points_json": q.get("markscheme_points_json") or [],
            "explanation": q.get("explanation") or "",
            "max_marks": q.get("max_marks") or 1,
            "content_blocks_json": q.get("content_blocks_json") or [],
            "response_schema_json": q.get("response_schema_json") or {},
            "autograde_rules_json": q.get("autograde_rules_json") or {},
            "tags_json": q.get("tags_json") or [],
        }
        for q in changed
    ]
    ids = [row["external_id"] for row in rows]
    migration = f"""-- Key-term alias and remaining open-answer hotfix after trust audit on 2026-05-04.

begin;

with patch_payload as (
  select {sql_literal(rows)} as data
),
patch_rows as (
  select *
  from patch_payload,
  jsonb_to_recordset(patch_payload.data) as row(
    external_id text,
    format text,
    stem text,
    options_json jsonb,
    correct_answer_json jsonb,
    markscheme_points_json jsonb,
    explanation text,
    max_marks integer,
    content_blocks_json jsonb,
    response_schema_json jsonb,
    autograde_rules_json jsonb,
    tags_json jsonb
  )
)
update public.questions q
set format = p.format::public.question_format,
    stem = p.stem,
    options_json = p.options_json,
    correct_answer_json = p.correct_answer_json,
    markscheme_points_json = p.markscheme_points_json,
    explanation = p.explanation,
    max_marks = greatest(1, least(20, coalesce(p.max_marks, 1)))::smallint,
    content_blocks_json = p.content_blocks_json,
    response_schema_json = p.response_schema_json,
    autograde_rules_json = p.autograde_rules_json,
    tags_json = p.tags_json,
    teacher_notes = concat_ws(' | ', nullif(q.teacher_notes, ''), 'Content accuracy hotfix 2026-05-04: checked exact-marked answers and improved objective reliability or aliases.')
from patch_rows p
where q.external_id = p.external_id;

update public.session_questions sq
set question_snapshot_json = public.build_runtime_question_payload(sq.question_id, sq.id)
from public.sessions s, public.questions q
where s.id = sq.session_id
  and q.id = sq.question_id
  and s.completed_at is null
  and q.external_id = any ({sql_text_array(ids)});

do $$
declare
  cache_memory_alone_ok boolean;
  cache_alias_ok boolean;
  tcpip_ok boolean;
  color_depth_ok boolean;
begin
  select public.answer_text_matches('memory', autograde_rules_json -> 'accepted', 'phrase', 'exact') into cache_memory_alone_ok
  from public.questions
  where external_id = 'software.practice_bank.topic_02_03_software_database.q033';

  if coalesce(cache_memory_alone_ok, false) then
    raise exception 'Key-term hotfix failed: plain memory is still accepted for cache question';
  end if;

  select public.answer_text_matches('cache memory', autograde_rules_json -> 'accepted', 'phrase', 'exact') into cache_alias_ok
  from public.questions
  where external_id = 'software.practice_bank.topic_02_03_software_database.q033';

  if not coalesce(cache_alias_ok, false) then
    raise exception 'Key-term hotfix failed: cache memory is not accepted';
  end if;

  select public.answer_text_matches('TCPIP', autograde_rules_json -> 'accepted', 'phrase', 'exact') into tcpip_ok
  from public.questions
  where external_id = 'cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q037';

  if not coalesce(tcpip_ok, false) then
    raise exception 'Key-term hotfix failed: TCPIP alias is not accepted';
  end if;

  select public.answer_text_matches('color depth', autograde_rules_json -> 'accepted', 'phrase', 'exact') into color_depth_ok
  from public.questions
  where external_id = 'digital-data.practice_bank.topic_01_digital_data.q119';

  if not coalesce(color_depth_ok, false) then
    raise exception 'Key-term hotfix failed: color depth alias is not accepted';
  end if;
end $$;

commit;
"""
    MIGRATION.write_text(migration, encoding="utf-8")


def main() -> None:
    changed = patch_payload()
    write_migration(changed)
    REPORT.write_text(
        json.dumps(
            {
                "changed_count": len(changed),
                "changed_question_external_ids": [q["question_external_id"] for q in changed],
                "migration": str(MIGRATION.relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"changed": len(changed), "migration": str(MIGRATION)}, indent=2))


if __name__ == "__main__":
    main()
