# Stage 4 Accuracy Gate

This document defines the review gate between:

- normalized source extraction
- staged database import

The app must not behave as if all parsed questions are equally ready for
students. This gate exists because question accuracy is critical to exam
preparation.

## Principle

The importer should be generous in what it can parse, but strict in what it
allows to move forward without review.

That means:

- parsing can be broad
- staging can be broad
- publication must be strict

## Current Transformer

Current Stage 4 transformer:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

It reads the normalized bundle and adds review intelligence:

- review flags
- review priority
- staging status

## Staging Status Meanings

### `draft`

The item should not be treated as clean review-ready content yet.

Reasons include:

- unresolved prompt assets
- invalid MCQ option structure
- missing stem
- missing correct answer
- missing explanation
- unresolved objective mapping
- open defect-register items
- unsafe open-answer normalization
- known misclassified true/false items

### `ready_for_review`

The item is structurally and editorially shaped well enough to enter a serious
teacher/content review step before any future publish step.

This does **not** mean “student-ready”.

It means:

- no hard structural blocker found;
- no core editorial blocker found;
- any remaining flags are lower-risk review issues rather than known trust
  defects.

## Current Baseline After Tightening (2026-05-04)

After hardening the staging gate and regenerating the payload from the real Unit
1 source pack, the current summary is:

- `904` questions staged
- `29` prompt assets staged
- `0` `ready_for_review`
- `904` `draft`

Gate-bucket split:

- `904` `editorial_draft`

This is an intentionally stricter and more honest result than before.

The earlier version said all `904` questions were `ready_for_review`, which was
misleading because the bank still had:

- no student-facing explanations;
- unresolved objective gaps;
- known audited defects;
- unsafe open-answer grading shapes; and
- repeated true/false misclassification.

Those gap categories have now been reduced substantially:

- `known_content_defect`: `0`
- `needs_objective_mapping`: `0`
- `needs_autograde_rule_review`: `0`

The bank is still correctly blocked because:

- `transformed_exam_item`: `263`
- `practice_question_needs_source_normalization`: `483`

After the explanation-enrichment pass, the bank is no longer blocked by empty
feedback. All questions now have a first-pass explanation and are
`ready_for_review`, but they are not approved for live student use.

## Current Review Flags

### Structural blocking flags

- `missing_stem`
- `invalid_mcq_option_count`
- `missing_correct_answer`
- `unresolved_prompt_asset`
- `misclassified_true_false`

If any structural blocking flag is present, the item stays in `draft` and is
tagged internally as `structural_draft`.

### Editorial blocking flags

- `known_content_defect`
- `needs_autograde_rule_review`
- `needs_explanation_enrichment`
- `needs_objective_mapping`

If any editorial blocking flag is present, the item stays in `draft` and is
tagged internally as `editorial_draft`.

### Review flags

- `known_content_defect`
- `misclassified_true_false`
- `needs_structured_answer_normalization`
- `supplementary_derived_item`
- `transformed_exam_item`
- `needs_objective_mapping`
- `needs_explanation_enrichment`
- `needs_autograde_rule_review`
- `practice_question_needs_source_normalization`

These do not block staging, but they are signals that the question still needs
content-quality work.

## Why These Flags Matter

### `transformed_exam_item`

This identifies questions that were adapted from a longer or different original
format, for example:

- split from a multi-mark question
- converted to MCQ
- otherwise transformed for auto-marking

These questions are often useful, but they need more scrutiny because the
transformation itself can introduce ambiguity or oversimplification.

The detector was tightened on 2026-05-03 to catch a broader range of source
locator wording, including:

- `converted from`
- `converted to`
- `rewritten as`
- `supplementary item derived from ...`

That raised the transformed-item count from `181` to `263`, which is a more
honest reflection of how much rewritten content is in the bank.

### `known_content_defect`

This flag is driven from:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`

If an imported item appears in the audited defect register, it must not be
treated as review-ready until the defect is resolved and the register is
updated.

### `misclassified_true_false`

This identifies the repeated pipeline defect where a single True/False judgment
has been staged as `match_table`.

This is a structural blocker because it distorts both rendering and later
grading expectations.

### `needs_objective_mapping`

Objective-level analytics and adaptive support depend on trustworthy objective
mapping. Until that is added, the question should be considered incomplete for
the full rebuilt model.

After the first objective-mapping pass, this flag should now be interpreted as:

- a genuine unresolved case
- an item that still needs better objective evidence
- not just a default placeholder on every question

### `needs_explanation_enrichment`

Students need good feedback, not just right/wrong output. This flag reminds us
that a bare question+answer pair is not enough for the final learning
experience.

After the 2026-05-04 explanation pass, this flag should only reappear if a new
question enters staging without a generated or manually written explanation.

### `needs_autograde_rule_review`

Open-ended or semi-open-ended formats such as:

- fill-gap
- short-text
- structured response

need more careful grading logic than plain MCQ.

After the 2026-05-04 structural re-audit and ordering-support pass, this flag
should now be interpreted very narrowly. It is no longer a blanket marker on
most text-entry items, and the only known ordering residual has been normalized
as a `drag_drop` / ordering question.
runtime contract.

### `needs_structured_answer_normalization`

This surfaces items where the answer data is still trapped in a raw prose form,
for example:

- `accept: ...`
- `also accept ...`
- `Any 2 from ...`
- unstructured match answers

These items may still be good source material, but they are not yet safely
shaped for dependable self-marking.

### `supplementary_derived_item`

This identifies extra revision items derived from mark-scheme content rather
than directly imported from the question-paper wording.

These items are not automatically bad, but their provenance should stay visible
so they are not mistaken for direct PPQ conversions.

### `practice_question_needs_source_normalization`

Practice-bank items are useful, but they should still be normalized and checked
carefully against the fact files and official content.

## Review Priority

The transformer assigns a review priority:

- `critical`
- `high`
- `medium`
- `low`

### `critical`

Assigned when a structural blocking flag is present.

### `high`

Assigned when the item is structurally parseable but still blocked by editorial
trust issues, especially:

- missing explanation;
- unresolved objective mapping;
- unsafe auto-mark rule shape; or
- confirmed defect-register presence.

### `medium`

Assigned when the item mainly needs enrichment or mapping work.

### `low`

Assigned when no important review issue has been detected yet.

This does not mean “publish automatically”. It only means “lower-risk review”.

## What This Protects Against

This gate is designed to stop us from accidentally treating questions as ready
just because they parsed cleanly.

It protects against:

- missing diagrams in visual questions
- MCQs with broken option sets
- empty or weak answer structure
- transformed questions that need human sense-checking
- unsupported auto-marking assumptions
- audited known-bad content slipping forward
- single-statement true/false items hiding inside `match_table`
- staging summaries that overstate readiness

## Current Limitation

This is still a heuristic review gate, not a semantic truth engine.

It helps us:

- prioritize review
- identify likely weak spots
- keep the content pipeline honest

But it does not replace careful content QA using:

- the official fact files
- the curated past-paper-by-topic documents
- the extracted mark schemes
- the teacher’s own sense-checking

## Best Use In The Next Stage

The recommended next step is:

1. build the normalized bundle
2. build the staging payload with review flags
3. inspect summary counts and samples
4. fix confirmed defects, explanations, and unsafe grading structures
5. only then allow any items to move from `draft` toward `approved`
6. only after that shape real staged database inserts for live promotion
