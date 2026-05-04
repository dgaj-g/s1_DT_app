# Stage 4 Content Audit: Health and Safety (2026-05-03)

## Scope
This audit checks the `Health and safety` topic in the staged Stage 4 payload against the curated source materials. The aim is to determine whether the imported questions are factually trustworthy, faithful to source intent, and safe for an auto-marked revision app.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_10_11_12.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_7_12.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_practice_questions.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged health-and-safety questions: `31`
- Prompt assets linked: `0`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `22` MCQ
  - `6` match_table
  - `2` structured_response
  - `1` fill_gap
- Current review flags:
  - `needs_explanation_enrichment`: `31`
  - `practice_question_needs_source_normalization`: `19`
  - `transformed_exam_item`: `9`
  - `needs_autograde_rule_review`: `3`
  - `needs_objective_mapping`: `1`

## Findings

### 1. [Medium] The raw health-and-safety content looks comparatively reliable, but the topic still relies on several transformed micro-items.
This topic is cleaner than some earlier ones on factual accuracy. The supporting QA report is broadly reassuring:
- 2018 Q1(d): OK
- 2019 Q1(f): only a minor wording/typo note
- 2022 Q9(a)(i)/(ii): OK
- 2024 Q1(e): OK
- 2024 Q9(b): OK
- 2025 Q10(a)/(b): OK

However, the staged bank still contains `9` transformed items, including:
- `health-and-safety.past_paper.topics_10_11_12.q002`
- `q004`
- `q005`
- `q007`
- `q008`
- `q009`
- `q010`
- `q011`
- `q012`

Most of these are not obviously wrong, but they break broader source material into smaller recognition tasks, which weakens revision depth even when the facts themselves are sound.

### 2. [Medium] Several transformed items flatten richer prevention/hazard material into isolated one-mark recognition checks.
Examples include:
- `q007` and `q008`
  - health hazards from gaming split into separate MCQs
- `q009` and `q010`
  - RSI-contributing activities split into separate MCQs
- `q011` and `q012`
  - back-strain prevention reduced to recognition items

Again, these are not necessarily inaccurate, but they simplify explanation-heavy health-and-safety revision into isolated answers too often.

### 3. [Medium] Single-statement True/False items are again misclassified as `match_table`.
Examples include:
- `health-and-safety.practice_bank.topic_09_12_wider_impact.q011`
- `q012`
- `q013`
- `q014`

These are ordinary binary-judgment prompts and should be represented as a dedicated true/false format, not as match-table records.

### 4. [Medium] The list-style and structured-response health-and-safety items are strong revision prompts, but they are not yet safe for automatic marking.
Examples include:
- `health-and-safety.practice_bank.topic_09_12_wider_impact.q015`
  - `spine; lumbar`
- `q016`
  - `Any THREE of: taking regular breaks; moving and changing sitting position regularly; exercise; using ergonomic keyboards and mice; switching to joysticks; choosing furniture that supports good posture and is adjustable; using wrist rests`
- `q017`
  - `RSI (Repetitive Strain Injury); back strain; eye strain`

These are actually good revision prompts, but the current answer storage is still raw-string/list prose rather than structured accepted-answer rules.

### 5. [Medium] One objective-mapping gap remains in the practice side.
The following staged item still carries `needs_objective_mapping`:
- `health-and-safety.practice_bank.topic_09_12_wider_impact.q014`

That is not a major failure, but it still needs resolution if later adaptive reporting is to be fully dependable.

### 6. [Positive] The staged match/reconstruction work is reasonably coherent in this topic.
Unlike some earlier topics, the transformed/matched items here generally remain understandable and aligned to the intended concept. For example:
- `health-and-safety.past_paper.topics_10_11_12.q002`
  - matching health problems to prevention methods
- `health-and-safety.practice_bank.topic_09_12_wider_impact.q018`
  - matching measures to the problems they help prevent

These still need structural/runtime treatment, but they are not currently showing the kind of glaring concept drift we saw in some other topics.

### 7. [Positive] There are no prompt-asset issues in this topic.
This topic has:
- `0` prompt assets
- `0` unresolved assets

That appears acceptable.

### 8. [Medium] No health-and-safety question is explanation-ready yet.
All `31` staged questions still carry `needs_explanation_enrichment`, so the student-facing feedback/teaching layer is still missing.

## Overall Assessment
`Health and safety` is one of the more trustworthy topics we have audited so far on raw factual content. It does not currently show a major factual howler of the kind seen in some earlier topics.

However, it still is not safe for student release.

The main issues are:
1. over-reliance on transformed micro-items for richer prevention/hazard content;
2. repeated true/false misclassification; and
3. unsafe list-style/structured-response marking.

## Recommendation
Do not promote Health and Safety toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. normalize single true/false items into a dedicated format;
2. add stronger accepted-answer rules for the fill-gap and list-style items;
3. review whether the transformed hazard/prevention items preserve enough of the original revision demand; and
4. resolve the remaining objective-mapping gap.
