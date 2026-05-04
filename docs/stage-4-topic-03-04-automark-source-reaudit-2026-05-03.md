# Stage 4 Focused Re-Audit: Topic 3/4 Automark Source Corrections (2026-05-03)

## Scope
This re-audit checks the direct source-correction pass applied to:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`

The goal is narrow:

1. decide whether `DB-001` is a genuine source defect or only a staging/runtime defect;
2. verify that any source correction is backed by the Topic 3 support files;
3. confirm whether `DB-002` should remain open as a structural accepted-answer problem; and
4. verify that the regenerated import and staging payloads reflect the correct decision.

This is not a full re-audit of all Database Applications content.

## Inputs Reviewed

### Source and support files
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_3_4.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/apply_fixes.py`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_automark_pastpaper.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_extraction/2024.md`

### Regenerated outputs reviewed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

## Items Reviewed

- `database-applications.past_paper.topics_03_04.q003`
- `database-applications.past_paper.topics_03_04.q042`
- `database-applications.past_paper.topics_03_04.q045`
- `database-applications.past_paper.topics_03_04.q046`

## Findings

### 1. [Closed] `DB-001` was a genuine source defect and has been corrected cleanly.
The earlier source wording for `q042` said:

- `Complete the sentences about databases using these words: RECORD; TABLE; COLUMN. Each word is used once only.`

but only provided two blanks and only used two answers:

- `(1) Table; (2) Record`

This was not just a staging defect. The Topic 3 QA notes explicitly describe the intended wording as:

- `RECORD / TABLE / COLUMN — not all words used`

and the supporting fix script also injects only the two missing sentences, not a third blank. That means the correct repair is to change the instruction, not to invent a third sentence.

The patched source now reads:

- `Complete the sentences about databases using these words: RECORD; TABLE; COLUMN. Not all words are used.`

The regenerated import bundle now reflects that wording exactly for:

- `database-applications.past_paper.topics_03_04.q042`

Verdict:

- `DB-001` is now fixed at source-content level

### 2. [Open, by design] `DB-002` is not a source defect and should remain a structural/runtime defect.
The following items still carry accepted alternatives in prose:

- `database-applications.past_paper.topics_03_04.q003`
- `database-applications.past_paper.topics_03_04.q045`
- `database-applications.past_paper.topics_03_04.q046`

Examples:

- `Uniquely identifies a record (accept: uniquely identifies a member / individual)`
- `ArtistID (accept: ArtistName)`
- `RO1 (accept: =RO1)`

The support files are important here:

- `qa_automark_pastpaper.md` explicitly calls for OR-logic for `(accept: ...)` answers
- `_extraction/2024.md` confirms that both `ArtistID`/`ArtistName` and `RO1`/`=RO1` are acceptable depending on the field/criteria framing

So the problem is not that the source answer text is wrong. The problem is that the staging/runtime layer still stores these as raw prose rather than a structured accepted-answer set.

Verdict:

- `DB-002` remains open
- this should be fixed in accepted-answer normalization, not by rewriting the source content

### 3. The corrected `q042` is still a draft, but now for the right reasons.
After regeneration, `database-applications.past_paper.topics_03_04.q042` still carries:

- `needs_autograde_rule_review`
- `needs_explanation_enrichment`

That is correct.

It should no longer be blocked because of impossible instructions, but it is still not ready for student release until the marking and explanation layers are improved.

## Outcome

### Defects that can now be closed
- `DB-001`

### Defects that remain open
- `DB-002`

## Conclusion
This re-audit gives us a clean split:

- `DB-001` was a real source defect and has now been corrected responsibly
- `DB-002` is not a source-content problem and should stay in the structural/runtime remediation queue

That is exactly the kind of distinction we want to preserve if this app is going to earn student trust.
