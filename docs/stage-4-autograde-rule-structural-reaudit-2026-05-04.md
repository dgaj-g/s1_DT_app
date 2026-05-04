# Stage 4 Autograde Rule Structural Re-Audit — 2026-05-04

## Scope

This re-audit targeted the remaining `needs_autograde_rule_review` family after:

- source-content defects had already been driven to zero;
- objective mapping had already been driven to zero; and
- the bridge/runtime path could already handle explicit accepted-answer shapes.

At the start of this pass, the Stage 4 staging summary still showed:

- `needs_autograde_rule_review`: `165`

The goal here was not to make that count look smaller cosmetically. The goal
was to separate:

1. answer shapes that were still genuinely ambiguous; from
2. answer shapes the Phase 1 runtime could already grade deterministically.

## Files changed

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_05_06.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_01_digital_data.md`

## What changed

### 1. The staging gate now recognizes safe autograde families

The Stage 4 gate previously flagged every:

- `fill_gap`
- `short_text`
- `structured_response`

item as needing autograde review by default.

That was too blunt. The gate now treats these families as structurally safe:

- `accepted_texts`
- `ordered_gaps`
- `shared_gap_pool`
- simple one-answer `short_text` / `fill_gap` items with a tight exact-match shape

It still keeps genuinely ambiguous cases blocked.

### 2. The importer now normalizes more residual answer shapes

The bundle builder was extended so it can now normalize:

- stem-aligned multi-blank phrase answers
  - example: `dots per inch`
  - example: `Analogue to Digital Converter`
- four-answer shared pools
  - example: `State four things supported by the MP4 file type`
- slash-separated short-answer alternatives where the stem only asks for one answer
  - example: `Limited range / limited battery life`
- an explicit accepted-text override for:
  - `database-applications.practice_bank.topic_02_03_software_database.q058`

### 3. Two long-definition stragglers were rewritten at source level

These were better fixed in the source than forced through brittle exact-text grading:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_05_06.md`
  - `network-technologies.past_paper.topics_05_06.q022`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_01_digital_data.md`
  - `digital-data.practice_bank.topic_01_digital_data.q065`

Both now ask for concise concept labels rather than long prose definitions.

### 4. The Phase 1 promotion bridge now enforces unresolved autograde blockers

This was an important trust-boundary fix.

The bridge now rejects questions that still carry:

- `needs_autograde_rule_review`
- `needs_structured_answer_normalization`
- `misclassified_true_false`

That means a reviewer cannot accidentally promote a structurally unresolved
question just by flipping its staging status.

## Verified results

After sequentially rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

the cross-bank count changed:

- `needs_autograde_rule_review`
  - from `165`
  - to `3`
  - to `1`
  - to `0`

Current residual count:

- `needs_autograde_rule_review`: `0`

## Controlled bridge verification before ordering support

A controlled promotion fixture was built from eight representative questions:

- newly cleared multi-blank fill-gap items
- newly cleared shared-pool items
- newly cleared accepted-text items
- the one residual ordering item

Dry-run result:

- `8` staged
- `7` promoted
- `1` rejected

Promoted:

- `fill_gap`: `5`
- `short_text`: `2`

Rejected:

- `digital-data.practice_bank.topic_01_digital_data.q012`

Bridge rejection reason:

- `flag_needs_autograde_rule_review`

This is the correct outcome.

## Ordering support added

The previous residual item was:

- `digital-data.practice_bank.topic_01_digital_data.q012`

Prompt:

- `Place the following storage units in descending order according to size: Megabyte, Bit, Kilobyte, Byte, Gigabyte.`

It is now normalized as:

- `format`: `drag_drop`
- `options_json.items`: the unordered storage units
- `correct_answer_json.order`: the correct descending order
- `autograde_rules_json.mode`: `ordering`

A controlled one-question promotion fixture verified that this item now
promotes as a live ordering question:

- `1` staged
- `1` promoted
- `0` rejected
- promoted format: `drag_drop`

## Conclusion

This re-audit closes the autograde-rule family as a broad cross-bank blocker.

The bank still remains blocked for the right editorial reasons, especially
missing explanations and practice-source normalization. The structural
autograde-rule blocker is now cleared.
