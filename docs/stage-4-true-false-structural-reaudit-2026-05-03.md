# Stage 4 Cross-Topic Re-Audit: True/False Structural Normalization (2026-05-03)

## Scope
This re-audit checks whether the repeated cross-topic defect of single-statement True/False items being staged as `match_table` has now been resolved in the Stage 4 import and staging layers.

This is a structural re-audit, not a source-content rewrite.

## Inputs Reviewed

### Scripts changed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

### Regenerated outputs reviewed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`
- `/private/tmp/unit1_phase1_live_payload_true_false_check.json`

## Structural change applied

In:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`

`infer_format(...)` now classifies eligible single-statement binary judgment items as `true_false` instead of `match_table`.

The normalization now triggers when:
- the qtype explicitly says `True / False` or `True/False`
- the stem includes clear binary-judgment signals such as:
  - `True or False`
  - `State whether`
  - `Select whether`
  - `Decide whether`
  - `Tick True or False`
- or the answer is exactly `True` / `False` and the item has neither options nor matching/list blocks

## Verified outcomes

### 1. The misclassification blocker has been removed from the Stage 4 gate.
After rebuilding the Stage 4 bundle and staging payload:

- `misclassified_true_false`
  - from `65`
  - to `0`

### 2. The import bundle now stores these items in the correct runtime-facing format.
Verified examples:

- `digital-data.practice_bank.topic_01_digital_data.q008`
  - format: `true_false`
- `cyberspace-network-security-and-data-transfer.past_paper.topics_07_08_09.q047`
  - format: `true_false`
- `health-and-safety.practice_bank.topic_09_12_wider_impact.q011`
  - format: `true_false`

### 3. The cleanup also reduced wider structural noise across the bank.
After rebuilding:

- `needs_structured_answer_normalization`
  - from `174`
  - to `101`

This reflects the fact that a large number of T/F items no longer appear structurally malformed once they are modeled as `true_false` rather than `match_table`.

### 4. The Phase 1 promotion bridge no longer sees the old T/F match-table failure mode.
A verification run against:

- `/private/tmp/unit1_phase1_live_payload_true_false_check.json`

showed:

- `true_false_still_modeled_as_match_table`
  - `0`

That confirms the live-payload bridge is now aligned with the corrected staging shape.

### 5. The staging gate is now cleaner and more honest.
After the rebuild:

- all `904` staged questions remain `draft`
- but the old `critical`/`structural_draft` split caused by T/F misclassification is gone
- current gate buckets are now:
  - `editorial_draft`: `904`

That is a healthier state for the bank because the remaining blockers are now mostly real content, explanation, and answer-normalization work rather than a repeated classification bug.

## Defects that can now be closed

- `SS-001`
- `DD-002`
- `SW-003`
- `HW-002`
- `CY-002`
- `CL-002`
- `EL-002`
- `EMP-001`
- `HS-001`
- `DA-001`

## Conclusion
This re-audit supports closing the cross-topic true/false misclassification defects.

The original problem was not with the source content itself. It was with the importer and downstream staging assumptions.

That structural defect is now resolved at the bundle, staging, and promotion-bridge levels:
- eligible single-statement binary items are stored as `true_false`
- Stage 4 no longer flags them as misclassified
- the promotion bridge no longer rejects them for being `match_table` in disguise

The remaining blockers for these questions are the expected later-stage issues such as:
- `needs_explanation_enrichment`
- `needs_autograde_rule_review`
- topic-specific content/editorial defects unrelated to the old T/F shape bug
