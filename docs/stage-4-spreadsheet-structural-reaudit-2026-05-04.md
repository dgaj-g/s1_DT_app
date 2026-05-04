# Stage 4 Focused Re-Audit: Spreadsheet Structural Answer Family (2026-05-04)

## Scope

This re-audit revisits the open spreadsheet structural defect family:

- `SS-002`

The aim was to decide whether the remaining short/list spreadsheet answers are
now safely represented for promotion through the Phase 1 live payload bridge.

## Source file reviewed

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_04_spreadsheet.md`

## Regenerated outputs reviewed

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`
- `/private/tmp/stage4_spreadsheet_recheck_live.json`

## Items reviewed

- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q039`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q040`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q041`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q042`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q043`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q045`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q046`
- `spreadsheet-applications.past_paper.topics_03_04.q054`

## Findings

### 1. The list-style practice items now have explicit shared-pool structures.

The following already stage cleanly as distinct-answer fill-gap questions:

- `q039` data-validation examples
- `q040` chart types
- `q041` formatting features

Each now carries:
- explicit `gaps`
- explicit accepted concepts
- `required_count`
- `require_distinct`

That removes the earlier dependence on prose-only `Any X from` marking.

### 2. The short-answer spreadsheet items are now canonical enough for exact-term promotion.

Two source answers were tightened to canonical forms:

- `q043`
  - before: `=AVERAGE(B2:B20)`
  - after: `AVERAGE`
- `q045`
  - before: `CSV (Comma Separated Values) file`
  - after: `CSV`

The remaining exact-answer items are already suitably crisp:

- `q042` → `=D1-C1`
- `q046` → `$B$2`
- `q054` → `B9:D9`

These are now strong enough for Phase 1 `short_text` promotion with exact accepted terms.

### 3. Controlled promotion verification succeeded for the full family.

A controlled reviewable fixture was built from the eight spreadsheet items and
passed through the Phase 1 promotion bridge.

Verified output:
- `/private/tmp/stage4_spreadsheet_recheck_live.json`

Summary:
- `8` staged
- `8` promoted
- `0` rejected

Promoted formats:
- `5` `short_text`
- `3` `fill_gap`

This is the key result:
- the spreadsheet family is no longer blocked by unsafe answer structure
- it remains blocked only by the normal editorial gate, especially explanation enrichment

## Conclusion

`SS-002` is now closed.

The affected items are not fully student-ready yet because they still need:
- student-facing explanations
- broader topic-level review completion

But the specific structural defect identified in the earlier spreadsheet audit
has now been corrected and verified through the promotion bridge.
