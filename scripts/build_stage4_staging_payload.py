#!/usr/bin/env python3
"""Transform the normalized Unit 1 import bundle into staging payloads.

This script takes the output of build_stage4_import_bundle.py and produces a
review-focused payload aligned to the Stage 3 staging tables:

- import_batches
- staged_questions
- staged_question_assets

It also adds explicit review flags so questionable items are surfaced before
anything is considered ready for publication.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "supabase" / "imports" / "unit1_stage4_import_bundle.json"
DEFAULT_OUTPUT = REPO_ROOT / "supabase" / "imports" / "unit1_stage4_staging_payload.json"
DEFECT_REGISTER = REPO_ROOT / "docs" / "stage-4-content-defect-register-2026-05-03.md"

STRUCTURAL_BLOCKING_FLAGS = {
    "missing_stem",
    "invalid_mcq_option_count",
    "missing_correct_answer",
    "unresolved_prompt_asset",
    "misclassified_true_false",
}

EDITORIAL_BLOCKING_FLAGS = {
    "known_content_defect",
    "needs_autograde_rule_review",
    "needs_explanation_enrichment",
    "needs_objective_mapping",
}

REVIEW_FLAGS = {
    "known_content_defect",
    "misclassified_true_false",
    "needs_structured_answer_normalization",
    "supplementary_derived_item",
    "transformed_exam_item",
    "needs_objective_mapping",
    "needs_explanation_enrichment",
    "needs_autograde_rule_review",
    "practice_question_needs_source_normalization",
}

QUESTION_EXTERNAL_ID_RE = re.compile(
    r"`([a-z0-9-]+\.(?:past_paper|practice_bank|mark_scheme)\.[a-z0-9_]+\.q\d+)`"
)
QUESTION_SHORT_ID_RE = re.compile(r"`(q\d+)`")
BLANK_RE = re.compile(r"_{2,}")


def normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def load_bundle(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_defect_question_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    open_question_ids: set[str] = set()
    block_ids: set[str] = set()
    current_prefix: str | None = None
    current_status: str | None = None

    def flush_block() -> None:
        nonlocal block_ids, current_prefix, current_status, open_question_ids
        if not block_ids:
            current_prefix = None
            current_status = None
            return

        status_text = (current_status or "").lower()
        is_closed = (
            ("closed" in status_text or "resolved" in status_text)
            and "pending" not in status_text
        )
        if not is_closed:
            open_question_ids.update(block_ids)

        block_ids = set()
        current_prefix = None
        current_status = None

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if stripped.startswith("### "):
            flush_block()

        full_ids = QUESTION_EXTERNAL_ID_RE.findall(line)
        if full_ids:
            for full_id in full_ids:
                block_ids.add(full_id)
                current_prefix = full_id.rsplit(".q", 1)[0]
        elif current_prefix:
            for short_id in QUESTION_SHORT_ID_RE.findall(line):
                block_ids.add(f"{current_prefix}.{short_id}")

        if stripped.lower().startswith("- status:"):
            current_status = stripped.split(":", 1)[1].strip()

    flush_block()
    return open_question_ids


def collect_assets_by_question(bundle: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for asset in bundle.get("question_assets", []):
        grouped[asset["question_external_id"]].append(asset)
    return grouped


def is_transformed_exam_item(source_locator: str) -> bool:
    locator = (source_locator or "").lower()
    triggers = [
        "converted from",
        "converted to",
        "converted to mcq",
        "converted to true/false",
        "split into",
        "originally",
        "transformed",
        "rewritten as",
    ]
    return any(trigger in locator for trigger in triggers)


def is_supplementary_derived_item(source_locator: str) -> bool:
    locator = (source_locator or "").lower()
    return any(
        signal in locator
        for signal in (
            "supplementary item derived from",
            "supplementary expert balancing item",
            "supplementary medium balancing item",
        )
    )


def is_true_false_shape_misclassified(question: dict) -> bool:
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
    correct_raw = normalize_text(str(question.get("correct_answer_json", {}).get("raw", ""))).lower()
    if correct_raw not in {"true", "false"}:
        return False
    if not question.get("options_json"):
        return True
    stem = normalize_text(question.get("stem", "")).lower()
    signals = [
        "true or false",
        "state whether",
        "select whether",
        "decide whether",
        "tick true or false",
    ]
    return any(signal in stem for signal in signals)


def needs_structured_answer_normalization(question: dict) -> bool:
    format_name = question.get("format")
    correct_answer_json = question.get("correct_answer_json", {})
    correct_raw = normalize_text(str(correct_answer_json.get("raw", ""))).lower()
    accepted_texts = correct_answer_json.get("accepted_texts")

    if format_name == "fill_gap":
        structured_gaps = correct_answer_json.get("gaps")
        if isinstance(structured_gaps, list) and structured_gaps:
            if all(
                isinstance(gap, dict)
                and gap.get("id")
                and isinstance(gap.get("accepted_texts"), list)
                and gap.get("accepted_texts")
                for gap in structured_gaps
            ):
                return False

    if not correct_raw:
        return False

    prose_markers = [
        "accept:",
        "also accept",
        "any 2 from",
        "any two from",
        "any 3 from",
        "any three from",
        "do not accept",
    ]
    if any(marker in correct_raw for marker in prose_markers):
        return True

    if accepted_texts and isinstance(accepted_texts, list):
        return False

    if format_name == "match_table":
        options_payload = question.get("options_json")
        answer_pairs = correct_answer_json.get("pairs")
        if not isinstance(options_payload, dict):
            return True
        if not options_payload.get("rows") or not options_payload.get("choices"):
            return True
        if not isinstance(answer_pairs, list) or not answer_pairs:
            return True

    if format_name == "structured_response":
        return True

    return False


def has_safe_simple_autograde_shape(question: dict) -> bool:
    format_name = question.get("format")
    if format_name not in {"short_text", "fill_gap"}:
        return False

    autograde_rules = question.get("autograde_rules_json", {})
    raw_answer = normalize_text(str(autograde_rules.get("raw_answer", "")))
    if not raw_answer:
        return False

    lowered_raw = raw_answer.lower()
    prose_markers = [
        "accept:",
        "also accept",
        "any 2 from",
        "any two from",
        "any 3 from",
        "any three from",
        "do not accept",
    ]
    if any(marker in lowered_raw for marker in prose_markers):
        return False

    separator_markers = [";", " / ", ","]
    if any(marker in raw_answer for marker in separator_markers):
        return False
    if re.search(r"\bor\b", lowered_raw):
        return False
    if "(" in raw_answer or ")" in raw_answer:
        return False
    if len(raw_answer.split()) > 4:
        return False

    if format_name == "fill_gap":
        blank_count = len(BLANK_RE.findall(normalize_text(question.get("stem", ""))))
        if blank_count > 1:
            return False

    return True


def has_safe_autograde_shape(question: dict) -> bool:
    format_name = question.get("format")
    if format_name == "structured_response":
        return False

    autograde_rules = question.get("autograde_rules_json", {})
    mode = autograde_rules.get("mode")

    if mode in {"ordered_gaps", "shared_gap_pool"}:
        return True

    if mode == "accepted_texts" and format_name in {"short_text", "fill_gap"}:
        return True

    if mode == "needs_enrichment":
        return has_safe_simple_autograde_shape(question)

    return False


def derive_review_flags(
    question: dict,
    linked_assets: list[dict],
    known_defect_ids: set[str],
) -> list[str]:
    flags: list[str] = []

    stem = normalize_text(question.get("stem", ""))
    if not stem:
        flags.append("missing_stem")

    correct_answer = question.get("correct_answer_json", {}).get("raw", "")
    if not normalize_text(str(correct_answer)):
        flags.append("missing_correct_answer")

    if question.get("format") == "mcq":
        option_count = len(question.get("options_json", []))
        if option_count != 4:
            flags.append("invalid_mcq_option_count")

    if question.get("question_external_id") in known_defect_ids:
        flags.append("known_content_defect")

    if is_transformed_exam_item(question.get("source_locator", "")):
        flags.append("transformed_exam_item")

    is_supplementary = is_supplementary_derived_item(question.get("source_locator", ""))
    if is_supplementary:
        flags.append("supplementary_derived_item")

    if is_true_false_shape_misclassified(question):
        flags.append("misclassified_true_false")

    if not normalize_text(question.get("explanation", "")):
        flags.append("needs_explanation_enrichment")

    if not question.get("objective_codes_json"):
        flags.append("needs_objective_mapping")

    if question.get("format") in {"fill_gap", "short_text", "structured_response"} and not has_safe_autograde_shape(question):
        flags.append("needs_autograde_rule_review")

    if question.get("source_set") == "practice_bank" and not is_supplementary:
        flags.append("practice_question_needs_source_normalization")

    if needs_structured_answer_normalization(question):
        flags.append("needs_structured_answer_normalization")

    figure_blocks = [
        block for block in question.get("content_blocks_json", [])
        if block.get("type") == "figure"
    ]
    for block in figure_blocks:
        block_key = block.get("block_key")
        matches = [
            asset for asset in linked_assets
            if asset.get("block_key") == block_key and asset.get("asset_role") == "prompt"
        ]
        if not matches or not all(asset.get("resolved") for asset in matches):
            flags.append("unresolved_prompt_asset")
            break

    return sorted(set(flags))


def derive_review_priority(flags: list[str]) -> str:
    if any(flag in STRUCTURAL_BLOCKING_FLAGS for flag in flags):
        return "critical"
    if any(flag in EDITORIAL_BLOCKING_FLAGS for flag in flags):
        return "high"
    if "needs_autograde_rule_review" in flags or "transformed_exam_item" in flags:
        return "high"
    if any(flag in REVIEW_FLAGS for flag in flags):
        return "medium"
    return "low"


def derive_staging_status(flags: list[str]) -> str:
    if any(flag in STRUCTURAL_BLOCKING_FLAGS for flag in flags):
        return "draft"
    if any(flag in EDITORIAL_BLOCKING_FLAGS for flag in flags):
        return "draft"
    return "ready_for_review"


def derive_gate_bucket(flags: list[str], staging_status: str) -> str:
    if staging_status == "ready_for_review":
        return "review_ready"
    if any(flag in STRUCTURAL_BLOCKING_FLAGS for flag in flags):
        return "structural_draft"
    return "editorial_draft"


def build_import_batch(bundle: dict) -> dict:
    summary = bundle.get("summary", {})
    return {
        "batch_label": bundle.get("batch_label", "unit1-import-batch"),
        "source_format": "json",
        "batch_status": "uploaded",
        "source_file_name": Path(bundle.get("source_root", "")).name or "unit1-curated-source-pack",
        "notes": "Generated from the curated Unit 1 markdown and figure source pack.",
        "metadata_json": {
            "source_root": bundle.get("source_root"),
            "question_count": summary.get("question_count", 0),
            "asset_count": summary.get("asset_count", 0),
            "topic_counts": summary.get("topic_counts", {}),
        },
    }


def build_payload(bundle: dict) -> dict:
    assets_by_question = collect_assets_by_question(bundle)
    known_defect_ids = load_defect_question_ids(DEFECT_REGISTER)
    staged_questions: list[dict] = []
    staged_assets: list[dict] = []
    flag_counter: Counter[str] = Counter()
    priority_counter: Counter[str] = Counter()
    gate_bucket_counter: Counter[str] = Counter()
    topic_counter: dict[str, Counter[str]] = defaultdict(Counter)
    objective_counter: Counter[str] = Counter()

    for row_number, question in enumerate(bundle.get("questions", []), start=1):
        linked_assets = assets_by_question.get(question["question_external_id"], [])
        flags = derive_review_flags(question, linked_assets, known_defect_ids)
        priority = derive_review_priority(flags)
        staging_status = derive_staging_status(flags)
        gate_bucket = derive_gate_bucket(flags, staging_status)
        priority_counter[priority] += 1
        gate_bucket_counter[gate_bucket] += 1
        for objective_code in question.get("objective_codes_json", []):
            objective_counter[objective_code] += 1

        for flag in flags:
            flag_counter[flag] += 1
            topic_counter[question["topic_slug"]][flag] += 1

        staged_questions.append({
            "question_external_id": question["question_external_id"],
            "row_number": row_number,
            "topic_slug": question["topic_slug"],
            "topic_title": question["topic_title"],
            "difficulty": question["difficulty"],
            "format": question["format"],
            "adaptive_tier": question["adaptive_tier"],
            "question_family_code": question["question_family_code"],
            "selection_weight": question["selection_weight"],
            "stem": question["stem"],
            "options_json": question["options_json"],
            "correct_answer_json": question["correct_answer_json"],
            "markscheme_points_json": question["markscheme_points_json"],
            "explanation": question["explanation"],
            "max_marks": question["max_marks"],
            "content_blocks_json": question["content_blocks_json"],
            "response_schema_json": question["response_schema_json"],
            "autograde_rules_json": question["autograde_rules_json"],
            "objective_codes_json": question.get("objective_codes_json", []),
            "tags_json": question["tags_json"],
            "source_kind": question["source_set"],
            "source_title": question["source_title"],
            "source_file_name": question["source_file_name"],
            "source_locator": question["source_locator"],
            "teacher_notes": question.get("teacher_notes", ""),
            "review_notes": "",
            "dedupe_fingerprint": question["dedupe_fingerprint"],
            "staging_status": staging_status,
            "metadata_json": {
                "review_priority": priority,
                "review_flags": flags,
                "gate_bucket": gate_bucket,
                "question_label": question["question_label"],
                "marks_text": question["marks_text"],
                "source_set": question["source_set"],
                "qtype_label": question["qtype_label"],
            },
        })

        for asset in linked_assets:
            staged_assets.append({
                "question_external_id": question["question_external_id"],
                "asset_external_id": asset["asset_external_id"],
                "asset_kind": asset["asset_kind"],
                "asset_role": asset["asset_role"],
                "storage_bucket": "question-imports",
                "storage_path": asset["storage_path"],
                "mime_type": asset["mime_type"],
                "alt_text": asset["alt_text"],
                "caption": asset["caption"],
                "original_file_name": asset["file_name"],
                "source_locator": asset["source_locator"],
                "display_order": asset["display_order"],
                "block_key": asset["block_key"],
                "metadata_json": {
                    "resolved": asset["resolved"],
                    "source_relative_path": asset["source_relative_path"],
                },
            })

    summary = {
        "question_count": len(staged_questions),
        "asset_count": len(staged_assets),
        "flag_counts": dict(flag_counter),
        "priority_counts": dict(priority_counter),
        "gate_bucket_counts": dict(gate_bucket_counter),
        "objective_counts": dict(objective_counter),
        "objective_mapped_count": sum(1 for q in staged_questions if q["objective_codes_json"]),
        "objective_unmapped_count": sum(1 for q in staged_questions if not q["objective_codes_json"]),
        "topic_flag_counts": {topic: dict(counter) for topic, counter in topic_counter.items()},
        "ready_for_review_count": sum(1 for q in staged_questions if q["staging_status"] == "ready_for_review"),
        "draft_count": sum(1 for q in staged_questions if q["staging_status"] == "draft"),
    }

    return {
        "import_batch": build_import_batch(bundle),
        "staged_questions": staged_questions,
        "staged_question_assets": staged_assets,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    bundle = load_bundle(args.input)
    payload = build_payload(bundle)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
