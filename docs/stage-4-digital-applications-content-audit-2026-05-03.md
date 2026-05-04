# Stage 4 Content Audit: Digital Applications (2026-05-03)

## Scope
This audit checks the `Digital applications` topic in the staged Stage 4 payload against the curated source materials. The aim is to determine whether the imported questions are factually trustworthy, faithful to source intent, and safe for an auto-marked revision app.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_10_11_12.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_7_12.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_practice_questions.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged digital-applications questions: `48`
- Prompt assets linked: `0`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `40` MCQ
  - `5` match_table
  - `2` structured_response
  - `1` fill_gap
- Current review flags:
  - `needs_explanation_enrichment`: `48`
  - `practice_question_needs_source_normalization`: `35`
  - `transformed_exam_item`: `12`
  - `needs_autograde_rule_review`: `3`
- Objective-mapping gaps: `0`

## Findings

### 1. [Medium] Digital Applications has broad and useful coverage, but a large proportion of the topic is still lightweight recognition content.
This topic spans:
- MMOGs
- AR/VR
- simulation
- gamification
- mobile-first strategy
- apps and app monetisation
- VLEs
- online banking
- online training
- e-commerce
- B2B / B2C

That breadth is a real strength. However, `40` of the `48` staged questions are MCQs, and `12` are flagged `transformed_exam_item`. The topic therefore leans heavily toward quick recognition rather than deeper generation or explanation.

### 2. [Medium] Several transformed past-paper items flatten richer training, shopping and banking disadvantages into one-mark recognition checks.
Examples include:
- `digital-applications.past_paper.topics_10_11_12.q001`
- `q002`
- `q003`
  - online training advantages split into separate MCQs
- `q005`
- `q006`
- `q007`
  - online shopping disadvantages split into multiple recognition items
- `q008`
- `q009`
  - online training disadvantages flattened into separate recognition items
- `q010`
  - gaming disadvantage reduced to one recognition prompt
- `q011`
- `q012`
- `q013`
  - online banking disadvantages divided into separate MCQs

These are mostly factually plausible, but they reduce the student's need to generate and organise ideas, which matters in a topic full of evaluative pros/cons questions.

### 3. [Medium] Single-statement True/False items are again misclassified as `match_table`.
Examples include:
- `digital-applications.practice_bank.topic_09_12_wider_impact.q026`
- `q027`
- `q028`
- `q029`

As in several other topics, these are ordinary binary-judgment prompts and should be represented as a dedicated true/false format rather than match-table items.

### 4. [Medium] The best practice-bank Digital Applications prompts are still not safely auto-markable.
Examples include:
- `digital-applications.practice_bank.topic_09_12_wider_impact.q030`
  - `Virtual; Learning`
- `q032`
  - `Pay to download; In-app advertising; In-app purchases`
- `q033`
  - `Reusability ... Accessibility ... Environmentally friendly ...`

These are useful revision prompts, but they still depend on raw-string/list-style answer storage rather than structured accepted-answer logic. In particular, `q033` is a good content question but not yet a fair self-marking question.

### 5. [Medium] Some practice-bank items are slightly brittle or source-specific in a way that would benefit from editorial review.
Examples include:
- `digital-applications.practice_bank.topic_09_12_wider_impact.q024`
  - B2B example: `Salesforce`
- `q025`
  - B2C example: `Amazon`
- `q035`
  - risk for e-commerce users: `The item ordered may be defective`

These are not automatically wrong, and in one case the staged bank has actually repaired a source bug by carrying the intended answer for `q035`. But several items still feel more fact-file-specific than ideal for a high-trust revision bank.

### 6. [Positive] The source/QA evidence suggests this topic is strong overall on raw factual accuracy.
The practice QA report describes Topic 12 as `Strong` and says the MMOG / AR / VR distractors are well chosen, with only one blocker in the original source pack: the missing answer for Topic 12 Q35.

The staged payload now carries:
- `digital-applications.practice_bank.topic_09_12_wider_impact.q035`
- answer: `A`

So the importer/staging layer appears to have repaired that particular source bug rather than preserving it.

The QA report for Topics 7–12 is also broadly reassuring on the past-paper side:
- 2022 Q6: OK
- 2023 Q11(b): OK
- 2024 Q9(c): OK
- 2025 Q12: only minor missing-context concern in the source phrasing

### 7. [Positive] This topic has no prompt-asset issues and no current objective-mapping gaps.
The staged topic has:
- `0` prompt assets
- `0` unresolved assets
- `0` objective-mapping gaps

That is a strong structural position.

### 8. [Medium] No Digital Applications question is explanation-ready yet.
All `48` staged questions still carry `needs_explanation_enrichment`, so the student-facing revision/teaching layer is still missing.

## Overall Assessment
`Digital applications` is one of the stronger topics we have audited so far on raw content coverage and factual reliability.

However, it still is not safe for student release.

The biggest issues are:
1. too much reliance on recognition-style MCQs for evaluative training/shopping/banking material;
2. the repeated true/false structural defect; and
3. unsafe list-style/structured-response marking for some of the best practice prompts.

## Recommendation
Do not promote Digital Applications toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. normalize single true/false items into a dedicated format;
2. add stronger accepted-answer rules for the fill-gap and structured/list questions;
3. review whether transformed online training, shopping and banking items preserve enough of the original exam demand; and
4. add proper teaching explanations before student release.
