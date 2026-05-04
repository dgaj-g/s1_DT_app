#!/usr/bin/env python3
"""Apply teacher review decisions and build a safe approved live payload.

This is the gate between the teacher review CSV and anything student-facing.
It deliberately treats blank review decisions as "not approved yet". A question
can only reach the live payload if the teacher review CSV explicitly approves it
and the existing Phase 1 promotion checks still accept its runtime shape.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_phase1_live_payload import (  # noqa: E402
    DEFAULT_DEFECTS,
    build_payload as build_live_payload,
    parse_defect_register,
)


DEFAULT_STAGING_PAYLOAD = REPO_ROOT / "supabase" / "imports" / "unit1_stage4_staging_payload.json"
DEFAULT_REVIEW_CSV = REPO_ROOT / "docs" / "unit1-teacher-question-review.csv"
DEFAULT_APPROVED_STAGING = REPO_ROOT / "supabase" / "imports" / "unit1_stage5_approved_staging_payload.json"
DEFAULT_APPROVED_LIVE = REPO_ROOT / "supabase" / "imports" / "unit1_stage5_approved_live_payload.json"
DEFAULT_SUMMARY_JSON = REPO_ROOT / "docs" / "unit1-stage5-approval-summary.json"
DEFAULT_SUMMARY_CSV = REPO_ROOT / "docs" / "unit1-stage5-approval-bucket-summary.csv"
DEFAULT_REPORT_MD = REPO_ROOT / "docs" / "stage-5-approval-gate-2026-05-04.md"

DIFFICULTIES = ("easy", "medium", "expert")
DECISION_COLUMN = "teacher_decision"
COMMENT_COLUMN = "teacher_comment"
ID_COLUMN = "question_external_id"

APPROVE_DECISIONS = {
    "approve",
    "approved",
    "accept",
    "accepted",
    "yes",
    "y",
    "use",
    "use in student sessions",
    "student ready",
    "live",
}
REJECT_DECISIONS = {
    "reject",
    "rejected",
    "remove",
    "no",
    "n",
    "do not use",
    "do not use in student sessions",
    "exclude",
}
EDIT_DECISIONS = {
    "edit",
    "needs edit",
    "needs_edit",
    "revise",
    "revision needed",
    "hold",
    "draft",
    "needs checking",
    "query",
}
BLANK_DECISIONS = {"", "undecided", "pending", "review", "to review", "not reviewed"}


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def normalize_decision(value: Any) -> str:
    text = normalize_text(value).lower()
    text = text.replace("-", " ").replace("_", " ")
    return " ".join(text.split())


def classify_decision(value: Any) -> str:
    decision = normalize_decision(value)
    if decision in APPROVE_DECISIONS:
        return "approved"
    if decision in REJECT_DECISIONS:
        return "rejected"
    if decision in EDIT_DECISIONS:
        return "needs_edit"
    if decision in BLANK_DECISIONS:
        return "undecided"
    return "invalid"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_review_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        required = {ID_COLUMN, DECISION_COLUMN, COMMENT_COLUMN}
        missing = sorted(required - set(fieldnames))
        if missing:
            raise ValueError(f"Review CSV missing required columns: {', '.join(missing)}")
        return list(reader)


def collect_decisions(review_rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], list[str]]:
    decisions: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    seen_rows: dict[str, int] = {}

    for index, row in enumerate(review_rows, start=2):
        external_id = normalize_text(row.get(ID_COLUMN))
        raw_decision = normalize_text(row.get(DECISION_COLUMN))
        comment = normalize_text(row.get(COMMENT_COLUMN))
        if not external_id:
            errors.append(f"row {index}: missing {ID_COLUMN}")
            continue
        if external_id in decisions:
            previous = seen_rows[external_id]
            errors.append(f"row {index}: duplicate {ID_COLUMN} also seen on row {previous}: {external_id}")
            continue

        status = classify_decision(raw_decision)
        if status == "invalid":
            errors.append(
                f"row {index}: invalid teacher_decision {raw_decision!r} for {external_id}. "
                "Use approve, reject, needs edit, or leave blank."
            )

        decisions[external_id] = {
            "decision": status,
            "raw_decision": raw_decision,
            "teacher_comment": comment,
            "review_csv_row": str(index),
        }
        seen_rows[external_id] = index

    return decisions, errors


def decision_to_staging_status(decision: str) -> str:
    if decision == "approved":
        return "approved"
    if decision == "rejected":
        return "rejected"
    if decision == "needs_edit":
        return "draft"
    return "ready_for_review"


def annotate_question(question: dict[str, Any], decision: dict[str, str]) -> dict[str, Any]:
    updated = deepcopy(question)
    decision_status = decision["decision"]
    updated["staging_status"] = decision_to_staging_status(decision_status)

    metadata = updated.get("metadata_json")
    if not isinstance(metadata, dict):
        metadata = {}
    metadata = deepcopy(metadata)
    metadata["teacher_review"] = {
        "decision": decision_status,
        "raw_decision": decision["raw_decision"],
        "teacher_comment": decision["teacher_comment"],
        "review_csv_row": decision["review_csv_row"],
        "applied_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    updated["metadata_json"] = metadata

    if decision["teacher_comment"]:
        existing_notes = normalize_text(updated.get("teacher_notes"))
        comment_note = f"Teacher review comment: {decision['teacher_comment']}"
        updated["teacher_notes"] = f"{existing_notes} | {comment_note}" if existing_notes else comment_note

    return updated


def bucket_counts(questions: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {difficulty: 0 for difficulty in DIFFICULTIES})
    for question in questions:
        topic = normalize_text(question.get("topic_slug"))
        difficulty = normalize_text(question.get("difficulty")).lower()
        if topic and difficulty in DIFFICULTIES:
            counts[topic][difficulty] += 1
    return {topic: dict(values) for topic, values in sorted(counts.items())}


def summarize_buckets(
    all_questions: list[dict[str, Any]],
    approved_questions: list[dict[str, Any]],
    min_per_bucket: int,
) -> list[dict[str, Any]]:
    all_counts = bucket_counts(all_questions)
    approved_counts = bucket_counts(approved_questions)
    rows: list[dict[str, Any]] = []
    for topic in sorted(all_counts):
        for difficulty in DIFFICULTIES:
            all_count = all_counts.get(topic, {}).get(difficulty, 0)
            approved_count = approved_counts.get(topic, {}).get(difficulty, 0)
            rows.append(
                {
                    "topic_slug": topic,
                    "difficulty": difficulty,
                    "available_for_review": all_count,
                    "approved": approved_count,
                    "minimum_for_10_question_session": min_per_bucket,
                    "session_ready": "yes" if approved_count >= min_per_bucket else "no",
                }
            )
    return rows


def write_bucket_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "topic_slug",
        "difficulty",
        "available_for_review",
        "approved",
        "minimum_for_10_question_session",
        "session_ready",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def build_approved_staging_payload(
    staging_payload: dict[str, Any],
    decisions: dict[str, dict[str, str]],
    source_staging_payload: Path,
    source_review_csv: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    staged_questions = staging_payload.get("staged_questions", [])
    if not isinstance(staged_questions, list):
        raise ValueError("Staging payload staged_questions must be a list")

    staged_ids = {question["question_external_id"] for question in staged_questions}
    decision_ids = set(decisions)
    unknown_decision_ids = sorted(decision_ids - staged_ids)

    annotated_questions: list[dict[str, Any]] = []
    approved_questions: list[dict[str, Any]] = []
    included_question_ids: set[str] = set()
    decision_counts: Counter[str] = Counter()
    topic_decision_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for question in staged_questions:
        external_id = question["question_external_id"]
        decision = decisions.get(
            external_id,
            {
                "decision": "undecided",
                "raw_decision": "",
                "teacher_comment": "",
                "review_csv_row": "",
            },
        )
        annotated = annotate_question(question, decision)
        annotated_questions.append(annotated)
        decision_counts[decision["decision"]] += 1
        topic_decision_counts[question["topic_slug"]][decision["decision"]] += 1
        if decision["decision"] == "approved":
            approved_questions.append(annotated)
            included_question_ids.add(external_id)

    approved_assets = [
        deepcopy(asset)
        for asset in staging_payload.get("staged_question_assets", [])
        if asset.get("question_external_id") in included_question_ids
    ]

    import_batch = deepcopy(staging_payload.get("import_batch", {}))
    metadata = import_batch.get("metadata_json")
    if not isinstance(metadata, dict):
        metadata = {}
    metadata = deepcopy(metadata)
    metadata["stage5_approval"] = {
        "source_review_csv": str(source_review_csv),
        "approved_question_count": len(approved_questions),
        "decision_counts": dict(decision_counts),
        "applied_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    import_batch["metadata_json"] = metadata
    import_batch["batch_label"] = f"{import_batch.get('batch_label', 'unit1')}-approved-only"
    import_batch["batch_status"] = "approved"
    import_batch["notes"] = normalize_text(import_batch.get("notes")) + " Stage 5 approval gate applied."

    approved_payload = {
        "import_batch": import_batch,
        "staged_questions": approved_questions,
        "staged_question_assets": approved_assets,
        "approval_audit": {
            "source_staging_payload": str(source_staging_payload),
            "source_review_csv": str(source_review_csv),
            "unknown_decision_ids": unknown_decision_ids,
            "decision_counts": dict(decision_counts),
            "topic_decision_counts": {topic: dict(counter) for topic, counter in sorted(topic_decision_counts.items())},
            "source_question_count": len(staged_questions),
            "approved_question_count": len(approved_questions),
            "approved_asset_count": len(approved_assets),
        },
    }

    annotated_all_payload = {
        "import_batch": import_batch,
        "staged_questions": annotated_questions,
        "staged_question_assets": deepcopy(staging_payload.get("staged_question_assets", [])),
    }

    audit = {
        "unknown_decision_ids": unknown_decision_ids,
        "decision_counts": dict(decision_counts),
        "topic_decision_counts": {topic: dict(counter) for topic, counter in sorted(topic_decision_counts.items())},
        "source_question_count": len(staged_questions),
        "approved_question_count": len(approved_questions),
        "approved_asset_count": len(approved_assets),
        "annotated_all_payload": annotated_all_payload,
    }
    return approved_payload, audit


def build_markdown_report(summary: dict[str, Any], bucket_rows: list[dict[str, Any]]) -> str:
    decision_counts = summary["decision_counts"]
    live_summary = summary["live_payload_summary"]
    not_ready_rows = [row for row in bucket_rows if row["session_ready"] == "no"]

    lines = [
        "# Stage 5 Approval Gate Report (2026-05-04)",
        "",
        "## Purpose",
        "This report checks whether teacher review decisions can safely become student-facing questions.",
        "",
        "Blank teacher decisions are deliberately treated as not approved. This prevents unreviewed questions from leaking into student sessions.",
        "",
        "## Decision Summary",
        f"- Source staged questions: {summary['source_question_count']}",
        f"- Approved by teacher review CSV: {summary['approved_question_count']}",
        f"- Rejected: {decision_counts.get('rejected', 0)}",
        f"- Needs edit / held as draft: {decision_counts.get('needs_edit', 0)}",
        f"- Undecided / blank: {decision_counts.get('undecided', 0)}",
        f"- Invalid decisions: {decision_counts.get('invalid', 0)}",
        "",
        "## Live Payload Summary",
        f"- Promoted into live runtime payload: {live_summary.get('promoted_question_count', 0)}",
        f"- Rejected by runtime checks: {live_summary.get('rejected_question_count', 0)}",
        f"- Linked question assets: {live_summary.get('question_asset_count', 0)}",
        f"- Linked objectives: {live_summary.get('question_objective_link_count', 0)}",
        "",
        "## Session Readiness",
        f"- Minimum per topic/difficulty bucket used for this check: {summary['min_per_bucket']}",
        f"- Buckets below minimum after approval: {len(not_ready_rows)}",
        "",
    ]

    if not_ready_rows:
        lines.extend(
            [
                "The buckets below the minimum are expected until enough questions are explicitly approved.",
                "",
                "| Topic | Difficulty | Approved | Available For Review |",
                "|---|---:|---:|---:|",
            ]
        )
        for row in not_ready_rows:
            lines.append(
                f"| {row['topic_slug']} | {row['difficulty']} | {row['approved']} | {row['available_for_review']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Outputs",
            f"- Approved staging payload: `{summary['approved_staging_payload']}`",
            f"- Approved live payload: `{summary['approved_live_payload']}`",
            f"- JSON summary: `{summary['summary_json']}`",
            f"- Bucket CSV: `{summary['bucket_csv']}`",
            "",
            "## Safety Position",
            "This script does not write to Supabase. It only creates local payload files. Remote import/deployment remains a separate deliberate step.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-payload", type=Path, default=DEFAULT_STAGING_PAYLOAD)
    parser.add_argument("--review-csv", type=Path, default=DEFAULT_REVIEW_CSV)
    parser.add_argument("--defects", type=Path, default=DEFAULT_DEFECTS)
    parser.add_argument("--approved-staging-output", type=Path, default=DEFAULT_APPROVED_STAGING)
    parser.add_argument("--approved-live-output", type=Path, default=DEFAULT_APPROVED_LIVE)
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY_CSV)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--min-per-bucket", type=int, default=10)
    parser.add_argument("--fail-on-invalid", action="store_true")
    parser.add_argument("--fail-on-empty-approved", action="store_true")
    parser.add_argument("--fail-on-underfilled-buckets", action="store_true")
    parser.add_argument(
        "--allow-live-rejections",
        action="store_true",
        help="Do not fail if approved questions are rejected by the strict runtime promotion checks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    staging_payload = load_json(args.staging_payload)
    review_rows = load_review_rows(args.review_csv)
    decisions, decision_errors = collect_decisions(review_rows)

    approved_staging_payload, approval_audit = build_approved_staging_payload(
        staging_payload,
        decisions,
        args.staging_payload,
        args.review_csv,
    )
    unknown_decision_ids = approval_audit["unknown_decision_ids"]
    validation_errors = decision_errors + [
        f"review CSV contains unknown question_external_id: {external_id}" for external_id in unknown_decision_ids
    ]

    defect_map = parse_defect_register(args.defects)
    live_payload = build_live_payload(approved_staging_payload, defect_map, {"approved"})

    approved_questions = approved_staging_payload["staged_questions"]
    bucket_rows = summarize_buckets(
        staging_payload.get("staged_questions", []),
        approved_questions,
        args.min_per_bucket,
    )
    underfilled = [row for row in bucket_rows if row["session_ready"] == "no"]

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_staging_payload": str(args.staging_payload),
        "source_review_csv": str(args.review_csv),
        "approved_staging_payload": str(args.approved_staging_output),
        "approved_live_payload": str(args.approved_live_output),
        "summary_json": str(args.summary_json),
        "bucket_csv": str(args.summary_csv),
        "report_md": str(args.report_md),
        "source_question_count": approval_audit["source_question_count"],
        "approved_question_count": approval_audit["approved_question_count"],
        "approved_asset_count": approval_audit["approved_asset_count"],
        "decision_counts": approval_audit["decision_counts"],
        "topic_decision_counts": approval_audit["topic_decision_counts"],
        "validation_errors": validation_errors,
        "min_per_bucket": args.min_per_bucket,
        "underfilled_bucket_count": len(underfilled),
        "underfilled_buckets": underfilled,
        "live_payload_summary": live_payload["summary"],
        "live_rejection_reason_counts": live_payload["summary"].get("rejection_reason_counts", {}),
    }

    write_json(args.approved_staging_output, approved_staging_payload)
    write_json(args.approved_live_output, live_payload)
    write_json(args.summary_json, summary)
    write_bucket_csv(args.summary_csv, bucket_rows)
    args.report_md.parent.mkdir(parents=True, exist_ok=True)
    args.report_md.write_text(build_markdown_report(summary, bucket_rows), encoding="utf-8")

    print(f"Wrote approved staging payload to {args.approved_staging_output}")
    print(f"Wrote approved live payload to {args.approved_live_output}")
    print(f"Wrote approval summary to {args.summary_json}")
    print(json.dumps({
        "source_question_count": summary["source_question_count"],
        "approved_question_count": summary["approved_question_count"],
        "decision_counts": summary["decision_counts"],
        "live_payload_summary": summary["live_payload_summary"],
        "underfilled_bucket_count": summary["underfilled_bucket_count"],
        "validation_error_count": len(validation_errors),
    }, indent=2))

    should_fail = False
    if args.fail_on_invalid and validation_errors:
        should_fail = True
    if args.fail_on_empty_approved and not approved_questions:
        should_fail = True
    if args.fail_on_underfilled_buckets and underfilled:
        should_fail = True
    if (
        approved_questions
        and not args.allow_live_rejections
        and live_payload["summary"].get("rejected_question_count", 0) > 0
    ):
        should_fail = True

    if should_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
