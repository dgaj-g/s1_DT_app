# Stage 4 Focused Re-Audit: Topic 9/12 Practice Source Corrections (2026-05-03)

## Scope
This re-audit checks the direct source-correction pass applied to:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`

The goal is narrow:

1. verify whether the GPS-process MCQ defect is genuinely a source-level problem;
2. correct it in a way that stays faithful to the source pack rather than importing outside assumptions; and
3. verify that the regenerated import bundle reflects a now-safe multiple-choice structure.

This is not a full re-audit of the wider Topic 9/12 practice source.

## Inputs Reviewed

### Source and supporting files
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_practice_questions.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-ethical-legal-and-environmental-impact-content-audit-2026-05-03.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`

### Regenerated outputs reviewed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

## Item Reviewed

- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q006`

## Findings

### 1. [Closed] `EL-001` was a genuine source-level MCQ safety defect and has been corrected cleanly.
The current Topic 9 practice-source QA notes already describe the original problem:

- the question `Which process is used by GPS to work out a device's location?`
- had a broken distractor
- and suggested replacing it with another process noun such as `Trilateration` or `Geocoding`

However, by the time of this re-audit, the live source had already moved to:

- `A. Triangulation`
- `B. Encryption`
- `C. Trilateration`
- `D. Tessellation`
- answer: `A`

That repaired the grammar problem, but created a more serious trust issue:

- two options now looked technically plausible to a well-informed student
- while the same source pack still taught `Triangulation; 3` later in Topic 9 Q16

So the safest fix was not to change the answer to `Trilateration`, because that would conflict with the rest of the curated pack. The safer fix was to keep the intended source answer and replace the distractor with a clearly wrong noun.

The patched source now reads:

- `A. Triangulation`
- `B. Encryption`
- `C. Geocoding`
- `D. Tessellation`
- answer: `A`

This keeps the question internally consistent with the rest of the pack while removing the two-correct-answer risk.

### 2. The regenerated import bundle now reflects the corrected option set exactly.
After rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`

the imported item now shows:

- `Triangulation`
- `Encryption`
- `Geocoding`
- `Tessellation`

with:

- `correct_answer_json.raw = A`

That is a safe self-marking structure for this item at the content level.

### 3. This correction is intentionally source-faithful rather than technically expansive.
This is important.

The purpose of the fix was not to turn the practice bank into a more advanced geodesy lesson. It was to remove an unsafe MCQ structure while staying aligned with the source pack students are actually being asked to revise from.

That makes this a legitimate source correction for this project.

## Outcome

### Defects that can now be closed
- `EL-001`

## Conclusion
This re-audit supports closing the GPS-process practice defect:

- the item was unsafe in source form;
- the source has now been corrected in a way that preserves the intended answer model; and
- the regenerated bundle confirms the safer distractor set is now flowing through the pipeline.
