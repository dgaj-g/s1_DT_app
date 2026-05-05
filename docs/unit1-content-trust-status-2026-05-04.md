# Unit 1 Content Trust Status

Date: 2026-05-04

## Why this exists

This file records the content-quality response to teacher testing where several serious issues were found:

- fill-gap answers such as `b12` being marked wrong when `B12` was accepted;
- match-table stems leaking generated helper text such as `Pairs: ... -> ?`;
- spreadsheet and database questions appearing without necessary visual context;
- open-ended answers being marked by exact phrase matching;
- at least one incorrect/unsafe accepted answer, where `memory` alone was accepted for a cache-memory question;
- wording/source concerns such as `3000 million` instead of `3 billion` and a hard-drive disadvantage needing clearer source-backed wording.

## What has now been changed

### Database migrations applied

The following migrations have been pushed to the linked Supabase project:

- `supabase/migrations/20260504172000_content_accuracy_hotfixes.sql`
- `supabase/migrations/20260504173500_widen_slash_fill_gap_answers.sql`
- `supabase/migrations/20260504175000_remove_remaining_scaffold_and_refresh_snapshots.sql`
- `supabase/migrations/20260504180500_objective_marking_reliability_hotfix.sql`
- `supabase/migrations/20260504182500_key_term_alias_and_open_answer_hotfix.sql`

### Student-facing fixes

- Removed public `Pairs:` / `-> ?` helper text from stems and content blocks.
- Added a frontend defensive cleaner so stale snapshots also hide any remaining generated helper text.
- Refreshed unfinished session snapshots in Supabase so in-progress student sessions do not keep old wording.
- Confirmed `b12` is accepted for the VLOOKUP answer where `B12` is expected.
- Confirmed chart answers such as `column`, `bar`, and `pie` are accepted for the chart-types question.
- Changed `3000 million cycles per second` to `3 billion cycles per second`.
- Reworded the HDD disadvantage answer to `A head crash can damage the disk surface`, supported by the hardware fact file wording that an HDD can crash and repeated crashes can damage the surface.
- Removed non-formatting answers such as sheet-tab management and `AutoSum` from the spreadsheet formatting-features question.
- Removed `memory` alone as an accepted answer for the cache-memory question.

### Marking reliability fixes

- Converted brittle open-ended short-answer prompts to objective MCQs where exact text marking was not reliable.
- Added safer aliases for fixed key-term answers, including examples such as `16GB`, `TCPIP`, `color depth`, `DPA`, `LAN`, `WAN`, `IoT`, `3-D Printer`, `Cache memory`, and spelling/punctuation variants.
- Kept scored marking only; no question has been made practice-only or unscored.

### Visual-context fixes

- Strict visual-context links have been added for spreadsheet, database, digital-data, hardware, and network questions that need images/tables/diagrams.
- The audit currently reports `118` questions with effective visual links.
- A contact sheet exists at `docs/database-image-contact-sheet.png` for reviewing extracted database images.

## Current audit position

The mechanical trust audit is at:

- `docs/unit1-question-bank-trust-audit-2026-05-04.md`
- `docs/unit1-question-bank-trust-audit-2026-05-04.csv`
- `docs/unit1-question-bank-trust-audit-2026-05-04.json`

Current result:

- Questions checked: `938`
- Blocker findings: `0`
- High findings: `0`
- Medium findings: `37`
- Scaffold leaks in active payload: `0`
- Generic `Complete the sentence` stems in active payload: `0`

The remaining medium findings are not known active defects. They are review markers for:

- duplicate or similar stems, often because a past-paper item and a practice item cover the same concept;
- fixed key-term short answers that still use exact matching but now have reviewed aliases.

## Important honesty note

This audit is a mechanical trust audit. It catches systematic defects consistently across the full bank, but it is not the same as a human teacher manually validating all 938 questions line-by-line against the original papers, mark schemes, fact files, and textbook scans.

For exam-critical deployment, the safe position is:

1. Use the mechanical audit to prevent known failure patterns.
2. Use the teacher review table/report to spot-check or fully review questions by topic.
3. Treat any newly discovered defect as a rule, then rerun the audit against all 938 questions.

## Latest build status

`npm run build` passes after these changes. The only warning is the existing Vite chunk-size warning.
