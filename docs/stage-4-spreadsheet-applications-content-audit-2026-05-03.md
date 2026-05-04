# Stage 4 Content Audit: Spreadsheet Applications (2026-05-03)

## Scope
This audit checks the `Spreadsheet applications` topic in the staged Stage 4 payload against the curated source materials. The goal is to determine whether the imported questions are:
- factually accurate;
- faithful to the source material;
- safely auto-markable; and
- appropriate for eventual adaptive delivery.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_04_spreadsheet.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged spreadsheet questions: `107`
- Prompt assets linked: `8`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `79` MCQ
  - `14` match_table
  - `9` short_text
  - `5` fill_gap
- Current review flags:
  - `needs_explanation_enrichment`: `107`
  - `needs_objective_mapping`: `8`
  - `needs_autograde_rule_review`: `14`
  - `practice_question_needs_source_normalization`: `50`

## Findings

### 1. [High] Transformed spreadsheet past-paper items are being materially under-reported by the review gate.
The source pack contains a large number of spreadsheet items explicitly labeled as converted exam questions, for example:
- `2018 Q7(a), converted from Short Answer`
- `2018 Q7(c)(iii), converted from 2-mark Describe`
- `2019 Q8(d), converted from Short Answer`

Within Topic 4 alone, the source contains `41` `converted from ...` markers, yet the current payload summary reports `0` transformed spreadsheet questions. This is not just a cosmetic issue. It means one of the biggest content-risk classes in this topic is not being surfaced properly for editorial review.

Examples from `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`:
- Q1: formatting on merged headers
- Q5: absolute cell reference advantage
- Q14: chart axis range matching

These are strong revision items in principle, but they need stricter review because they were rewritten from longer original exam prompts.

### 2. [High] Several simple True/False practice items are currently misclassified as `match_table` questions.
The practice source contains straightforward single-statement true/false items:
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q029`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q030`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q031`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q032`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q033`

Examples:
- `All formulae in a spreadsheet must start with an equals sign (=).`
- `A row is a vertical group of cells named after a letter.`
- `A macro can be activated by a mouse click or by pressing a key.`

These are currently staged as `match_table` with `correct_answer_json.raw = 'True'` or `'False'`. That is not the right structural model. These should become explicit true/false or binary-choice items. Leaving them as pseudo-match items would make the question contract less predictable and creates unnecessary risk for rendering and scoring.

### 3. [High] Several spreadsheet short-answer items are still not safely auto-markable in their current staged form.
The current staged payload stores many answers as raw prose or exact formula strings, without structured accepted-answer rules. Important examples include:
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q039`
  - `Any 2 from: Age must be a whole number which is less than 18; Exam Result must be between 0 and 100; Gender must be from a list which consists of Male and Female.`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q040`
  - `Any 3 from: Bar Chart; Line Chart; Pie Chart; Scatter Graph.`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q041`
  - `Any 2 from: change font ... ; change cell background colour; add a border ... ; merge & centre ...`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q042`
  - `=D1-C1`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q043`
  - `=AVERAGE(B2:B20)`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q045`
  - `CSV (Comma Separated Values) file`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q046`
  - `$B$2`
- `spreadsheet-applications.past_paper.topics_03_04.q054`
  - `B9:D9`

The topic content itself is mostly reasonable here. The risk is in the self-marking layer. Exact-string marking will be too brittle for list-based answers and may be too strict even for formula/range syntax if students include benign spacing or accepted shorthand. These items need normalized accepted-answer structures before student release.

### 4. [Medium] Spreadsheet objective mapping is improved, but there are still unresolved items in revision-relevant areas.
The following spreadsheet items remain flagged `needs_objective_mapping`:
- `spreadsheet-applications.past_paper.topics_03_04.q028`
- `spreadsheet-applications.past_paper.topics_03_04.q053`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q024`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q032`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q033`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q044`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q049`
- `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q050`

This is not catastrophic, but it matters because spreadsheet revision is heavily skill-based. Weak or missing objective mapping would make later adaptive guidance less trustworthy.

### 5. [Medium] The 2025 true/false spreadsheet item is revision-worthy, but not yet staged in the cleanest structure.
`spreadsheet-applications.past_paper.topics_03_04.q053` is currently staged as `match_table` with a raw answer string:
- `Enable users to perform calculations → True`
- `Cannot assist the user in making informed choices or predictions → False`
- `Offer tools to create charts and graphs that visually represent data → True`

This is a good question for revision, but it would be better represented as a true/false statement-set with row-level answer structure rather than a prose bundle in `correct_answer_json.raw`.

### 6. [Positive] Prompt-image handling for spreadsheet past-paper items is strong.
The importer linked all `8` spreadsheet prompt assets with `0` unresolved. Examples include:
- `spreadsheet-applications.past_paper.topics_03_04.q001`
- `spreadsheet-applications.past_paper.topics_03_04.q011`
- `spreadsheet-applications.past_paper.topics_03_04.q015`
- `spreadsheet-applications.past_paper.topics_03_04.q018`
- `spreadsheet-applications.past_paper.topics_03_04.q028`
- `spreadsheet-applications.past_paper.topics_03_04.q036`
- `spreadsheet-applications.past_paper.topics_03_04.q044`
- `spreadsheet-applications.past_paper.topics_03_04.q054`

This is one of the strongest parts of the current spreadsheet import and is a meaningful improvement over the older prototype.

### 7. [Positive, with caution] I did not find an obvious factual howler in the spreadsheet source on the same level as the Network switch/router issue.
That is encouraging. The spreadsheet practice bank appears broadly usable as a source base. The bigger problem in this topic is not raw subject accuracy; it is that many valid questions are not yet transformed into a safe, student-ready auto-marking structure.

### 8. [Medium] No spreadsheet item is explanation-ready yet.
Every spreadsheet question still carries `needs_explanation_enrichment`. So even where the prompt and answer are good, the revision-teaching layer students need is still missing.

## Overall Assessment
`Spreadsheet applications` is in better shape than `Network technologies` on raw factual quality, and the prompt-asset handling is strong. However, it is still not safe to treat this topic as student-ready.

The main blockers are:
1. transformed exam items are under-flagged by the review layer;
2. several true/false items are structurally misclassified;
3. formula/range/list-style short answers are not yet supported by fair auto-marking rules; and
4. explanations are absent throughout.

## Recommendation
Do not promote spreadsheet questions toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. tighten transformed-item detection so spreadsheet conversions are surfaced honestly;
2. normalize true/false statement items into a dedicated structure rather than pseudo-match items;
3. create structured accepted-answer rules for formula, range, and “Any X from” answers; and
4. add student-facing teaching explanations.
