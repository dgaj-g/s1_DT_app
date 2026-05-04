# Stage 4 Focused Re-Audit: Software Defect Family (2026-05-04)

## Scope

This re-audit revisited the remaining open `Software` defect family:

- `SW-001`
- `SW-002`

The goal was to replace weak transformed past-paper items with safer, more faithful auto-markable versions rather than merely tolerating them as low-value matches.

## Source file changed

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_01_02.md`

## Questions corrected

### `software.past_paper.topics_01_02.q001`

Before:
- `match_table`
- both examples mapped to the same bucket
- weak proxy for the original `list two resources` demand

After:
- stem: `Apart from allocating memory, name TWO other resources managed by system software.`
- staged as:
  - `fill_gap`
  - 2 required answers
  - distinct-answer enforcement
- accepted concepts:
  - `Storage devices`
  - `Processor time`

### `software.past_paper.topics_01_02.q008`

Before:
- expanded into a 3-part utility-purpose match question
- broader than the original `List two utility programs`

After:
- stem: `List TWO utility programs.`
- staged as:
  - shared-pool `fill_gap`
  - 2 required answers
  - distinct-answer enforcement
- accepted concepts:
  - `Disk defragmenter`
  - `Anti-virus`
  - `Backup`

### `software.past_paper.topics_01_02.q009`

Before:
- `match_table`
- both resources mapped to `Managed by the operating system`
- weak transformation of the original source demand

After:
- stem: `Name TWO resources managed by the operating system.`
- staged as:
  - `fill_gap`
  - 2 required answers
  - distinct-answer enforcement
- accepted concepts:
  - `Memory (RAM allocation)` / `Memory` / `RAM allocation`
  - `Peripherals`

## Verification

### Staging rebuild

Regenerated:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

Verified that:
- all three questions now stage as `fill_gap`
- the answer structures are explicit rather than inferred from weak raw pairs

### Controlled promotion dry run

Dry-run output:
- `/private/tmp/stage4_software_recheck_live.json`

Summary:
- `3` staged
- `3` promoted
- `0` rejected

This confirms the corrected `Software` items are promotable through the Phase 1 bridge when defect gating is lifted for verification.

## Conclusion

`SW-001` and `SW-002` are now closed.

These items are still not student-ready in the broader sense because they still require:
- student-facing explanations
- broader topic-level review completion

But the specific defect family identified in the earlier audit has been corrected at source, rebuilt, and verified through the promotion bridge.
