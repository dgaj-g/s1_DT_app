# Stage 4 Focused Re-Audit: Topic 7/8 Practice Source Correction (2026-05-03)

## Scope
This re-audit checks the direct source-correction pass applied to:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_07_08_cyberspace_cloud.md`

The goal is narrow:

1. verify whether the named-example whistleblowing prompt is genuinely a source-level trust problem;
2. correct it in a way that improves student-facing stability without drifting away from the source pack's intended concept coverage; and
3. confirm that the regenerated staged item now reflects a safer concept-based revision prompt.

This is not a full re-audit of the wider Topic 7/8 practice source.

## Inputs Reviewed

### Source and supporting files
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_07_08_cyberspace_cloud.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-cyberspace-network-security-and-data-transfer-content-audit-2026-05-03.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`

### Regenerated outputs reviewed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

## Item Reviewed

- `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q023`

## Findings

### 1. [Closed] `CY-003` was a genuine source-level editorial weakness and has been corrected safely.
The original practice prompt asked:

- `State one example of a website that specialises in sharing stolen data (whistleblowing).`
- answer: `Wikileaks`

That was weak for three reasons:

- it relied on a specific named example rather than a stable syllabus concept;
- the wording `sharing stolen data` was loaded and not ideal for a trusted revision platform; and
- the item was brittle, because the revision value depended on remembering one website name rather than understanding the underlying term.

The source has now been rewritten to:

- `What term is used to describe the release of confidential information to expose wrongdoing in the public interest?`
- answer: `Whistleblowing`

This keeps the same broad topic intent while converting the item into a concept-centred revision question that is much less fragile and much more appropriate for student use.

### 2. The regenerated import bundle now reflects the safer concept-based prompt exactly.
After rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`

the imported item now shows:

- stem: `What term is used to describe the release of confidential information to expose wrongdoing in the public interest?`
- answer: `Whistleblowing`

The old named-example wording and `Wikileaks` answer are no longer present in the staged source flow for this item.

### 3. A small objective-mapping follow-up was needed and has been corrected.
Rewriting the item away from the `Wikileaks` keyword initially caused the staged question to lose its inferred objective mapping.

That exposed a genuine mapper blind spot rather than a content problem, so the objective catalog was updated to recognize:

- `whistleblowing`
- `confidential information`
- `public interest`
- `wrongdoing`

as valid cyberspace/cybercrime signals in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`

After regenerating the staging payload, the item now maps to:

- `cyberspace-network-security-and-data-transfer.cybercrime`

and no longer carries `needs_objective_mapping`.

### 4. The item is still draft for the expected non-content reasons.
The staged question remains `draft`, but now for the right reasons. It still carries:

- `needs_autograde_rule_review`
- `needs_explanation_enrichment`
- `needs_structured_answer_normalization`
- `practice_question_needs_source_normalization`

Those are legitimate downstream staging/runtime issues. They are not evidence that the source-level whistleblowing defect remains.

## Outcome

### Defects that can now be closed
- `CY-003`

## Conclusion
This re-audit supports closing the whistleblowing source defect:

- the original item was editorially brittle;
- the source has been rewritten into a stable concept-led prompt;
- the regenerated bundle reflects the safer wording and answer;
- the objective mapper has been updated so the item still lands in the correct cyberspace learning objective; and
- the remaining blockers are now the expected structural/explanation tasks rather than a lingering content-trust problem.
