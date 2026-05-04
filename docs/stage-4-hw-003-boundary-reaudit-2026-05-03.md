# Stage 4 Focused Re-Audit: HW-003 Source/Structure Boundary (2026-05-03)

## Scope
This re-audit revisits the remaining `HW-003` defect against the current source and staged outputs.

The goal is to decide whether `HW-003` is still a genuine source-content defect, or whether it now belongs entirely in the structural/runtime layer.

This check focuses only on:

- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q025`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q032`

## Inputs Reviewed

### Source
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

### Supporting audit/defect context
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-computer-hardware-content-audit-2026-05-03.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-topic-05-06-practice-source-reaudit-2026-05-03.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`

### Current staged output reviewed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

## Findings

### 1. `q025` is now source-safe and should no longer be treated as a content defect.
The current source wording is:

- `The ALU is a vital part of the ____________-____________ cycle.`
- answer: `fetch-execute`

This is concise, natural, and conceptually clear.

The older audit concern about awkward wording referred to the earlier phrasing:

- `part and end of the ... cycle`

That wording has already been removed. There is no longer a good reason to keep `q025` under a source-content defect label.

### 2. `q032` is also source-safe; its remaining problem is structural.
The current source wording is:

- `State one disadvantage of a wireless microphone.`
- answer: `Limited range / limited battery life`

This is a perfectly reasonable revision prompt at source level. The issue is not the wording or concept. The issue is that the accepted alternatives are still stored as one raw answer string rather than as a structured accepted-answer rule.

That means the remaining risk for `q032` is:

- fair self-marking
- answer normalization
- runtime accepted-answer structure

not source-content trust.

### 3. The current `known_content_defect` gate is now overstating the problem for both items.
In the staged payload, both `q025` and `q032` still carry:

- `known_content_defect`

That is no longer an honest description of their current state.

The remaining flags that do still make sense are:

#### `q025`
- `needs_autograde_rule_review`
- `needs_explanation_enrichment`
- `practice_question_needs_source_normalization`

#### `q032`
- `needs_autograde_rule_review`
- `needs_explanation_enrichment`
- `needs_structured_answer_normalization`
- `practice_question_needs_source_normalization`

Those are downstream staging/runtime issues, not evidence of a still-open source defect.

## Outcome

### Source-level conclusion
The source-review portion of `HW-003` is complete.

### What should happen in the defect register
- remove `q025` and `q032` from `known_content_defect`
- retire `HW-003` as a source-content defect
- if needed, carry the `q032` problem forward under a structural normalization defect instead

## Conclusion
`HW-003` should no longer remain open as a source-content defect.

The current source is acceptable for both reviewed items:

- `q025` is now clearly worded
- `q032` is a reasonable prompt with multiple acceptable answers

The remaining work belongs to the structural/runtime layer, not to source correction.
