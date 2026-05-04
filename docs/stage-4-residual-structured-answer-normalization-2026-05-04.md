# Stage 4 Residual Structured-Answer Normalization Re-Audit

Date: 2026-05-04
Project: S1 / GCSE Unit 1 Revision App
Scope: Final structural normalization pass for the residual `needs_structured_answer_normalization` family.

## Context
After the earlier true/false, accepted-answer, and match-table passes, the staged payload had been reduced to a much smaller unresolved structural set.

The remaining questions were no longer mixed parser failures. They had converged into a narrow family of genuine multi-answer open-response items, plus a small amount of short factual conservative classification.

## Structural changes applied
The final pass introduced three follow-on normalizations in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260503221500_phase1_runtime_v2.sql`

### 1. Comma-separated `Terms:` / `Measures:` recovery
The importer now recovers structured choices from list blocks such as:

- `Terms: Phishing, Identity Theft, Cyberbullying`
- `Measures: Anti-glare screen, Wrist rest, Lumbar support chair, Foot rest`

This removed the last hidden match-table residue from the Topic 9/10/11/12 practice-source family.

### 2. `also accept ...` normalization
Short-answer items that previously kept accepted alternatives in prose now normalize them into explicit accepted-answer lists.

Examples include:

- `digital-data.past_paper.topics_01_02.q047`
- `software.past_paper.topics_01_02.q017`

### 3. `Short factual` reclassification
The importer now treats the `Short factual` question type as `short_text` rather than leaving it as generic `structured_response`.

This removed a large amount of conservative but unhelpful structural noise from simple “name one / state one” prompts.

### 4. `Any 2 / Any 3 from` normalization
The remaining genuinely multi-answer list items are now normalized into a structured multi-gap `fill_gap` shape with:

- explicit gap ids
- a shared accepted-answer pool
- `require_distinct: true`

This preserves the source demand better than forcing those items into distractor-based multi-select questions.

## Verified outcomes
After rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

The cross-bank structural blocker count changed as follows:

- `needs_structured_answer_normalization`
  - from `31`
  - to `12`
  - to `0`

At this point, the staging summary contains **no remaining structural-normalization blocker flags**.

## Controlled bridge verification
A controlled Phase 1 promotion fixture was run using:

- `digital-data.practice_bank.topic_01_digital_data.q033`
- `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q038`

Result:

- the cyberspace item promoted successfully as a `fill_gap` runtime payload with three distinct answer boxes
- the digital-data item was rejected, but only because of the already-open content defect `DD-003`

This is the correct outcome. It shows that the bridge now understands the structured multi-answer shape, and that open content defects still block promotion independently.

## Full-bank bridge verification
A full-bank Phase 1 bridge check was then run against the rebuilt staging payload.

Key result:

- there were **no structural rejection reasons** left in the summary

The remaining full-bank blockers are now purely editorial / release-governance blockers such as:

- `staging_status_not_allowed:draft`
- `missing_explanation`
- `flag_needs_explanation_enrichment`
- `flag_needs_objective_mapping`
- open audited defects

## Conclusion
This pass closes the structural normalization family as a live blocker category.

That does **not** mean the bank is ready for students. It means something narrower but very important:

- the remaining promotion blockers are now about **content trust, explanation quality, objective coverage, and release status**, not hidden parser/runtime ambiguity

This is a real milestone because it narrows the next phase of work to the questions themselves and the teaching quality around them.
