# Stage 4 Focused Re-Audit: Topic 2/3 Practice Source Corrections (2026-05-03)

## Scope
This re-audit checks the direct source-correction pass applied to:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_02_03_software_database.md`

The aim is narrow:

1. verify whether the RAM/ROM wording defect identified in the Software audit is a true source defect;
2. confirm that the correction improves conceptual accuracy without overreaching; and
3. verify that the regenerated import and staging payloads reflect the corrected wording.

This is not a full re-audit of all Software or Database practice questions.

## Inputs Reviewed

### Source and supporting files
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_02_03_software_database.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-software-content-audit-2026-05-03.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`

### Regenerated outputs reviewed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

## Item Reviewed

- `software.practice_bank.topic_02_03_software_database.q026`

## Findings

### 1. [Closed] `SW-004` was a genuine source wording defect and has been corrected cleanly.
The earlier source wording for `q026` said:

- `The two microchips that make up the main memory in a computer's CPU are called __________ and __________.`

That wording was technically careless because it tied RAM and ROM directly to:

- `the main memory in a computer's CPU`

which risks teaching an inaccurate relationship between primary memory and the CPU.

The patched source now reads:

- `The two main types of primary memory are called __________ and __________.`

with the same answer:

- `RAM; ROM`

This is a much safer revision prompt:

- it stays inside the intended concept contrast;
- it no longer mis-locates RAM/ROM inside the CPU; and
- it remains fully consistent with the stored answer.

### 2. The regenerated import bundle now reflects the corrected wording exactly.
After rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`

the staged stem for:

- `software.practice_bank.topic_02_03_software_database.q026`

now reads:

- `The two main types of primary memory are called __________ and __________.`

This confirms the source correction has propagated properly into the import pipeline.

### 3. The item still remains a draft, but no longer for source-trust reasons.
The staging payload still blocks `q026`, which is correct.

Its remaining review flags are:

- `needs_autograde_rule_review`
- `needs_explanation_enrichment`
- `practice_question_needs_source_normalization`

That means the source-content defect is fixed, but the item is still not student-ready until the marking/explanation layers improve.

## Outcome

### Defects that can now be closed
- `SW-004`

## Conclusion
This re-audit supports closing the Software source-wording defect:

- the original wording was genuinely unsafe;
- the new wording is more accurate and still simple for students; and
- the regenerated bundle confirms the correction took effect.

The remaining software issues should stay in the transformation/runtime queue rather than being treated as source problems.
