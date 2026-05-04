# Stage 4 Content Audit: Changes in Employment Opportunities, Skills Requirements and Work Practices (2026-05-03)

## Scope
This audit checks the `Changes in employment opportunities, skills requirements and work practices` topic in the staged Stage 4 payload against the curated source materials. The aim is to determine whether the imported questions are factually trustworthy, faithful to source intent, and safe for an auto-marked revision app.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_10_11_12.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_7_12.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_practice_questions.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged employment-change questions: `26`
- Prompt assets linked: `0`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `16` MCQ
  - `5` match_table
  - `3` fill_gap
  - `2` structured_response
- Current review flags:
  - `needs_explanation_enrichment`: `26`
  - `practice_question_needs_source_normalization`: `19`
  - `transformed_exam_item`: `6`
  - `needs_autograde_rule_review`: `5`
- Objective-mapping gaps: `0`

## Findings

### 1. [High] This topic is thin, so its dependence on transformed exam items is a larger risk than the raw count suggests.
The supporting QA report explicitly notes that Topic 10 coverage is `genuinely thin`, with only three past-paper question groups listed. In the staged bank, `6` of the `26` questions are transformed exam items, including:
- `changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q001`
- `q002`
  - teleworking employer advantages split from a 2-mark `list two` item
- `q004`
- `q005`
- `q006`
- `q007`
  - a 6-mark QWC employment-impact response split into multiple recognition items plus a fill-gap

Because the topic is small, this transformation layer carries a lot of weight. If these rewrites are weak, students do not have much else in-topic to balance them out.

### 2. [Medium] Several transformed items flatten the real exam demand into low-generation recognition tasks.
The staged transformed items are not obviously factually wrong, but they do simplify the source demand noticeably.

Examples:
- `q001` and `q002`
  - turn a 2-mark `state two advantages` teleworking response into two separate MCQs
- `q004` to `q007`
  - reduce a broader `discuss the impact of increased use of digital technology on employment` response into small recognition tasks and one short fill-gap

This is not as severe as some of the bigger cybersecurity/cloud flattening, but it still weakens revision value in a topic where students need to explain impacts, not just spot them.

### 3. [Medium] Single-statement True/False items are again misclassified as `match_table`.
Examples include:
- `changes-in-employment-opportunities-skills-requirements-and-work-practices.practice_bank.topic_09_12_wider_impact.q010`
- `q011`
- `q012`
- `q013`

These are ordinary binary-judgment prompts and should be represented as a dedicated true/false format, not as match-table items.

### 4. [Medium] The open-response and list-style practice items are not yet safe for fair auto-marking.
Examples include:
- `changes-in-employment-opportunities-skills-requirements-and-work-practices.practice_bank.topic_09_12_wider_impact.q016`
  - `Shift work (accept: nightshifts)`
- `q017`
  - `Any THREE of: programmers; software engineers; ICT technicians; network managers; ICT consultants; web designers; app developers; social media (roles)`
- `q014`
  - `Teleworking; internet`
- `q015`
  - `9-5 (or 9 to 5)`
- `past_paper q007`
  - `productivity; job losses`

These are all plausible revision prompts, but they still rely on raw-answer prose and alternative-answer conventions that the live app is not yet equipped to mark fairly.

### 5. [Medium] Some practice-bank prompts are quite fact-file-specific and slightly dated in feel.
Examples include:
- `changes-in-employment-opportunities-skills-requirements-and-work-practices.practice_bank.topic_09_12_wider_impact.q005`
  - call centres operating 24 hours so users can report a lost phone or bank card
- `q008`
  - portable device example: `Tablet`
- `q019`
  - teleworker device example: `PDA`

These are not automatically wrong, but they are more brittle and source-specific than the strongest revision questions. In a small topic bank, too many items like this can make the revision feel narrow rather than concept-led.

### 6. [Positive] The raw source content for this topic appears broadly reliable.
The Topic 10 QA section is relatively reassuring:
- 2018 teleworking-employer advantages: OK
- 2021 job-displacement definition: only a cohesion issue around `definition above`
- 2023 Q11(a) QWC rewrite: described as a reasonable reframing, not a substantive content problem

That suggests the main problems here are not wholesale factual errors. They are mostly transformation quality, thin coverage, and auto-marking structure.

### 7. [Positive] This topic has no prompt-asset problems and no current objective-mapping gaps.
The staged topic has:
- `0` prompt assets
- `0` unresolved assets
- `0` questions flagged `needs_objective_mapping`

That is a stronger structural position than several earlier topics.

### 8. [Medium] No employment-change question is explanation-ready yet.
All `26` staged questions still carry `needs_explanation_enrichment`, so the student-facing teaching/feedback layer is still missing.

## Overall Assessment
`Changes in employment opportunities, skills requirements and work practices` is not one of the most error-prone topics we have audited so far. Its raw source material appears comparatively stable.

However, it still is not safe for student release.

The biggest risks are:
1. the topic is thin, so over-simplified transformations have an outsized effect;
2. true/false items are structurally misclassified again; and
3. several of the best candidate revision prompts still depend on unsafe raw-answer marking.

## Recommendation
Do not promote Topic 10 toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. normalize single true/false items into a dedicated format;
2. add stronger accepted-answer rules for the fill-gap and open/list questions;
3. review whether the transformed teleworking/employment-impact items preserve enough of the original exam demand; and
4. consider whether this topic needs broader coverage to avoid over-reliance on a small number of transformed items.
