# Stage 4 Content Audit: Software (2026-05-03)

## Scope
This audit checks the `Software` topic in the staged Stage 4 payload against the curated source materials. The goal is to determine whether the imported questions are factually sound, faithful to the source intent, and safe for use in an auto-marked revision app.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_01_02.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_02_03_software_database.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged software questions: `53`
- Prompt assets linked: `0`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `30` MCQ
  - `12` match_table
  - `6` short_text
  - `5` fill_gap
- Current review flags:
  - `needs_explanation_enrichment`: `53`
  - `practice_question_needs_source_normalization`: `35`
  - `needs_autograde_rule_review`: `11`
  - `transformed_exam_item`: `7`
  - `needs_objective_mapping`: `5`

## Findings

### 1. [High] Some transformed software questions weaken the original exam demand too far and become low-value matching tasks.
Two imported past-paper items are especially weak in their transformed form:
- `software.past_paper.topics_01_02.q001`
- `software.past_paper.topics_01_02.q009`

Both come from source prompts asking students to list resources managed by system software / the operating system. In the staged version, they become match tasks with only two examples, and both answers map to the same bucket:
- `1 → A; 2 → A`

That means the question now effectively asks students to confirm that both examples are managed resources, while the `NOT managed` option is unused. This is technically still markable, but it is a weak transformation and a poor revision experience compared with the original intent.

### 2. [High] One transformed software item appears to introduce extra content beyond the original source demand.
`software.past_paper.topics_01_02.q008` comes from a source item originally described as `List two utility programs`, but the staged version becomes a three-part match question covering:
- disk defragmenter
- anti-virus
- backup

That is not automatically wrong, but it does go beyond a simple adaptation of the original prompt. It broadens the content and adds a more elaborate structure than the source required. For an exam-revision app, that needs explicit review because students may assume every imported past-paper-derived item reflects the original exam demand more closely than it actually does.

### 3. [High] Several single-statement software True/False items are again misclassified as `match_table`.
Examples include:
- `software.practice_bank.topic_02_03_software_database.q022`
- `software.practice_bank.topic_02_03_software_database.q023`
- `software.practice_bank.topic_02_03_software_database.q024`
- `software.practice_bank.topic_02_03_software_database.q025`

These are ordinary binary statements such as:
- `ROM is volatile memory that loses its contents when the computer is switched off.`
- `Larger RAM capacity will mean faster processing speeds.`
- `Backups of software should be stored separately from the computer to protect against dangers such as fire.`

As with other topics, these should be represented as explicit true/false items rather than pseudo-match records with raw answers like `True` or `False`.

### 4. [High] One practice-bank software question is phrased in a technically careless way that should not be trusted without review.
`software.practice_bank.topic_02_03_software_database.q026` currently asks:

`The two microchips that make up the main memory in a computer's CPU are called __________ and __________.`

Stored answer:
- `RAM; ROM`

The wording is problematic. RAM and ROM are not normally described as the two microchips that make up the main memory in a computer's CPU. Even if the source intended to contrast RAM and ROM, the phrasing is careless enough that it risks teaching students an inaccurate hardware/software relationship.

### 5. [Medium] Several software short-answer items are useful, but not yet safely auto-markable.
Examples include:
- `software.practice_bank.topic_02_03_software_database.q028`
  - `Any 2 from: disk defragmenting; task scheduling; backup; restoring data; antivirus / virus checking; file compression.`
- `software.practice_bank.topic_02_03_software_database.q029`
  - `Any 2 from: processing bank statements; processing credit card statements; generating gas/electricity billing information; reading meter readings.`
- `software.practice_bank.topic_02_03_software_database.q032`
  - `ROM (Read Only Memory)`
- `software.practice_bank.topic_02_03_software_database.q033`
  - `Cache (memory)`
- `software.past_paper.topics_01_02.q017`
  - `Booting (also accept Booting up, Bootup, Start up sequence)`

These are all potentially good revision prompts, but their accepted-answer logic is still trapped in raw text rather than a structured auto-marking contract.

### 6. [Medium] Software objective mapping is still incomplete.
The following staged software items remain flagged `needs_objective_mapping`:
- `software.practice_bank.topic_02_03_software_database.q002`
- `software.practice_bank.topic_02_03_software_database.q018`
- `software.practice_bank.topic_02_03_software_database.q019`
- `software.practice_bank.topic_02_03_software_database.q024`
- `software.practice_bank.topic_02_03_software_database.q034`

This is not a topic-level failure, but it would weaken later adaptive support if left unresolved.

### 7. [Positive] The transformed-item flags are at least surfacing risk more honestly here than in some other topics.
The current staged software payload flags `7` items as `transformed_exam_item`. That is a healthier state than the spreadsheet topic, where many converted items were not being surfaced at all. The problem here is therefore more about the *quality* of some transformations than about invisible risk.

### 8. [Positive] The software topic does not appear to depend on prompt images.
There are `0` linked prompt assets and `0` unresolved assets. For this topic, that appears acceptable rather than a missing-content problem.

### 9. [Medium] No software question is explanation-ready yet.
All `53` software questions still carry `needs_explanation_enrichment`. So even the better items are not yet providing the teaching feedback students need.

## Overall Assessment
`Software` is not as visually or structurally complex as some other topics, but it still is not safe for student release.

The most important issues are:
1. some transformed past-paper items have been weakened too far;
2. several true/false questions are structurally misclassified;
3. at least one practice question has technically careless wording; and
4. accepted-answer handling is still too loose or too raw for fair self-marking.

## Recommendation
Do not promote software questions toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. rework weak transformed match questions so they preserve more of the original exam demand;
2. normalize single true/false items into a dedicated structure;
3. correct or replace the `RAM/ROM in a computer's CPU` practice prompt; and
4. extract structured accepted-answer rules for short-answer items with alternatives or `Any X from` logic.
