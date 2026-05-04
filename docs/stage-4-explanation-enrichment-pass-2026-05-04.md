# Stage 4 Explanation Enrichment Pass - 2026-05-04

## Purpose

This pass adds a first student-facing teaching explanation to every staged
question without treating those questions as approved for student use.

The aim is to move the bank from empty feedback to a reviewable baseline:

- show the expected answer clearly;
- connect the answer to the mapped learning objective;
- keep transformed and practice-bank review flags visible; and
- preserve the owner approval boundary before anything can go live.

## Files changed

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`

## What changed

The import bundle builder now generates a first-pass explanation from:

- the normalized correct answer;
- the question format;
- the mark-scheme points where available; and
- the first one or two mapped learning objectives.

Examples:

- MCQ: names the correct option, then links it to the objective.
- Match table: lists the correct pairings, then links them to the objective.
- Fill-gap / short-text: states an accepted answer, then links it to the objective.
- Ordering: lists the correct order, then links it to the objective.

## Objective-mapping refinements

The explanation pass exposed a few objective-mapping slips, so the mapper was
tightened before accepting the new explanation baseline.

Improvements included:

- MCQ objective inference now sees the correct option text, not just the answer
  letter.
- Router/switch/NIC/file-server signals are prioritised for Network
  Technologies device questions.
- Cloud-risk prompts are prioritised toward cloud disadvantages.
- GPS privacy/use prompts are prioritised toward the correct GPS objectives.
- The broad `act` signal was removed from legal cleanup logic because it could
  falsely match words such as `fact`.

## Verified rebuild result

After sequentially rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

the staging payload reports:

- `question_count`: `904`
- `asset_count`: `29`
- `needs_explanation_enrichment`: removed from `flag_counts`
- `needs_objective_mapping`: `0`
- `needs_autograde_rule_review`: `0`
- `known_content_defect`: `0`
- `ready_for_review_count`: `904`
- `draft_count`: `0`

Remaining review flags:

- `transformed_exam_item`: `263`
- `supplementary_derived_item`: `6`
- `practice_question_needs_source_normalization`: `483`

## Promotion boundary check

The Phase 1 live-payload bridge was run after the explanation pass.

Result:

- `904` staged questions
- `0` promoted
- `904` rejected

Only rejection reason:

- `staging_status_not_allowed:ready_for_review`

This is correct. The bank is now ready for teacher/content-owner review, but no
question is live until it is explicitly marked `approved`.

## Technical promotion dry run

A separate dry run allowed `ready_for_review` status temporarily, only to test
whether the runtime bridge could parse every review-ready question.

Initial dry-run issues found:

- multi-row true/false questions needed to be promoted as `match_table` with
  True/False choices;
- one database short-answer prompt was incorrectly detected as an ordering
  question because it contained the phrase `ascending order`.

Fixes made:

- multi-statement true/false items now normalize to structured match tables;
- single true/false items remain `true_false`;
- ordering detection now requires an explicit ordering instruction such as
  `place the following`, `arrange the following`, `put the following`, or
  `correct order`;
- the promotion bridge accepts structured True/False match tables.

Final technical dry run:

- `904` staged
- `904` promoted
- `0` rejected

Promoted formats:

- `mcq`: `594`
- `match_table`: `80`
- `short_text`: `74`
- `fill_gap`: `90`
- `true_false`: `65`
- `drag_drop`: `1`

The strict live payload was then regenerated without allowing
`ready_for_review`, returning to:

- `0` promoted
- `904` rejected
- rejection reason: `staging_status_not_allowed:ready_for_review`

## Current interpretation

The bank has moved from structurally blocked to reviewable. This does not mean
the bank is finished.

The next trust work should focus on:

- reviewing transformed exam items for fidelity to exam demand;
- reviewing practice-bank items for source normalization;
- then approving only the questions that pass that review.
