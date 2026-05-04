# Network Technologies Content Audit

Date: 2026-05-02

Scope:

- source pack review for Topic 6 (`Network technologies`)
- staged import output review for the same topic
- focus on fidelity, accuracy, self-markability, and student readiness

Source files reviewed:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_05_06.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

Generated payload reviewed:

- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Overall Verdict

`Network technologies` is **not yet student-ready**, even though the source ingestion itself is productive and much richer than the old prototype bank.

The import pipeline is successfully capturing the topic at scale:

- `84` staged questions for `network-technologies`
- `4` prompt assets
- `0` unresolved prompt assets for this topic

That is a strong technical base.

However, the current question set still has three important classes of risk:

1. some source-derived items are preserving apparent factual or answer-key problems
2. several imported formats are not yet in a safely self-markable structure
3. many transformed past-paper items still need editorial scrutiny to ensure they preserve exam intent

## Findings

### 1. The practice-bank source currently contains at least one clear answer-key problem, and the importer preserves it unchanged

In the practice-bank source:

- Q4 describes a switch as the "connection point for a group of computers" that organises communication between the file server and computers, with answer `C. Switch`
- Q5 then describes a "sophisticated switched hub" that holds computer addresses and forwards data efficiently, but the source answer is `C. Router`

That looks internally inconsistent. The Q5 wording strongly describes a switch, not a router.

Source reference:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

Imported question affected:

- `network-technologies.practice_bank.topic_05_06_hardware_networks.q005`

Why this matters:

- if we trust the source blindly, we import a wrong answer into the live bank
- this is exactly the kind of defect that could teach students the wrong concept

### 2. The same switch/router ambiguity appears again in the practice bank’s matching question

The practice-bank matching item:

- `network-technologies.practice_bank.topic_05_06_hardware_networks.q031`

maps:

- `Switch → 3` for the “connection point for a group of computers”
- `Router → 1` for the “sophisticated switched hub ... often used as a gateway”

This mixes two different ideas into the router definition and repeats the same conceptual confusion seen in Q5.

Source reference:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

Why this matters:

- this is not just a formatting issue; it is a conceptual inconsistency inside the source-derived practice bank
- the importer currently preserves it rather than surfacing it as suspect

### 3. Several Network match/true-false items are captured only as raw strings, not as safe self-marking structures

Examples:

- `network-technologies.past_paper.topics_05_06.q005`
- `network-technologies.past_paper.topics_05_06.q014`
- `network-technologies.past_paper.topics_05_06.q023`
- `network-technologies.past_paper.topics_05_06.q027`
- `network-technologies.past_paper.topics_05_06.q029`
- `network-technologies.past_paper.topics_05_06.q040`
- `network-technologies.past_paper.topics_05_06.q045`
- `network-technologies.past_paper.topics_05_06.q050`

These are staged as:

- prose in `stem`
- raw answer strings in `correct_answer_json.raw`

rather than a normalized structure such as:

- `pairs`
- `choices`
- `true_false_rows`

Why this matters:

- these are good exam-style questions in principle
- but in their current staged form they are not yet safely renderable or markable by the current app
- without transformation, they would be fragile and error-prone in student sessions

### 4. Fill-gap items in this topic are especially vulnerable under the current scoring rules

Examples:

- `network-technologies.past_paper.topics_05_06.q025`
- `network-technologies.past_paper.topics_05_06.q026`
- `network-technologies.past_paper.topics_05_06.q047`
- `network-technologies.past_paper.topics_05_06.q048`
- `network-technologies.past_paper.topics_05_06.q049`

These are actually good candidates for self-marking in concept. The problem is the current live scorer uses permissive substring logic for `fill_gap`.

Why this matters:

- answers like `NETWORK` / `APPLICATION` / `DEVICES` / `PROTOCOLS` need exact-but-reasonable marking
- the current scoring model is loose enough that partial fragments could be accepted inappropriately
- this is a scoring-quality issue, not a source-quality issue

### 5. Transformed exam items are common in this topic and need closer editorial checking before trust

This topic contains many imported past-paper items flagged as transformed, including:

- `network-technologies.past_paper.topics_05_06.q001`
- `network-technologies.past_paper.topics_05_06.q002`
- `network-technologies.past_paper.topics_05_06.q003`
- `network-technologies.past_paper.topics_05_06.q011`
- `network-technologies.past_paper.topics_05_06.q012`
- `network-technologies.past_paper.topics_05_06.q015`
- `network-technologies.past_paper.topics_05_06.q016`
- `network-technologies.past_paper.topics_05_06.q017`
- `network-technologies.past_paper.topics_05_06.q018`

These are not automatically wrong. Many are sensible conversions. But because they were turned from longer or differently shaped exam tasks into MCQ/fill-gap items, they are one of the highest editorial-risk groups.

Why this matters:

- students need revision that reflects the exam faithfully
- transformed questions can be useful, but only if they preserve the real concept and do not oversimplify the original demand

### 6. The topic is structurally strong on prompt assets

This is a positive finding.

For `network-technologies`, the importer resolved all prompt assets reviewed in this audit:

- `network-technologies.past_paper.topics_05_06.q010`
- `network-technologies.past_paper.topics_05_06.q014`
- `network-technologies.past_paper.topics_05_06.q020`
- `network-technologies.past_paper.topics_05_06.q040`

Asset resolution result:

- `4` assets
- `0` unresolved

Why this matters:

- unlike the older prototype, the new pipeline is successfully carrying the diagram layer for this topic
- that is essential for real exam-style revision

### 7. Explanation quality for this topic is still absent

Every staged Network question still has:

- `needs_explanation_enrichment`

Why this matters:

- even where the stem and answer are good, students are not yet receiving the teaching feedback needed for high-quality revision
- this is especially important for misunderstood pairs like `Internet vs WWW`, `router vs switch`, or topology advantages/disadvantages

## What I Trust In This Topic So Far

I am comfortable saying the following parts are promising:

- the source pack gives broad, relevant coverage of the topic
- the diagram-backed past-paper items are being carried into staging rather than lost
- the importer is preserving a large amount of usable exam-style material
- the topic’s objective coverage looks broadly sensible

## What I Do Not Yet Trust

I do **not** yet trust:

- the answer key of every practice-bank question
- the self-marking readiness of the imported `match_table`, `true/false`, and `fill_gap` items
- the editorial faithfulness of all transformed MCQ items
- the student-facing readiness of this topic without explanations

## Recommendation Before Promotion

Before `Network technologies` is allowed anywhere near student sessions in the rebuilt bank, it should go through this sequence:

1. answer-key verification pass against source and notes
2. transformation pass from raw staged structures into runtime-safe self-marking structures
3. explanation enrichment
4. transformed-item editorial review
5. final topic-level QA sweep

## Bottom Line

This topic is **not a failure**. The ingestion work is meaningful and the source coverage is strong.

But it is also **not yet safe enough** to trust as a student-ready revision topic. The biggest immediate concern is that the current pipeline can faithfully preserve incorrect or internally inconsistent source answers unless we add a stronger verification layer before promotion.
