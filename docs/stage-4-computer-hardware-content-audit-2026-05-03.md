# Stage 4 Content Audit: Computer Hardware (2026-05-03)

## Scope
This audit checks the `Computer hardware` topic in the staged Stage 4 payload against the curated source materials. The aim is to determine whether the imported questions are factually accurate, faithful to the source material, and safe for auto-marked revision.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_05_06.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_5_6.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged computer-hardware questions: `80`
- Prompt assets linked: `5`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `52` MCQ
  - `13` match_table
  - `7` fill_gap
  - `6` short_text
  - `2` structured_response
- Current review flags:
  - `needs_explanation_enrichment`: `80`
  - `practice_question_needs_source_normalization`: `32`
  - `transformed_exam_item`: `29`
  - `needs_autograde_rule_review`: `15`
  - `needs_objective_mapping`: `7`

## Findings

### 1. [High] The practice-bank fetch-execute/register material contains at least one clear conceptual error and should not be trusted as-is.
The strongest problem in this topic is the practice-bank CPU/register section:
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q027`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q028`

`q027` asks:
- `Name the CPU component that stores each piece of data in a unique memory address so the CPU can retrieve it immediately.`
- staged answer: `Immediate Access Store`

That wording is conceptually poor. It blurs together memory addressing and immediate access storage in a way that risks teaching the wrong model of how CPU components and main memory behave.

`q028` is worse. It stages this answer key:
- `Program Counter → 2`
- `MAR → 4`
- `MDR → 3`
- `ALU → 1`

But the definitions include:
- `3. Temporarily holds the instruction once it has been fetched (all data from memory to CPU goes via this)`
- `4. Stores the current instruction or data being executed`

This is muddled. `MAR → 4` is not a safe mapping, and definition 3 also mixes ideas in a way that does not sit cleanly with the standard roles of MDR and the current instruction register. This is a genuine content-quality problem, not just a formatting issue.

### 2. [High] Several single-statement hardware True/False items are again misclassified as `match_table`.
Examples include:
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q021`
- `q022`
- `q023`
- `q024`

These are ordinary binary prompts such as:
- `ROM is volatile memory, meaning data is lost when the computer is switched off.`
- `Registers are much faster to access than RAM because they have to be accessed so often.`
- `A Hard Disk Drive is faster than RAM.`

As with other topics, these should be represented as explicit true/false items rather than match-table items with raw `True`/`False` answers.

### 3. [High] The transformed hardware bank is very large, so editorial transformation quality matters a great deal here.
This topic has `29` questions flagged `transformed_exam_item`, which is a large proportion of the staged hardware bank.

Examples include:
- `computer-hardware.past_paper.topics_05_06.q001` to `q003`
  - one 3-mark laptop specification table split into separate MCQs
- `q014` and `q015`
  - a `list two` fetch-execute/register question split into two MCQs
- `q022` and `q023`
  - a 4-mark QWC-style CPU-components item split into isolated MCQs
- `q030` and `q031`
  - a 4-mark device-classification item split into smaller parts
- `q044` to `q046`
  - a 3-mark fill-in split into three separate 1-mark items

These are not automatically wrong, and in a few cases the transformed wording is actually cleaner than the source pack's missing-context form. But because so much of this topic has been converted, the risk of the student seeing a weaker or distorted version of the original demand is high.

### 4. [Medium] One practice-bank hardware prompt is awkward enough that it should be normalized even if the intended answer is accepted.
`computer-hardware.practice_bank.topic_05_06_hardware_networks.q025` currently reads:
- `The ALU is a vital part and end of the ____________-____________ cycle.`
- answer: `fetch-execute`

The intended concept is obvious, but the wording is clumsy enough that it would feel careless in a student-facing app. This is not a catastrophic defect, but it reinforces the pattern that parts of the hardware practice source need stronger normalization before promotion.

### 5. [Medium] Some hardware answers are reasonable but still not safely auto-markable in their current staged form.
Examples include:
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q032`
  - `Limited range / limited battery life`
- `computer-hardware.past_paper.topics_05_06.q007`
  - `16 GB`
- `computer-hardware.past_paper.topics_05_06.q010`
  - `Arithmetic Logic Unit`
- `computer-hardware.past_paper.topics_05_06.q040`
  - `Immediate Access Store`

The factual side of these may be acceptable, but the staged answers are still stored as raw strings rather than structured accepted-answer rules, which means the runtime could still mark good student wording unfairly.

### 6. [Medium] Hardware objective mapping is not complete in some important CPU/storage areas.
The following items remain flagged `needs_objective_mapping`:
- `computer-hardware.past_paper.topics_05_06.q028`
- `computer-hardware.past_paper.topics_05_06.q032`
- `computer-hardware.past_paper.topics_05_06.q040`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q001`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q009`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q017`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q031`

Given how central CPU, memory, storage, and peripherals are to Topic 5, incomplete mapping here would weaken future adaptive support.

### 7. [Positive] Prompt-asset handling is strong, and the importer appears to have repaired some source-context problems.
All `5` hardware prompt assets are linked with `0` unresolved:
- `computer-hardware.past_paper.topics_05_06.q001`
- `q002`
- `q003`
- `q007`
- `q010`

This matters because the QA report for Topics 5/6 notes several source-pack cohesion/context issues, especially around 2025 and CPU-component prompts. In several cases, the staged versions are actually better framed than the raw source-pack wording. That is a real positive.

### 8. [Positive, with caution] I did not find a factual defect on the scale of the Network switch/router error in the transformed past-paper side.
The biggest content risk in this topic is not the transformed past-paper side by itself; it is the hardware practice-bank CPU/register material. The past-paper-derived hardware content still needs scrutiny, but it does not currently look as error-prone as the weakest Network practice items.

### 9. [Medium] No hardware question is explanation-ready yet.
All `80` hardware questions still carry `needs_explanation_enrichment`, so the teaching-feedback layer remains absent.

## Overall Assessment
`Computer hardware` has better asset handling and better context recovery than some other topics, but it still is not safe for student release.

The strongest blockers are:
1. the practice-bank fetch-execute/register content is unreliable;
2. single true/false items are structurally misclassified;
3. the topic contains a very large volume of transformed exam material that still needs editorial trust-checking; and
4. short-answer marking remains too raw.

## Recommendation
Do not promote computer-hardware questions toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. correct or remove the unreliable hardware practice-bank register/fetch-execute items;
2. normalize single true/false items into a dedicated structure;
3. apply stricter review to transformed hardware exam items because they make up such a large share of the topic; and
4. add structured accepted-answer rules and explanations.
