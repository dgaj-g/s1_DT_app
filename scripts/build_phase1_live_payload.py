#!/usr/bin/env python3
"""Build Phase 1 live runtime payloads from approved staged questions.

This script is the promotion bridge between the Stage 4 staging payload and the
Phase 1 runtime contract. It is intentionally strict:

- only approved staged questions may promote by default;
- known open defects block promotion;
- unsupported or weakly normalized formats are rejected;
- student-facing runtime structures must be explicit and self-markable.

The output is not a direct Supabase write. It is a normalized payload that can
later be applied to:

- public.questions
- public.content_sources
- public.question_source_links
- public.question_assets
- public.question_asset_links
- public.question_objectives
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "supabase" / "imports" / "unit1_stage4_staging_payload.json"
DEFAULT_DEFECTS = REPO_ROOT / "docs" / "stage-4-content-defect-register-2026-05-03.md"
DEFAULT_OUTPUT = REPO_ROOT / "supabase" / "imports" / "unit1_phase1_live_payload.json"

SUPPORTED_LIVE_FORMATS = {"mcq", "true_false", "match_table", "fill_gap", "short_text", "drag_drop"}
ALLOWED_STAGING_STATUSES = {"approved"}
RAW_PROSE_PATTERNS = (
    "accept:",
    "also accept",
    "any 2 from",
    "any 1 from",
    "do not accept",
    "don't accept",
    "for example",
    "e.g.",
    "eg ",
)
MATCH_ARROW_RE = re.compile(r"^\s*([A-Za-z0-9]+)\s*(?:→|->|=>|:)\s*([A-Za-z0-9]+)\s*$")
BACKTICK_EXTERNAL_ID_RE = re.compile(r"`([a-z0-9-]+\.(?:past_paper|practice_bank|mark_scheme)\.[a-z0-9_.-]+)`")
QUESTION_SHORT_ID_RE = re.compile(r"`(q\d+)`")
OPTION_SEGMENT_RE = re.compile(r"\b([A-Z])\.\s*(.+?)(?=(?:\s*[;|]\s*[A-Z]\.\s)|$)")
BLANK_RE = re.compile(r"_{3,}")


def normalize_text(text: str) -> str:
    return " ".join(str(text or "").split()).strip()


def slugify(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", normalize_text(text).lower())
    return value.strip("-") or "item"


def stable_hash(text: str, length: int = 12) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def stable_item_id(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_defect_register(path: Path) -> dict[str, list[str]]:
    by_question: dict[str, list[str]] = defaultdict(list)
    block_ids: set[str] = set()
    current_prefix: str | None = None
    current_status: str | None = None
    current_code: str | None = None

    def flush_block() -> None:
        nonlocal block_ids, current_prefix, current_status, current_code, by_question
        if not block_ids or not current_code:
            block_ids = set()
            current_prefix = None
            current_status = None
            current_code = None
            return

        status_text = (current_status or "").lower()
        is_closed = (
            ("closed" in status_text or "resolved" in status_text)
            and "pending" not in status_text
        )
        if not is_closed:
            for external_id in block_ids:
                by_question[external_id].append(current_code)

        block_ids = set()
        current_prefix = None
        current_status = None
        current_code = None

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if stripped.startswith("### "):
            flush_block()
            current_code = stripped[4:].split("—", 1)[0].strip()

        full_ids = BACKTICK_EXTERNAL_ID_RE.findall(line)
        if full_ids:
            for external_id in full_ids:
                block_ids.add(external_id)
                current_prefix = external_id.rsplit(".q", 1)[0]
        elif current_prefix:
            for short_id in QUESTION_SHORT_ID_RE.findall(line):
                block_ids.add(f"{current_prefix}.{short_id}")

        if stripped.lower().startswith("- status:"):
            current_status = stripped.split(":", 1)[1].strip()

    flush_block()
    return dict(by_question)


def group_assets_by_question(payload: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for asset in payload.get("staged_question_assets", []):
        grouped[asset["question_external_id"]].append(asset)
    return grouped


def get_review_flags(question: dict) -> list[str]:
    metadata = question.get("metadata_json", {})
    flags = metadata.get("review_flags", [])
    return flags if isinstance(flags, list) else []


def build_content_sources(questions: Iterable[dict]) -> tuple[list[dict], dict[tuple[str, str, str, str, str], str]]:
    records: list[dict] = []
    key_map: dict[tuple[str, str, str, str, str], str] = {}

    for question in questions:
        key = (
            question.get("topic_slug", ""),
            question.get("source_kind", ""),
            question.get("source_title", ""),
            question.get("source_file_name", ""),
            question.get("source_locator", ""),
        )
        if key in key_map:
            continue

        external_id = "source-" + stable_hash("|".join(key), 16)
        key_map[key] = external_id
        records.append(
            {
                "content_source_external_id": external_id,
                "topic_slug": question.get("topic_slug", ""),
                "source_kind": question.get("source_kind", "teacher_note"),
                "title": question.get("source_title", "") or "Unknown source",
                "file_name": question.get("source_file_name", "") or "unknown",
                "year_label": None,
                "locator_text": question.get("source_locator", "") or "",
                "metadata_json": {
                    "source_set": question.get("metadata_json", {}).get("source_set"),
                    "question_external_id_sample": question.get("question_external_id"),
                },
            }
        )

    return records, key_map


def has_unresolved_assets(assets: list[dict]) -> bool:
    for asset in assets:
        if asset.get("asset_role") != "prompt":
            continue
        metadata = asset.get("metadata_json", {})
        if isinstance(metadata, dict) and not metadata.get("resolved", False):
            return True
    return False


def is_true_false_misclassified(question: dict) -> bool:
    if question.get("format") != "match_table":
        return False
    options_payload = question.get("options_json", {})
    answer_payload = question.get("correct_answer_json", {})
    if (
        isinstance(options_payload, dict)
        and isinstance(options_payload.get("rows"), list)
        and isinstance(options_payload.get("choices"), list)
        and isinstance(answer_payload.get("pairs"), list)
    ):
        choice_labels = {
            normalize_text(str(choice.get("label", ""))).lower()
            for choice in options_payload.get("choices", [])
            if isinstance(choice, dict)
        }
        if choice_labels <= {"true", "false"} and {"true", "false"} <= choice_labels:
            return False
    metadata = question.get("metadata_json", {})
    qtype = normalize_text(metadata.get("qtype_label", "")).lower()
    tags = [str(tag).lower() for tag in question.get("tags_json", [])]
    answer = normalize_text(question.get("correct_answer_json", {}).get("raw", "")).lower()
    return (
        "true / false" in qtype
        or "true/false" in qtype
        or "true-false" in tags
        or answer in {"true", "false"}
    )


def split_simple_terms(raw: str) -> list[str] | None:
    text = normalize_text(raw)
    if not text:
        return None

    lowered = text.lower()
    if any(pattern in lowered for pattern in RAW_PROSE_PATTERNS):
        return None

    if "(" in text and "accept" in lowered:
        return None

    separators = []
    if ";" in text:
        separators.append(";")
    if " / " in text:
        separators.append(" / ")
    if " or " in lowered:
        separators.append(" or ")

    if not separators:
        return [text]

    separator = separators[0]
    if separator == " or ":
        parts = [part.strip() for part in re.split(r"\bor\b", text, flags=re.IGNORECASE) if part.strip()]
    else:
        parts = [part.strip() for part in text.split(separator) if part.strip()]

    if not parts:
        return None

    if any(len(part.split()) > 6 for part in parts):
        return None

    return parts


def infer_normalization_mode(accepted_terms: list[str]) -> str:
    if all(re.fullmatch(r"[A-Za-z0-9$%./-]+", term) for term in accepted_terms):
        return "token"
    return "phrase"


def normalize_prompt_blocks(blocks: list[dict]) -> list[dict]:
    runtime_blocks: list[dict] = []
    for block in blocks:
        block_type = block.get("type", "text")
        if block_type == "list_block":
            runtime_blocks.append(
                {
                    "kind": "list",
                    "label": block.get("label", ""),
                    "items": block.get("items", []),
                    "block_key": block.get("block_key"),
                }
            )
        elif block_type == "figure":
            runtime_blocks.append(
                {
                    "kind": "figure",
                    "caption": block.get("caption", ""),
                    "block_key": block.get("block_key"),
                }
            )
        else:
            runtime_blocks.append(
                {
                    "kind": "text",
                    "text": block.get("text", ""),
                    "block_key": block.get("block_key"),
                }
            )
    return runtime_blocks


def parse_mcq(question: dict) -> tuple[dict | None, dict | None, dict | None, list[str]]:
    reasons: list[str] = []
    options = question.get("options_json", [])
    if not isinstance(options, list) or len(options) != 4:
        return None, None, None, ["invalid_mcq_option_count"]

    choices: list[dict] = []
    key_to_choice_id: dict[str, str] = {}
    label_to_choice_id: dict[str, str] = {}

    for idx, option in enumerate(options):
        if not isinstance(option, dict):
            return None, None, None, ["invalid_mcq_option_structure"]
        key = normalize_text(option.get("key", "")) or chr(ord("A") + idx)
        label = normalize_text(option.get("text", ""))
        if not label:
            return None, None, None, ["empty_mcq_option_label"]
        choice_id = slugify(key.lower()) or f"choice-{idx + 1}"
        choices.append({"id": choice_id, "label": label})
        key_to_choice_id[key.upper()] = choice_id
        label_to_choice_id[label.lower()] = choice_id

    raw_answer = normalize_text(question.get("correct_answer_json", {}).get("raw", ""))
    answer_key = raw_answer.upper()
    correct_choice_id = key_to_choice_id.get(answer_key) or label_to_choice_id.get(raw_answer.lower())
    if not correct_choice_id:
        reasons.append("invalid_mcq_correct_answer")

    if reasons:
        return None, None, None, reasons

    response_schema = {"kind": "single_choice", "choices": choices}
    autograde_rules = {"kind": "single_choice", "correct_choice_id": correct_choice_id}
    choice_lookup = {item["id"]: item["label"] for item in choices}
    legacy_options = {"choices": [item["label"] for item in choices]}
    legacy_answers = {"choice": choice_lookup[correct_choice_id]}
    return response_schema, autograde_rules, {"options_json": legacy_options, "correct_answer_json": legacy_answers}, []


def parse_true_false(question: dict) -> tuple[dict | None, dict | None, dict | None, list[str]]:
    raw_answer = normalize_text(question.get("correct_answer_json", {}).get("raw", "")).lower()
    if raw_answer not in {"true", "false"}:
        return None, None, None, ["invalid_true_false_answer"]

    response_schema = {
        "kind": "true_false",
        "statement": question.get("stem", ""),
        "true_label": "True",
        "false_label": "False",
    }
    autograde_rules = {"kind": "true_false", "correct_value": raw_answer == "true"}
    legacy_options = {"statement": question.get("stem", ""), "choices": ["True", "False"]}
    legacy_answers = {"choice": "True" if raw_answer == "true" else "False"}
    return response_schema, autograde_rules, {"options_json": legacy_options, "correct_answer_json": legacy_answers}, []


def extract_lettered_choices(question: dict) -> list[tuple[str, str]]:
    candidates: list[str] = []
    for block in question.get("content_blocks_json", []):
        if block.get("type") == "text":
            candidates.append(str(block.get("text", "")))
    candidates.append(str(question.get("stem", "")))

    matches: list[tuple[str, str]] = []
    for text in candidates:
        for key, label in OPTION_SEGMENT_RE.findall(text):
            cleaned = normalize_text(label)
            if cleaned:
                matches.append((key.upper(), cleaned))
        if matches:
            break
    return matches


def parse_match_pairs(raw: str) -> dict[str, str] | None:
    text = normalize_text(raw)
    if not text:
        return None
    pieces = [piece.strip() for piece in re.split(r"\s*;\s*", text) if piece.strip()]
    mapping: dict[str, str] = {}
    for piece in pieces:
        match = MATCH_ARROW_RE.match(piece)
        if not match:
            return None
        mapping[match.group(1).upper()] = match.group(2).upper()
    return mapping if mapping else None


def parse_match_table(question: dict) -> tuple[dict | None, dict | None, dict | None, list[str]]:
    if is_true_false_misclassified(question):
        return None, None, None, ["true_false_still_modeled_as_match_table"]

    options_payload = question.get("options_json", {})
    answer_payload = question.get("correct_answer_json", {})
    if (
        isinstance(options_payload, dict)
        and isinstance(options_payload.get("rows"), list)
        and isinstance(options_payload.get("choices"), list)
        and isinstance(answer_payload.get("pairs"), list)
        and options_payload.get("rows")
        and options_payload.get("choices")
        and answer_payload.get("pairs")
    ):
        rows = [
            {"id": normalize_text(row.get("id", "")), "label": normalize_text(row.get("label", ""))}
            for row in options_payload.get("rows", [])
            if normalize_text(row.get("id", "")) and normalize_text(row.get("label", ""))
        ]
        choices = [
            {"id": normalize_text(choice.get("id", "")), "label": normalize_text(choice.get("label", ""))}
            for choice in options_payload.get("choices", [])
            if normalize_text(choice.get("id", "")) and normalize_text(choice.get("label", ""))
        ]
        normalized_pairs = [
            {
                "row_id": normalize_text(pair.get("row_id", "")),
                "choice_id": normalize_text(pair.get("choice_id", "")),
            }
            for pair in answer_payload.get("pairs", [])
            if normalize_text(pair.get("row_id", "")) and normalize_text(pair.get("choice_id", ""))
        ]

        if not rows or not choices or not normalized_pairs:
            return None, None, None, ["invalid_structured_match_table_payload"]

        available_row_ids = {row["id"] for row in rows}
        available_choice_ids = {choice["id"] for choice in choices}
        choice_label_by_id = {choice["id"]: choice["label"] for choice in choices}
        legacy_pairs: dict[str, str] = {}
        for pair in normalized_pairs:
            if pair["row_id"] not in available_row_ids:
                return None, None, None, ["invalid_structured_match_row_id"]
            if pair["choice_id"] not in available_choice_ids:
                return None, None, None, ["invalid_structured_match_choice_id"]
        for row in rows:
            pair = next((item for item in normalized_pairs if item["row_id"] == row["id"]), None)
            if pair is None:
                return None, None, None, ["missing_structured_match_pair"]
            legacy_pairs[row["label"]] = choice_label_by_id[pair["choice_id"]]

        response_schema = {"kind": "match_table", "rows": rows, "choices": choices}
        autograde_rules = {"kind": "match_table", "pairs": normalized_pairs}
        legacy_options = {
            "pairs": [{"left": row["label"], "right": legacy_pairs[row["label"]]} for row in rows],
            "choices": [choice["label"] for choice in choices],
        }
        legacy_answers = {"pairs": legacy_pairs}
        return response_schema, autograde_rules, {"options_json": legacy_options, "correct_answer_json": legacy_answers}, []

    row_items: list[str] = []
    for block in question.get("content_blocks_json", []):
        if block.get("type") == "list_block" and block.get("items"):
            row_items = [normalize_text(item) for item in block.get("items", []) if normalize_text(item)]
            if row_items:
                break

    choice_pairs = extract_lettered_choices(question)
    raw_mapping = parse_match_pairs(question.get("correct_answer_json", {}).get("raw", ""))

    if not row_items or not choice_pairs or not raw_mapping:
        return None, None, None, ["unable_to_build_match_table_schema"]

    rows = [{"id": f"row{i}", "label": label} for i, label in enumerate(row_items, start=1)]
    choices = [{"id": key.lower(), "label": label} for key, label in choice_pairs]
    available_choice_ids = {choice["id"] for choice in choices}

    normalized_pairs: list[dict] = []
    legacy_pairs: dict[str, str] = {}
    choice_label_by_id = {choice["id"]: choice["label"] for choice in choices}

    for idx, row in enumerate(rows, start=1):
        target = raw_mapping.get(str(idx)) or raw_mapping.get(row["label"].upper())
        if not target:
            return None, None, None, ["unable_to_map_match_answer_rows"]
        choice_id = target.lower()
        if choice_id not in available_choice_ids:
            return None, None, None, ["unable_to_map_match_answer_choices"]
        normalized_pairs.append({"row_id": row["id"], "choice_id": choice_id})
        legacy_pairs[row["label"]] = choice_label_by_id[choice_id]

    response_schema = {"kind": "match_table", "rows": rows, "choices": choices}
    autograde_rules = {"kind": "match_table", "pairs": normalized_pairs}
    legacy_options = {"pairs": [{"left": row["label"], "right": legacy_pairs[row["label"]]} for row in rows], "choices": [choice["label"] for choice in choices]}
    legacy_answers = {"pairs": legacy_pairs}
    return response_schema, autograde_rules, {"options_json": legacy_options, "correct_answer_json": legacy_answers}, []


def parse_fill_gap(question: dict) -> tuple[dict | None, dict | None, dict | None, list[str]]:
    answer_payload = question.get("correct_answer_json", {})
    structured_gaps = answer_payload.get("gaps")
    if isinstance(structured_gaps, list) and structured_gaps:
        gaps = []
        gap_rules = []
        for idx, gap in enumerate(structured_gaps, start=1):
            gap_id = normalize_text(str(gap.get("id", f"gap{idx}"))) or f"gap{idx}"
            accepted_groups = gap.get("accepted_groups")
            if isinstance(accepted_groups, list) and accepted_groups:
                normalized_groups = []
                flattened_terms: list[str] = []
                for group in accepted_groups:
                    if not isinstance(group, dict):
                        return None, None, None, ["unsafe_structured_fill_gap_groups"]
                    canonical = normalize_text(group.get("canonical", ""))
                    accepted_terms = [
                        normalize_text(term)
                        for term in group.get("accepted_texts", [])
                        if normalize_text(term)
                    ]
                    if not canonical or not accepted_terms:
                        return None, None, None, ["unsafe_structured_fill_gap_groups"]
                    normalized_groups.append(
                        {
                            "canonical": canonical,
                            "accepted": accepted_terms,
                        }
                    )
                    flattened_terms.extend(accepted_terms)
                normalization_terms = flattened_terms
            else:
                accepted_terms = [
                    normalize_text(term)
                    for term in gap.get("accepted_texts", [])
                    if normalize_text(term)
                ]
                if not accepted_terms:
                    return None, None, None, ["unsafe_structured_fill_gap_terms"]
                normalized_groups = None
                normalization_terms = accepted_terms

            gaps.append({"id": gap_id, "label": f"Answer {idx}"})
            gap_rule = {
                "id": gap_id,
                "normalization": infer_normalization_mode(normalization_terms),
                "match_mode": "exact",
            }
            if normalized_groups:
                gap_rule["accepted_groups"] = normalized_groups
            else:
                gap_rule["accepted"] = normalization_terms
            gap_rules.append(gap_rule)

        response_schema = {"kind": "fill_gap", "gaps": gaps}
        autograde_rules = {
            "kind": "fill_gap",
            "gaps": gap_rules,
            "require_all": True,
            "require_distinct": bool(answer_payload.get("require_distinct")),
        }
        legacy_answers = {
            "accepted": [
                gap.get("accepted")
                or [group["canonical"] for group in gap.get("accepted_groups", [])]
                for gap in gap_rules
            ]
        }
        return response_schema, autograde_rules, {"options_json": {}, "correct_answer_json": legacy_answers}, []

    raw_answer = answer_payload.get("raw", "")
    lowered_raw = normalize_text(raw_answer).lower()
    if any(pattern in lowered_raw for pattern in RAW_PROSE_PATTERNS):
        return None, None, None, ["raw_fill_gap_answer_uses_prose_acceptance"]

    stem = question.get("stem", "")
    gap_count = max(1, len(BLANK_RE.findall(stem)))
    if ";" in raw_answer:
        parts = [normalize_text(part) for part in raw_answer.split(";") if normalize_text(part)]
    else:
        parts = [normalize_text(raw_answer)] if normalize_text(raw_answer) else []

    if not parts:
        return None, None, None, ["missing_fill_gap_answer"]

    if gap_count > 1 and len(parts) != gap_count:
        return None, None, None, ["ambiguous_multi_gap_answer"]

    if gap_count == 1 and len(parts) > 1:
        return None, None, None, ["ambiguous_single_gap_answer"]

    if gap_count > 1:
        gaps = [{"id": f"gap{i}", "label": f"Gap {i}"} for i in range(1, gap_count + 1)]
        gap_rules = []
        for gap, accepted in zip(gaps, parts):
            accepted_terms = split_simple_terms(accepted)
            if not accepted_terms:
                return None, None, None, ["unsafe_fill_gap_answer_terms"]
            gap_rules.append(
                {
                    "id": gap["id"],
                    "accepted": accepted_terms,
                    "normalization": infer_normalization_mode(accepted_terms),
                    "match_mode": "exact",
                }
            )
        response_schema = {"kind": "fill_gap", "gaps": gaps}
        autograde_rules = {"kind": "fill_gap", "gaps": gap_rules, "require_all": True}
        legacy_answers = {"accepted": parts}
    else:
        accepted_terms = answer_payload.get("accepted_texts")
        if accepted_terms:
            accepted_terms = [normalize_text(term) for term in accepted_terms if normalize_text(term)]
        else:
            accepted_terms = split_simple_terms(parts[0])
        if not accepted_terms:
            return None, None, None, ["unsafe_fill_gap_answer_terms"]
        response_schema = {"kind": "fill_gap", "gaps": [{"id": "gap1", "label": "Gap 1"}]}
        autograde_rules = {
            "kind": "fill_gap",
            "gaps": [
                {
                    "id": "gap1",
                    "accepted": accepted_terms,
                    "normalization": infer_normalization_mode(accepted_terms),
                    "match_mode": "exact",
                }
            ],
            "require_all": True,
        }
        legacy_answers = {"accepted": accepted_terms}

    return response_schema, autograde_rules, {"options_json": {}, "correct_answer_json": legacy_answers}, []


def parse_short_text(question: dict) -> tuple[dict | None, dict | None, dict | None, list[str]]:
    answer_payload = question.get("correct_answer_json", {})
    accepted_terms = answer_payload.get("accepted_texts")
    if accepted_terms:
        accepted_terms = [normalize_text(term) for term in accepted_terms if normalize_text(term)]
    else:
        accepted_terms = split_simple_terms(answer_payload.get("raw", ""))
    if not accepted_terms:
        return None, None, None, ["raw_short_text_answer_uses_prose_acceptance"]

    response_schema = {
        "kind": "short_text",
        "placeholder": "Type your answer",
        "max_length": 120,
    }
    autograde_rules = {
        "kind": "accepted_terms",
        "accepted": accepted_terms,
        "normalization": infer_normalization_mode(accepted_terms),
        "match_mode": "exact",
    }
    legacy_answers = {"accepted": accepted_terms}
    return response_schema, autograde_rules, {"options_json": {}, "correct_answer_json": legacy_answers}, []


def parse_drag_drop(question: dict) -> tuple[dict | None, dict | None, dict | None, list[str]]:
    options_payload = question.get("options_json", {})
    answer_payload = question.get("correct_answer_json", {})

    if not isinstance(options_payload, dict) or not isinstance(options_payload.get("items"), list):
        return None, None, None, ["invalid_ordering_items"]
    if not isinstance(answer_payload, dict) or not isinstance(answer_payload.get("order"), list):
        return None, None, None, ["invalid_ordering_answer"]

    items = [normalize_text(item) for item in options_payload.get("items", []) if normalize_text(item)]
    correct_order = [normalize_text(item) for item in answer_payload.get("order", []) if normalize_text(item)]
    if len(items) < 3 or len(items) != len(correct_order):
        return None, None, None, ["invalid_ordering_item_count"]
    if Counter(item.lower() for item in items) != Counter(item.lower() for item in correct_order):
        return None, None, None, ["ordering_answer_does_not_match_items"]

    runtime_items = [{"id": stable_item_id(item), "label": item} for item in items]
    correct_item_ids = [stable_item_id(item) for item in correct_order]
    response_schema = {"kind": "ordering", "items": runtime_items}
    autograde_rules = {"kind": "ordering", "correct_item_ids": correct_item_ids}
    legacy_payload = {
        "options_json": {"items": items},
        "correct_answer_json": {"order": correct_order},
    }
    return response_schema, autograde_rules, legacy_payload, []


def map_source_type(source_kind: str) -> str:
    if source_kind in {"past_paper", "mark_scheme"}:
        return "adapted_exam"
    return "new_original"


def map_source_role(source_kind: str) -> str:
    if source_kind == "past_paper":
        return "prompt"
    if source_kind == "mark_scheme":
        return "mark_scheme"
    if source_kind == "fact_file":
        return "fact_support"
    return "practice_model"


def build_runtime_entry(question: dict, linked_assets: list[dict]) -> tuple[dict | None, list[str]]:
    reasons: list[str] = []
    runtime_format = question.get("format", "")
    if runtime_format == "structured_response":
        reasons.append("unsupported_format_structured_response")
        return None, reasons

    if runtime_format not in SUPPORTED_LIVE_FORMATS:
        reasons.append(f"unsupported_format:{runtime_format}")
        return None, reasons

    if runtime_format == "mcq":
        response_schema, autograde_rules, legacy_payload, parse_reasons = parse_mcq(question)
    elif runtime_format == "true_false":
        response_schema, autograde_rules, legacy_payload, parse_reasons = parse_true_false(question)
    elif runtime_format == "match_table":
        response_schema, autograde_rules, legacy_payload, parse_reasons = parse_match_table(question)
    elif runtime_format == "fill_gap":
        response_schema, autograde_rules, legacy_payload, parse_reasons = parse_fill_gap(question)
    elif runtime_format == "short_text":
        response_schema, autograde_rules, legacy_payload, parse_reasons = parse_short_text(question)
    elif runtime_format == "drag_drop":
        response_schema, autograde_rules, legacy_payload, parse_reasons = parse_drag_drop(question)
    else:
        response_schema = autograde_rules = legacy_payload = None
        parse_reasons = [f"unsupported_format:{runtime_format}"]

    if parse_reasons:
        return None, parse_reasons

    payload = {
        "question_external_id": question["question_external_id"],
        "topic_slug": question["topic_slug"],
        "difficulty": question["difficulty"],
        "format": runtime_format,
        "adaptive_tier": question["adaptive_tier"],
        "question_family_code": question.get("question_family_code"),
        "selection_weight": question.get("selection_weight", 1.0),
        "stem": question["stem"],
        "options_json": legacy_payload["options_json"],
        "correct_answer_json": legacy_payload["correct_answer_json"],
        "markscheme_points_json": question.get("markscheme_points_json", []),
        "explanation": question["explanation"],
        "max_marks": question.get("max_marks", 1),
        "content_blocks_json": normalize_prompt_blocks(question.get("content_blocks_json", [])),
        "response_schema_json": response_schema,
        "autograde_rules_json": autograde_rules,
        "tags_json": question.get("tags_json", []),
        "source_type": map_source_type(question.get("source_kind", "")),
        "source_ref": question.get("source_locator", ""),
        "teacher_notes": question.get("teacher_notes", ""),
        "metadata_json": {
            "question_external_id": question["question_external_id"],
            "source_kind": question.get("source_kind"),
            "source_title": question.get("source_title"),
            "source_file_name": question.get("source_file_name"),
            "source_locator": question.get("source_locator"),
            "dedupe_fingerprint": question.get("dedupe_fingerprint"),
            "review_priority": question.get("metadata_json", {}).get("review_priority"),
        },
        "asset_count": len(linked_assets),
    }
    return payload, []


def determine_rejection_reasons(question: dict, linked_assets: list[dict], defect_map: dict[str, list[str]], allowed_statuses: set[str]) -> list[str]:
    reasons: list[str] = []
    status = question.get("staging_status", "")
    if status not in allowed_statuses:
        reasons.append(f"staging_status_not_allowed:{status}")

    explanation = normalize_text(question.get("explanation", ""))
    if not explanation:
        reasons.append("missing_explanation")

    flags = get_review_flags(question)
    if "needs_explanation_enrichment" in flags:
        reasons.append("flag_needs_explanation_enrichment")
    if "needs_objective_mapping" in flags:
        reasons.append("flag_needs_objective_mapping")
    if "needs_autograde_rule_review" in flags:
        reasons.append("flag_needs_autograde_rule_review")
    if "needs_structured_answer_normalization" in flags:
        reasons.append("flag_needs_structured_answer_normalization")
    if "misclassified_true_false" in flags:
        reasons.append("flag_misclassified_true_false")
    if not question.get("objective_codes_json"):
        reasons.append("missing_objective_codes")

    if has_unresolved_assets(linked_assets):
        reasons.append("unresolved_prompt_asset")

    defect_codes = defect_map.get(question["question_external_id"], [])
    for code in defect_codes:
        reasons.append(f"open_defect:{code}")

    return reasons


def build_payload(staging_payload: dict, defect_map: dict[str, list[str]], allowed_statuses: set[str]) -> dict:
    assets_by_question = group_assets_by_question(staging_payload)
    promoted_questions: list[dict] = []
    question_objectives: list[dict] = []
    question_assets: list[dict] = []
    question_asset_links: list[dict] = []
    question_source_links: list[dict] = []
    rejected_questions: list[dict] = []
    promoted_source_questions: list[dict] = []

    reason_counts: Counter[str] = Counter()
    topic_promoted_counts: Counter[str] = Counter()
    topic_rejected_counts: Counter[str] = Counter()
    promoted_format_counts: Counter[str] = Counter()

    seen_asset_external_ids: set[str] = set()

    for question in staging_payload.get("staged_questions", []):
        linked_assets = assets_by_question.get(question["question_external_id"], [])
        reasons = determine_rejection_reasons(question, linked_assets, defect_map, allowed_statuses)

        if not reasons:
            runtime_payload, parse_reasons = build_runtime_entry(question, linked_assets)
            reasons.extend(parse_reasons)
        else:
            runtime_payload = None

        if reasons:
            topic_rejected_counts[question["topic_slug"]] += 1
            for reason in reasons:
                reason_counts[reason] += 1
            rejected_questions.append(
                {
                    "question_external_id": question["question_external_id"],
                    "topic_slug": question["topic_slug"],
                    "format": question["format"],
                    "staging_status": question["staging_status"],
                    "review_flags": get_review_flags(question),
                    "reasons": sorted(set(reasons)),
                }
            )
            continue

        assert runtime_payload is not None
        promoted_questions.append(runtime_payload)
        promoted_source_questions.append(question)
        topic_promoted_counts[question["topic_slug"]] += 1
        promoted_format_counts[runtime_payload["format"]] += 1

        for display_order, objective_code in enumerate(question.get("objective_codes_json", []), start=1):
            question_objectives.append(
                {
                    "question_external_id": question["question_external_id"],
                    "objective_code": objective_code,
                    "is_primary": display_order == 1,
                    "display_order": display_order,
                }
            )

        for asset in linked_assets:
            asset_external_id = asset["asset_external_id"]
            if asset_external_id not in seen_asset_external_ids:
                seen_asset_external_ids.add(asset_external_id)
                question_assets.append(
                    {
                        "asset_external_id": asset_external_id,
                        "asset_kind": asset["asset_kind"],
                        "storage_bucket": asset["storage_bucket"],
                        "storage_path": asset["storage_path"],
                        "mime_type": asset.get("mime_type"),
                        "alt_text": asset["alt_text"],
                        "caption": asset.get("caption"),
                        "source_name": asset.get("original_file_name"),
                        "source_locator": asset.get("source_locator"),
                        "metadata_json": asset.get("metadata_json", {}),
                    }
                )

            question_asset_links.append(
                {
                    "question_external_id": question["question_external_id"],
                    "asset_external_id": asset_external_id,
                    "asset_role": asset["asset_role"],
                    "display_order": asset["display_order"],
                    "block_key": asset.get("block_key"),
                }
            )

    source_records, source_key_map = build_content_sources(promoted_source_questions)
    for question in promoted_source_questions:
        source_key = (
            question.get("topic_slug", ""),
            question.get("source_kind", ""),
            question.get("source_title", ""),
            question.get("source_file_name", ""),
            question.get("source_locator", ""),
        )
        question_source_links.append(
            {
                "question_external_id": question["question_external_id"],
                "content_source_external_id": source_key_map[source_key],
                "source_role": map_source_role(question.get("source_kind", "")),
                "note": question.get("source_locator", ""),
            }
        )

    summary = {
        "staged_question_count": len(staging_payload.get("staged_questions", [])),
        "promoted_question_count": len(promoted_questions),
        "rejected_question_count": len(rejected_questions),
        "promoted_format_counts": dict(promoted_format_counts),
        "topic_promoted_counts": dict(topic_promoted_counts),
        "topic_rejected_counts": dict(topic_rejected_counts),
        "rejection_reason_counts": dict(reason_counts),
        "question_asset_count": len(question_assets),
        "question_asset_link_count": len(question_asset_links),
        "question_objective_link_count": len(question_objectives),
        "question_source_link_count": len(question_source_links),
    }

    return {
        "promotion_policy": {
            "allowed_staging_statuses": sorted(allowed_statuses),
            "supported_live_formats": sorted(SUPPORTED_LIVE_FORMATS),
            "defect_register": str(DEFAULT_DEFECTS),
            "requires_explanation": True,
            "requires_objective_mapping": True,
        },
        "content_sources": source_records,
        "live_questions": promoted_questions,
        "question_objectives": question_objectives,
        "question_assets": question_assets,
        "question_asset_links": question_asset_links,
        "question_source_links": question_source_links,
        "rejected_questions": rejected_questions,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--defects", type=Path, default=DEFAULT_DEFECTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--allow-status", action="append", default=None, help="Allow additional staging statuses for controlled dry runs.")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    staging_payload = load_json(args.input)
    defect_map = parse_defect_register(args.defects)
    allowed_statuses = set(ALLOWED_STAGING_STATUSES)
    for status in args.allow_status or []:
        cleaned = normalize_text(status)
        if cleaned:
            allowed_statuses.add(cleaned)

    payload = build_payload(staging_payload, defect_map, allowed_statuses)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
