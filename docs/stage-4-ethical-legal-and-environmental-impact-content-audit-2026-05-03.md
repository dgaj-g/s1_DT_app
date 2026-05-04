# Stage 4 Content Audit: Ethical, Legal and Environmental Impact (2026-05-03)

## Scope
This audit checks the `Ethical, legal and environmental impact` topic in the staged Stage 4 payload against the curated source materials. The aim is to determine whether the imported questions are factually trustworthy, faithful to source intent, and safe for an auto-marked revision app.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_07_08_09.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_7_12.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_practice_questions.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged ethical/legal/environmental questions: `54`
- Prompt assets linked: `0`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `38` MCQ
  - `10` match_table
  - `5` fill_gap
  - `1` structured_response
- Current review flags:
  - `needs_explanation_enrichment`: `54`
  - `practice_question_needs_source_normalization`: `20`
  - `transformed_exam_item`: `19`
  - `needs_objective_mapping`: `7`
  - `needs_autograde_rule_review`: `6`

## Findings

### 1. [High] The GPS-process practice item is now structurally and conceptually unsafe after normalization.
The practice-source QA file had already flagged Topic 9 Q6 as a broken MCQ because one distractor was a sentence rather than a process name. In the staged payload, that item is now:
- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q006`
- stem: `Which process is used by GPS to work out a device's location?`
- options: `Triangulation`, `Encryption`, `Trilateration`, `Tessellation`
- staged answer: `A`

This is worse than a cosmetic issue. The importer has repaired the grammar problem by introducing `Trilateration` as a noun option, but it has kept `Triangulation` as the correct answer. That leaves the question in a state where two options are now plausible to a technically informed student. For a revision app, that is not safe enough.

### 2. [High] This topic contains a large amount of transformed exam content, and some of it flattens richer ethical/legal reasoning into recognition tasks.
There are `19` items flagged `transformed_exam_item`, including:
- `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q010` to `q014`
  - a longer social-media-misuse response set broken into separate MCQs
- `q022` and `q023`
  - a multi-statement DPA-selection task converted into two isolated `NOT a principle` MCQs
- `q024` and `q025`
  - Information Commissioner vs Data Controller responsibilities split into recognition items
- `q027`
  - 2024 GPS definition converted into a standalone MCQ
- `q029` and `q030`
  - later social-media misuse content again flattened into small MCQs

Many of these are not obviously factually wrong, but they reduce generation and explanation tasks to recognition tasks too often. That weakens their value as revision for the actual Unit 1 exam.

### 3. [Medium] Several source-context gaps have been repaired reasonably well by transformation, which is positive but should still be treated as editorial rewriting.
This topic gives a useful contrast with some earlier audits: the staged bank sometimes improves weak source presentation.

Examples:
- `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q022` and `q023`
  - reconstruct the missing six-option Data Protection Act choice list from 2023 Q10(b), which the QA report explicitly said was incomplete in the source doc
- `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q032`
  - reconstructs the legislation-matching task in a way that makes the distractor problem intelligible
- `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q027`
  - avoids the original `definition above` wording issue by turning the GPS definition into a direct question

This is a genuine positive, but it also means the topic is more heavily dependent on editorial reconstruction than the raw source docs alone might suggest.

### 4. [Medium] Single-statement True/False items are again misclassified as `match_table`.
Examples include:
- `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q033`
- `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q034`
- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q013`
- `q014`
- `q015`

These are ordinary binary-judgment prompts, not matching tasks. As in other topics, this is the wrong structural contract for the runtime.

### 5. [Medium] Several short-answer and fill-gap items are useful in principle but still unsafe for fair auto-marking in their current form.
Examples include:
- `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q003`
  - `Positioning`
- `q016`
  - `Copyright`
- `q019`
  - `Commissioner`
- `q031`
  - `Consumer`
- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q016`
  - `Triangulation; 3 (three)`
- `q017`
  - `Data Protection Act`

These are all reasonable revision ideas, but they still rely on raw-string answer storage or simplistic fill-gap logic. In an app students must trust, that is not robust enough yet.

### 6. [Medium] Some practice-bank prompts are too brittle or fact-file-specific for a high-trust revision bank.
A few examples stand out:
- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q008`
  - `Who originally invented GPS?`
- `q015`
  - `According to the fact file, by default a Facebook user profile will automatically become public when the user turns 18.`

These may reflect the source materials, but they are more brittle than the best exam-style revision questions. They risk turning revision into fact-file trivia rather than strong syllabus-centred preparation.

### 7. [Medium] Objective mapping is still incomplete in this topic.
The following staged items still carry `needs_objective_mapping`:
- `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q005`
- `q009`
- `q017`
- `q021`
- `q026`
- `q027`
- `q031`

This would weaken later adaptive guidance and topic-mastery reporting if left unresolved.

### 8. [Positive] The QA report suggests the core source material for this topic is broadly reliable, and one inherited CCEA typo has not been amplified.
The topic-specific QA report is largely reassuring here:
- 2018 Q1(f)/(g): OK
- 2019 Q1(d)/(e)/(g): OK
- 2021 Q1(a)/(b): OK
- 2021 Q8(a): OK
- 2021 Q10(d)(i)/(e): OK
- 2023 Q10(a): OK
- 2024 Q1(c): OK
- 2025 Q9(a)/(b): OK

The QA report also notes a CCEA mark-scheme typo in 2022 (`Copyright Designs and Patents Act (1998)` instead of `1988`). The staged ethical/legal items do not appear to have imported that bad year verbatim, which is a positive outcome.

### 9. [Positive] There are no prompt-asset issues in this topic.
This topic has `0` prompt assets and `0` unresolved assets. For this content area, that appears acceptable rather than a gap.

### 10. [Medium] No ethical/legal question is explanation-ready yet.
All `54` staged questions still carry `needs_explanation_enrichment`, so the student-facing teaching/feedback layer is still absent.

## Overall Assessment
`Ethical, legal and environmental impact` is stronger than some earlier topics on raw factual reliability, and it benefits from a few transformations that genuinely repair source-context gaps.

However, it still is not safe for student release.

The strongest risks are:
1. the GPS-process practice item, which is now in an internally unsafe state after normalization;
2. a heavy dependence on transformed exam items that flatten richer reasoning into recognition; and
3. the repeated runtime-structure problem of true/false misclassification plus brittle short-answer marking.

## Recommendation
Do not promote ethical/legal/environmental items toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. explicitly fix or replace the GPS-process practice item;
2. normalize single true/false items into a dedicated format;
3. review whether transformed social-media and DPA items preserve enough of the original exam demand; and
4. add stronger accepted-answer rules and explanations for the short/fill questions before they are ever shown to students.
