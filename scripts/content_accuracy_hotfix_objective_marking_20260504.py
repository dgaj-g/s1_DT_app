#!/usr/bin/env python3
"""Convert brittle exact-marked prompts into reliable scored objective items.

This pass addresses the teacher's accuracy/marking feedback from 2026-05-04:
- open-ended "state one..." short-text questions are converted to MCQ;
- generic "Complete the sentence" stems are rewritten with the actual sentence;
- spreadsheet formatting fill-gaps accept only genuine formatting features;
- current active session snapshots are refreshed by the generated migration.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "supabase/imports/unit1_stage5_approved_live_payload.json"
MIGRATION = ROOT / "supabase/migrations/20260504180500_objective_marking_reliability_hotfix.sql"
REPORT = ROOT / "docs/content-accuracy-objective-marking-hotfix-2026-05-04.json"

MCQ_PATCHES: dict[str, dict[str, Any]] = {
    "changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q001": {
        "stem": "Which option is an advantage of teleworking for an employer?",
        "choices": [
            "Lower office or rent costs",
            "More desks needed in the office",
            "Higher travel expenses for staff",
            "No need for any network access",
        ],
        "correct": "Lower office or rent costs",
        "explanation": "Teleworking can reduce overheads such as office space, rent and related running costs for an employer.",
    },
    "changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q002": {
        "stem": "Which option is an advantage of teleworking when recruiting staff?",
        "choices": [
            "The employer can recruit from a wider geographical area",
            "The employer must recruit only local staff",
            "The employer must remove all online communication",
            "The employer cannot use specialist staff",
        ],
        "correct": "The employer can recruit from a wider geographical area",
        "explanation": "Teleworking can remove geographical restrictions, so an employer may recruit suitable staff from a wider area.",
    },
    "computer-hardware.practice_bank.topic_05_06_hardware_networks.q032": {
        "stem": "Which option is a disadvantage of a wireless microphone?",
        "choices": [
            "It can have limited range or battery life",
            "It must always be connected by a long cable",
            "It cannot record sound waves",
            "It is a type of secondary storage",
        ],
        "correct": "It can have limited range or battery life",
        "explanation": "A wireless microphone may be limited by range and battery life, even though it avoids a trailing cable.",
    },
    "digital-applications.past_paper.topics_10_11_12.q001": {
        "stem": "Which option is an advantage of online training for staff?",
        "choices": [
            "They can learn at a convenient time or pace",
            "They must all travel to the same classroom",
            "They cannot revisit training materials",
            "They must complete training only during a live lesson",
        ],
        "correct": "They can learn at a convenient time or pace",
        "explanation": "Online training can allow staff to learn at a time and pace that suits them.",
    },
    "digital-applications.past_paper.topics_10_11_12.q002": {
        "stem": "Which option is an advantage of online training for a company?",
        "choices": [
            "Reduced training costs",
            "More travel and venue costs",
            "No way to update training materials",
            "No access for staff outside the office",
        ],
        "correct": "Reduced training costs",
        "explanation": "Online training can reduce costs because companies may avoid venue, travel or external trainer costs.",
    },
    "digital-applications.past_paper.topics_10_11_12.q003": {
        "stem": "Which option is an advantage of online training for the learner?",
        "choices": [
            "They can access training from different locations or times",
            "They must attend one fixed physical location",
            "They cannot pause or repeat content",
            "They must use paper files only",
        ],
        "correct": "They can access training from different locations or times",
        "explanation": "Online training can be accessed remotely and flexibly, which can make learning more convenient.",
    },
    "digital-applications.past_paper.topics_10_11_12.q005": {
        "stem": "Which option is a disadvantage of online shopping for a customer?",
        "choices": [
            "The goods may not meet expectations when they arrive",
            "The customer can physically try every item first",
            "The shop must be open only during local opening hours",
            "The customer cannot compare prices online",
        ],
        "correct": "The goods may not meet expectations when they arrive",
        "explanation": "With online shopping, customers cannot fully inspect or try goods before buying, so items may not meet expectations.",
    },
    "digital-applications.past_paper.topics_10_11_12.q006": {
        "stem": "Which option is another disadvantage of online shopping for a customer?",
        "choices": [
            "There may be a delay before goods are delivered",
            "Goods always arrive instantly",
            "Online shopping removes all risk of damaged goods",
            "Payment details are never required",
        ],
        "correct": "There may be a delay before goods are delivered",
        "explanation": "A customer may have to wait for delivery when buying goods online.",
    },
    "digital-applications.past_paper.topics_10_11_12.q008": {
        "stem": "Which option is a disadvantage of online training?",
        "choices": [
            "Reduced face-to-face or group interaction",
            "Students must always be in the same classroom",
            "Materials cannot be accessed online",
            "It removes the need for any device or connection",
        ],
        "correct": "Reduced face-to-face or group interaction",
        "explanation": "Online training can reduce direct face-to-face contact and group interaction.",
    },
    "digital-applications.past_paper.topics_10_11_12.q009": {
        "stem": "Which option is another disadvantage of online training?",
        "choices": [
            "Learners may feel isolated",
            "Learners always have more face-to-face support",
            "Learners cannot access materials at home",
            "It guarantees faster learning for every user",
        ],
        "correct": "Learners may feel isolated",
        "explanation": "Some learners may feel isolated because online training can reduce social contact and immediate support.",
    },
    "digital-applications.past_paper.topics_10_11_12.q010": {
        "stem": "Apart from health hazards, which option is a disadvantage of computer gaming?",
        "choices": [
            "It can become addictive or reduce face-to-face social time",
            "It always improves schoolwork",
            "It guarantees more outdoor exercise",
            "It prevents all online communication",
        ],
        "correct": "It can become addictive or reduce face-to-face social time",
        "explanation": "A non-health disadvantage of gaming is that it can become addictive or reduce time for schoolwork and face-to-face interaction.",
    },
    "digital-applications.past_paper.topics_10_11_12.q013": {
        "stem": "Which option is a disadvantage of online banking linked to lack of personal interaction?",
        "choices": [
            "There is no face-to-face contact with a bank teller",
            "It always provides longer face-to-face discussions",
            "It can only be used inside a branch",
            "It removes the need for authentication",
        ],
        "correct": "There is no face-to-face contact with a bank teller",
        "explanation": "Online banking can lack personal interaction because customers do not speak face to face with a bank teller.",
    },
    "network-technologies.practice_bank.topic_05_06_hardware_networks.q030": {
        "stem": "Which option is a communication method that a network can allow users to use easily?",
        "choices": [
            "Email",
            "BIOS setup",
            "Disk defragmentation",
            "Screen brightness control",
        ],
        "correct": "Email",
        "explanation": "Networks can make communication methods such as email, instant messaging and video conferencing easier to use.",
    },
}

GENERIC_FILL_STEMS: dict[str, str] = {
    "digital-data.practice_bank.topic_01_digital_data.q009": "Complete the sentence: ____ is meaningless raw facts and figures, but when it is processed and given meaning it becomes ____.",
    "digital-data.practice_bank.topic_01_digital_data.q046": "Complete the sentence: A bitmap image is made up of individual ____, while a vector image is made up of objects defined by mathematical ____.",
    "digital-data.practice_bank.topic_01_digital_data.q059": "Complete the sentence: A ____ detects sound waves and converts them to ____ variations that can be captured digitally.",
    "digital-data.practice_bank.topic_01_digital_data.q114": "Complete the sentence: ____ compression discards some data permanently, while ____ compression allows the original file to be fully restored.",
}

FORMATTING_FEATURE_GROUPS = [
    {"canonical": "change font", "accepted": ["change font", "font", "font type", "font size", "font style", "bold", "italic", "underline"]},
    {"canonical": "change cell background colour", "accepted": ["change cell background colour", "cell background colour", "background colour", "fill colour", "cell fill colour", "shading"]},
    {"canonical": "add borders", "accepted": ["add borders", "add a border", "add a border to cells", "cell borders", "borders"]},
    {"canonical": "merge and centre", "accepted": ["merge and centre", "merge & centre", "merge cells", "merge and center", "merge & center"]},
    {"canonical": "format as currency", "accepted": ["format as currency", "format cells to currency", "currency", "currency format"]},
    {"canonical": "text alignment", "accepted": ["text alignment", "alignment", "left align", "right align", "centre align", "center align", "justify", "justification"]},
    {"canonical": "decimal places", "accepted": ["decimal places", "change decimal places", "number of decimal places"]},
]


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


def slug_choice(label: str, index: int) -> dict[str, str]:
    return {"id": chr(ord("a") + index), "label": label}


def apply_mcq_patch(question: dict[str, Any], patch: dict[str, Any]) -> None:
    choices = patch["choices"]
    correct = patch["correct"]
    correct_index = choices.index(correct)
    schema_choices = [slug_choice(choice, i) for i, choice in enumerate(choices)]
    question["format"] = "mcq"
    question["stem"] = patch["stem"]
    question["options_json"] = {"choices": choices}
    question["correct_answer_json"] = {"choice": correct}
    question["markscheme_points_json"] = [correct]
    question["explanation"] = patch["explanation"]
    question["max_marks"] = 1
    question["content_blocks_json"] = [{"kind": "text", "text": patch["stem"], "block_key": None}]
    question["response_schema_json"] = {"kind": "single_choice", "choices": schema_choices}
    question["autograde_rules_json"] = {"kind": "single_choice", "correct_choice_id": schema_choices[correct_index]["id"]}
    question["tags_json"] = unique([*(question.get("tags_json") or []), "multiple-choice", "objective-marking-hotfix"])
    question["teacher_notes"] = (
        (question.get("teacher_notes") or "").rstrip()
        + " | Content accuracy hotfix 2026-05-04: converted from brittle open-ended exact marking to objective MCQ."
    ).strip(" |")


def apply_generic_fill_patch(question: dict[str, Any], stem: str) -> None:
    question["stem"] = stem
    question["content_blocks_json"] = [{"kind": "text", "text": stem, "block_key": None}]
    if question.get("question_external_id") == "digital-data.practice_bank.topic_01_digital_data.q059":
        question["explanation"] = "An accepted answer is microphone; voltage. This question checks whether you can recognise how sound is captured before being converted into digital data."
    question["teacher_notes"] = (
        (question.get("teacher_notes") or "").rstrip()
        + " | Content accuracy hotfix 2026-05-04: replaced generic 'Complete the sentence' prompt with the full sentence."
    ).strip(" |")


def apply_formatting_patch(question: dict[str, Any]) -> None:
    stem = "State two formatting features available in spreadsheet software."
    question["stem"] = stem
    question["correct_answer_json"] = {"accepted": [[g["canonical"] for g in FORMATTING_FEATURE_GROUPS], [g["canonical"] for g in FORMATTING_FEATURE_GROUPS]]}
    question["markscheme_points_json"] = [g["canonical"] for g in FORMATTING_FEATURE_GROUPS]
    question["explanation"] = "Accepted spreadsheet formatting features include font changes, cell background colour, borders, merge and centre, currency formatting, alignment and decimal places."
    question["content_blocks_json"] = [{"kind": "text", "text": stem, "block_key": None}]
    question["autograde_rules_json"] = {
        "kind": "fill_gap",
        "gaps": [
            {"id": "gap1", "normalization": "phrase", "match_mode": "exact", "accepted_groups": FORMATTING_FEATURE_GROUPS},
            {"id": "gap2", "normalization": "phrase", "match_mode": "exact", "accepted_groups": FORMATTING_FEATURE_GROUPS},
        ],
        "require_all": True,
        "require_distinct": True,
    }
    question["teacher_notes"] = (
        (question.get("teacher_notes") or "").rstrip()
        + " | Content accuracy hotfix 2026-05-04: limited accepted answers to genuine spreadsheet formatting features and blocked duplicate answers."
    ).strip(" |")


def patch_payload() -> list[dict[str, Any]]:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    changed: list[dict[str, Any]] = []
    for question in payload["live_questions"]:
        external_id = question["question_external_id"]
        before = json.dumps(question, sort_keys=True, ensure_ascii=False)
        if external_id in MCQ_PATCHES:
            apply_mcq_patch(question, MCQ_PATCHES[external_id])
        if external_id in GENERIC_FILL_STEMS:
            apply_generic_fill_patch(question, GENERIC_FILL_STEMS[external_id])
        if external_id == "spreadsheet-applications.practice_bank.topic_04_spreadsheet.q041":
            apply_formatting_patch(question)
        after = json.dumps(question, sort_keys=True, ensure_ascii=False)
        if before != after:
            changed.append(question)
    PAYLOAD.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def sql_literal(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return "'" + text.replace("'", "''") + "'::jsonb"


def sql_text_array(values: list[str]) -> str:
    return "array[" + ", ".join("'" + value.replace("'", "''") + "'" for value in values) + "]"


def write_migration(changed: list[dict[str, Any]]) -> None:
    rows = []
    for question in changed:
        rows.append(
            {
                "external_id": question["question_external_id"],
                "format": question["format"],
                "stem": question["stem"],
                "options_json": question.get("options_json") or {},
                "correct_answer_json": question.get("correct_answer_json") or {},
                "markscheme_points_json": question.get("markscheme_points_json") or [],
                "explanation": question.get("explanation") or "",
                "max_marks": question.get("max_marks") or 1,
                "content_blocks_json": question.get("content_blocks_json") or [],
                "response_schema_json": question.get("response_schema_json") or {},
                "autograde_rules_json": question.get("autograde_rules_json") or {},
                "tags_json": question.get("tags_json") or [],
            }
        )
    changed_ids = [row["external_id"] for row in rows]
    migration = f"""-- Objective-marking reliability hotfix after teacher accuracy feedback on 2026-05-04.
-- Converts brittle open-ended short answers to MCQ, rewrites generic fill-gap stems,
-- and removes non-formatting spreadsheet answers from a formatting-feature item.

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
    teacher_notes = concat_ws(' | ', nullif(q.teacher_notes, ''), 'Content accuracy hotfix 2026-05-04: improved objective marking reliability and prompt clarity.')
from patch_rows p
where q.external_id = p.external_id;

-- Existing in-progress sessions carry snapshots, so refresh them to avoid stale bad wording.
update public.session_questions sq
set question_snapshot_json = public.build_runtime_question_payload(sq.question_id, sq.id)
from public.sessions s, public.questions q
where s.id = sq.session_id
  and q.id = sq.question_id
  and s.completed_at is null
  and q.external_id = any ({sql_text_array(changed_ids)});

do $$
declare
  high_issue_count integer;
  generic_count integer;
  lower_b12_ok boolean;
  chart_short_ok boolean;
begin
  select count(*) into generic_count
  from public.questions
  where is_active = true
    and stem ~* '^\\s*complete the sentences?\\s*$';

  if generic_count <> 0 then
    raise exception 'Objective marking hotfix failed: % active generic complete-sentence stems remain', generic_count;
  end if;

  select public.answer_text_match_group(
    'b12',
    autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups',
    'phrase',
    'exact'
  ) is not null into lower_b12_ok
  from public.questions
  where external_id = 'spreadsheet-applications.past_paper.topics_03_04.q034';

  if not coalesce(lower_b12_ok, false) then
    raise exception 'Objective marking hotfix failed: lowercase b12 is not accepted';
  end if;

  select public.answer_text_match_group(
    'column',
    autograde_rules_json -> 'gaps' -> 0 -> 'accepted_groups',
    'phrase',
    'exact'
  ) is not null
  and public.answer_text_match_group(
    'bar',
    autograde_rules_json -> 'gaps' -> 1 -> 'accepted_groups',
    'phrase',
    'exact'
  ) is not null
  and public.answer_text_match_group(
    'pie',
    autograde_rules_json -> 'gaps' -> 2 -> 'accepted_groups',
    'phrase',
    'exact'
  ) is not null into chart_short_ok
  from public.questions
  where external_id = 'spreadsheet-applications.practice_bank.topic_04_spreadsheet.q040';

  if not coalesce(chart_short_ok, false) then
    raise exception 'Objective marking hotfix failed: chart short answers are not accepted';
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
