# Stage 4 Grouped-Alias Structural Re-Audit — 2026-05-04

## Scope

This re-audit covered the remaining structurally open answer-normalization families after the earlier residual fill-gap pass:

- `DD-003`
- `EMP-002`
- `HS-002`
- `DA-002`

The focus was not broad content quality. It was narrower:

1. remove the last ambiguous source prompt in the family where appropriate;
2. normalize multi-gap answers into explicit ordered or shared-pool structures;
3. add grouped alias support where a single conceptual answer can appear in more than one acceptable form;
4. verify that those staged shapes survive the Phase 1 promotion bridge.

## Key corrections made

### 1. Digital Data source ambiguity removed

Source file:
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_01_digital_data.md`

Question updated:
- `digital-data.practice_bank.topic_01_digital_data.q021`

Change:
- stem changed from an ambiguous `10 minute video clip` prompt
- answer narrowed from `Megabyte (MB) / Gigabyte (GB)` to `Megabyte (MB)`

Result in staging:
- `correct_answer_json.accepted_texts = ["Megabyte (MB)", "Megabyte", "MB"]`

### 2. Ordered multi-gap normalization added

Questions like these now stage as explicit ordered fill-gap answers instead of raw semicolon strings:

- `changes-in-employment-opportunities-skills-requirements-and-work-practices.practice_bank.topic_09_12_wider_impact.q014`
- `changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q007`
- `health-and-safety.practice_bank.topic_09_12_wider_impact.q015`
- `digital-applications.practice_bank.topic_09_12_wider_impact.q030`

These now use:
- `correct_answer_json.gaps`
- `autograde_rules_json.mode = "ordered_gaps"`

### 3. Grouped alias support added for shared-pool fill-gap answers

Some list-style answers are not just flat terms. They are concept labels with acceptable variants.

Examples:
- `health-and-safety.practice_bank.topic_09_12_wider_impact.q017`
  - `RSI`
  - `Repetitive Strain Injury`
  - `RSI (Repetitive Strain Injury)`
- `digital-applications.practice_bank.topic_09_12_wider_impact.q033`
  - `Reusability`
  - `Accessibility`
  - `Environmentally friendly`
  - plus their longer explanatory versions

These now stage with:
- `accepted_groups`
- a canonical value per concept
- grouped accepted alternatives per concept

This matters because `require_distinct` can now be interpreted at the concept level instead of only at the exact-typed-text level.

## Verification

### Staging rebuild

Rebuilt successfully:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

### Controlled promotion dry run

Fixture built from 14 representative questions across:
- Digital data
- Changes in employment opportunities, skills requirements and work practices
- Health and safety
- Digital applications

Dry-run result without defect gating:
- `14` staged
- `14` promoted
- `0` rejected

This confirmed that the newly normalized shapes are promotable by the Phase 1 bridge and are no longer blocked by structural parse reasons.

## Defect-register impact

Closed:
- `DD-003`
- `EMP-002`
- `HS-002`
- `DA-002`

Regenerated staging summary after closing those groups:
- `known_content_defect: 36`

Previous value before these closures:
- `known_content_defect: 51`

Net improvement:
- `15` fewer staged questions now carry `known_content_defect`

## Important boundary

These closures only mean the affected items are no longer blocked for the **specific structural reasons named in those defect groups**.

They are still not student-ready because they continue to carry broader review flags such as:
- `needs_explanation_enrichment`
- `needs_autograde_rule_review`
- `practice_question_needs_source_normalization`

## Conclusion

This re-audit meaningfully reduced the remaining defect surface without pretending the bank is ready.

The most important technical gain is that the pipeline can now represent:
- ordered multi-gap answers,
- shared-pool multi-answer responses,
- grouped alias concepts with distinctness enforcement,

which removes a substantial class of unfair marking risk from the Phase 1 path.
