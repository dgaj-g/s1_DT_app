# Stage 4 Content Audit: Digital Data (2026-05-03)

## Scope
This audit checks the `Digital data` topic in the staged Stage 4 payload against the curated source materials. The aim is to determine whether the imported questions are factually trustworthy, structurally faithful to source intent, and safe for auto-marked revision.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_01_02.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_01_digital_data.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged digital-data questions: `177`
- Prompt assets linked: `7`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `112` MCQ
  - `32` match_table
  - `23` short_text
  - `10` fill_gap
- Current review flags:
  - `needs_explanation_enrichment`: `177`
  - `practice_question_needs_source_normalization`: `120`
  - `needs_autograde_rule_review`: `33`
  - `transformed_exam_item`: `19`
  - `needs_objective_mapping`: `7`

## Findings

### 1. [High] The current family-grouping heuristic is far too broad for Digital Data and would suppress legitimate revision coverage.
The staged family code `digital-data.graphics.choose` currently groups at least `17` questions together, including items on:
- pixels;
- resolution;
- JPEG vs BMP compression;
- vector vs bitmap differences;
- pixel count calculations; and
- what information is stored for vector shapes.

Likewise, `digital-data.data-measurement.choose` bundles together distinct ideas such as:
- kilobytes and megabytes;
- sample rate;
- bit depth;
- bit rate; and
- bit-rate calculation formulae.

These are not “the same question in disguise”. If later session selection treats these family codes as near-duplicates, the app will accidentally reduce topic coverage and distort adaptive revision choices.

### 2. [High] Sixteen single-statement True/False items are currently staged as `match_table` questions.
Examples include:
- `digital-data.past_paper.topics_01_02.q042`
- `digital-data.practice_bank.topic_01_digital_data.q008`
- `digital-data.practice_bank.topic_01_digital_data.q031`
- `digital-data.practice_bank.topic_01_digital_data.q037`
- `digital-data.practice_bank.topic_01_digital_data.q045`
- `digital-data.practice_bank.topic_01_digital_data.q056`
- `digital-data.practice_bank.topic_01_digital_data.q100`

These are ordinary binary judgment items such as:
- `Data and information mean exactly the same thing.`
- `Vector graphics can be resized without loss of quality.`
- `MIDI is a format for storing actual sound data.`

Structuring these as `match_table` questions is the wrong contract. They should be modeled as explicit true/false items, or as a dedicated statement-check format. As currently staged, they add unnecessary rendering and scoring ambiguity.

### 3. [High] Several Digital Data short-answer items contain ambiguous or multi-answer marking that is still trapped in raw strings.
Important examples include:
- `digital-data.practice_bank.topic_01_digital_data.q021`
  - answer stored as `Megabyte (MB) / Gigabyte (GB)`
  - this suggests the prompt is too open or the expected unit is not clearly pinned down
- `digital-data.practice_bank.topic_01_digital_data.q033`
  - `Any 2 from: width; height; colour depth.`
- `digital-data.practice_bank.topic_01_digital_data.q040`
  - `Binary colour code for every pixel; width; height; colour depth (any 3).`
- `digital-data.practice_bank.topic_01_digital_data.q044`
  - `Any 2 from: ... advantages of streaming ...`
- `digital-data.past_paper.topics_01_02.q047`
  - `MP4 (also accept MOV or MPEG)`

The content itself is broadly useful, but in this state the auto-marking layer cannot distinguish between:
- true ambiguity in the question,
- acceptable alternative wording, and
- exact-answer requirements.

That is too risky for a revision app where students will trust the feedback.

### 4. [Medium] Digital Data has a large number of transformed exam items, and they need continued editorial scrutiny.
Unlike the spreadsheet topic, the transformed-item flags are at least surfacing part of the risk here: `19` questions are currently flagged `transformed_exam_item`.

Examples include:
- `digital-data.past_paper.topics_01_02.q004`
  - originally a 2-mark description of how a pixel is used in a bitmap image
- `digital-data.past_paper.topics_01_02.q005`
  - originally a 2-mark explanation of resolution
- `digital-data.past_paper.topics_01_02.q013`
  - originally a 2-mark explanation of data
- `digital-data.past_paper.topics_01_02.q014`
  - originally a 2-mark explanation of information
- `digital-data.past_paper.topics_01_02.q033`
  - originally a 2-mark question on data portability

These are strong revision candidates, but because they have been rewritten into simpler auto-markable forms, they need deliberate review to make sure the core mark-scheme intent has not been thinned out too far.

### 5. [Medium] Objective mapping is not complete in areas that matter for foundational understanding.
The following Digital Data items are still flagged `needs_objective_mapping`:
- `digital-data.past_paper.topics_01_02.q001`
- `digital-data.past_paper.topics_01_02.q009`
- `digital-data.past_paper.topics_01_02.q013`
- `digital-data.past_paper.topics_01_02.q014`
- `digital-data.past_paper.topics_01_02.q038`
- `digital-data.past_paper.topics_01_02.q046`
- `digital-data.past_paper.topics_01_02.q051`

Because Topic 1 is foundational to later topics, incomplete objective mapping here would weaken the usefulness of later adaptive support and student-topic mastery stats.

### 6. [Positive] Prompt-asset handling for Digital Data is good.
All `7` digital-data prompt assets were linked successfully with `0` unresolved. Examples include:
- `digital-data.past_paper.topics_01_02.q006`
- `digital-data.past_paper.topics_01_02.q007`
- `digital-data.past_paper.topics_01_02.q013`
- `digital-data.past_paper.topics_01_02.q014`
- `digital-data.past_paper.topics_01_02.q017`
- `digital-data.past_paper.topics_01_02.q037`
- `digital-data.past_paper.topics_01_02.q038`

That is a strong result and shows the asset layer is doing genuine work here.

### 7. [Positive, with caution] I did not find a clear factual howler in Digital Data on the same level as the Network switch/router issue.
That is encouraging. The topic appears stronger on subject accuracy than Network Technologies. The larger problems here are structural and editorial:
- over-broad family grouping;
- misclassified true/false items;
- ambiguous or alternative answers left as raw strings; and
- explanation gaps.

### 8. [Medium] No Digital Data question is explanation-ready yet.
All `177` digital-data questions still carry `needs_explanation_enrichment`. So even where the prompt and answer are good, the student-facing teaching value is not there yet.

## Overall Assessment
`Digital data` looks stronger than `Network technologies` on raw factual reliability and stronger than `Spreadsheet applications` on transformed-item visibility, but it is still not safe for student release.

The main blockers are:
1. family grouping is too broad and would suppress valid coverage;
2. single-statement true/false items are structurally misclassified;
3. multiple short-answer items still rely on ambiguous or prose-only answer storage; and
4. the topic still lacks explanations throughout.

## Recommendation
Do not promote Digital Data toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. narrow family-code grouping substantially;
2. normalize single true/false items into a dedicated format;
3. extract structured accepted-answer rules for ambiguous, multi-answer, and alternative-answer short responses; and
4. add student-facing teaching explanations.
