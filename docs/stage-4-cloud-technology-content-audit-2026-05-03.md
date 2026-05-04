# Stage 4 Content Audit: Cloud Technology (2026-05-03)

## Scope
This audit checks the `Cloud technology` topic in the staged Stage 4 payload against the curated source materials. The goal is to determine whether the imported questions are factually accurate, faithful to source intent, and safe for a self-marking revision app.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_07_08_09.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_07_08_cyberspace_cloud.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_7_12.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged cloud-technology questions: `36`
- Prompt assets linked: `0`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `29` MCQ
  - `5` match_table
  - `1` fill_gap
  - `1` structured_response
- Current review flags:
  - `needs_explanation_enrichment`: `36`
  - `transformed_exam_item`: `19`
  - `practice_question_needs_source_normalization`: `15`
  - `needs_autograde_rule_review`: `2`
  - `needs_objective_mapping`: `1`

## Findings

### 1. [High] Cloud Technology is heavily dependent on transformed “advantages/disadvantages” MCQs, which weakens the original revision demand.
This topic has `19` transformed items, and many of them come from source prompts that originally asked students to:
- give two advantages;
- give two disadvantages;
- explain how cloud computing helps customers or companies; or
- discuss cloud gaming benefits/risks in a longer-response format.

Examples include:
- `cloud-technology.past_paper.topics_07_08_09.q001` and `q002`
- `q003` and `q004`
- `q005` and `q006`
- `q007` to `q010`
- `q012` and `q013`
- `q014` and `q015`
- `q018` and `q019`

The source QA report says the underlying cloud content is mostly accurate, but the transformed bank reduces much of it to isolated one-mark recognition. That makes the topic less useful as revision for the real exam, where students often need to generate advantages/disadvantages rather than simply recognise them.

### 2. [High] Supplementary mark-scheme-derived true/false items are again being mixed into the past-paper stream.
Two staged items are clearly labeled as supplementary derivations from the mark scheme rather than direct imported exam questions:
- `cloud-technology.past_paper.topics_07_08_09.q020`
- `cloud-technology.past_paper.topics_07_08_09.q021`

These are:
- `True or False: One advantage of cloud computing is that it can reduce a company's carbon footprint.`
- `True or False: Cloud computing requires no Internet connection to access data.`

These may be useful revision checks, but they should not sit indistinguishably inside the same `past_paper` stream as direct question-paper-derived items.

### 3. [High] Single-statement True/False items are again misclassified as `match_table`.
Examples include:
- `cloud-technology.past_paper.topics_07_08_09.q020`
- `cloud-technology.past_paper.topics_07_08_09.q021`
- `cloud-technology.practice_bank.topic_07_08_cyberspace_cloud.q010`
- `cloud-technology.practice_bank.topic_07_08_cyberspace_cloud.q011`

These are ordinary binary judgment prompts and should be represented as explicit true/false items, not as match-table records with raw `True` / `False` answers.

### 4. [Medium] The cloud practice item about file-streaming cloud gaming appears factually risky and should be reviewed before use.
`cloud-technology.practice_bank.topic_07_08_cyberspace_cloud.q010` states:
- `In file streaming cloud gaming, the user needs a computer with sufficient power and specification to execute the game.`
- staged answer: `True`

That claim is questionable in the way it is phrased. One of the main appeals of file-streaming cloud gaming is reduced dependence on high-spec local hardware. The prompt may be trying to distinguish file-streaming from video-streaming approaches, but as written it is risky and should not be trusted without checking the source fact file carefully.

### 5. [Medium] The practice item on cloud-gaming feedback is too open-ended for the current marking model.
`cloud-technology.practice_bank.topic_07_08_cyberspace_cloud.q014` asks:
- `Name the significant impact cloud gaming has on game designers' ability to gather feedback in real time.`
- staged answer: `It allows them to monitor user behaviour, performance and preferences (in real time)`

That is a plausible answer, but the prompt is quite open for a single raw-string answer in an auto-marked system. It needs either tighter wording or structured accepted-answer logic.

### 6. [Medium] Cloud objective mapping is almost complete, but not fully.
Only one staged cloud question still carries `needs_objective_mapping`:
- `cloud-technology.past_paper.topics_07_08_09.q009`

That is encouraging, but it still needs resolving if later adaptive guidance is to be fully dependable.

### 7. [Positive] The supporting QA report suggests the underlying cloud content is broadly reliable.
The QA report for Topics 7–12 is comparatively reassuring on this topic:
- 2018 Q9(c) rewrite is explicitly described as clearer for students
- 2019 Q7 is marked OK
- 2023 Q9(a)/(b)/(c) are marked OK
- 2024 Q2(a)/(b)/(c) are marked OK

So unlike some earlier topics, the raw cloud source does not appear to be the main problem.

### 8. [Positive] There are no prompt-asset issues.
This topic has `0` prompt assets and `0` unresolved assets. For cloud content, that appears acceptable.

### 9. [Medium] No cloud question is explanation-ready yet.
All `36` staged cloud questions still carry `needs_explanation_enrichment`, so the revision-teaching layer is still missing.

## Overall Assessment
`Cloud technology` is comparatively clean on raw factual quality, but it still is not safe for student release.

The biggest problems are:
1. too much of the topic has been flattened into single-choice recognition items;
2. supplementary mark-scheme spin-offs are mixed into the past-paper stream;
3. true/false items are structurally misclassified; and
4. at least one cloud-gaming practice claim is risky enough to require source re-checking.

## Recommendation
Do not promote cloud-technology questions toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. distinguish direct PPQ-derived items from supplementary mark-scheme spin-offs in metadata and review workflow;
2. normalize single true/false items into a dedicated format;
3. review the file-streaming cloud gaming statement carefully against the fact file; and
4. preserve more of the original advantage/disadvantage reasoning demand instead of reducing so much of the topic to one-mark MCQs.
