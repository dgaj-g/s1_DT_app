# Database Applications Content Audit

Date: 2026-05-03

Scope:

- source pack review for Topic 3 (`Database applications`)
- staged import output review for the same topic
- focus on fidelity, completeness, self-markability, and student readiness

Source files reviewed:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_02_03_software_database.md`

Generated payload reviewed:

- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Overall Verdict

`Database applications` is in a **better factual state than Network technologies**, but it is still **not student-ready**.

The main risk pattern is different here:

- fewer obvious factual answer-key problems were found in the first-pass audit
- but there are still important self-marking, transformation, and review-gate problems

Topic-level snapshot:

- `120` staged questions
- `5` prompt assets
- `0` unresolved prompt assets
- `82` MCQ
- `15` short text
- `14` match
- `9` fill gap
- `4` still needing objective mapping

## Findings

### 1. The transformation-review heuristic is under-reporting converted Database items

The source markdown contains many lines such as:

- `converted from Short Answer`
- `converted from 2-mark Short Answer`

But the current transformed-item detector only looks for phrases such as:

- `converted to mcq`
- `split into`
- `originally`
- `transformed`

As a result, Database items that have clearly been transformed are not currently being flagged as transformed in the staging payload.

Files:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

Why this matters:

- these converted items should receive closer editorial scrutiny
- at present they can look safer than they really are simply because the trigger phrase is not being detected

### 2. Some Database questions carry alternative accepted answers in prose, but the staging layer does not yet structure them for marking

Examples:

- `database-applications.past_paper.topics_03_04.q003`
  - answer text includes `accept: uniquely identifies a member / individual`
- `database-applications.past_paper.topics_03_04.q045`
  - answer text includes `accept: ArtistName`
- `database-applications.past_paper.topics_03_04.q046`
  - answer text includes `accept: =RO1`

At present, those are carried into staging as raw strings, not as a structured accepted-answer list.

Why this matters:

- these are exactly the kinds of valid alternatives students are likely to type
- unless transformed into structured acceptance rules later, the current runtime would not mark them reliably

### 3. At least one imported past-paper item currently contains impossible instructions as staged

Question:

- `database-applications.past_paper.topics_03_04.q042`

Current staged prompt:

- `Complete the sentences about databases using these words: RECORD; TABLE; COLUMN. Each word is used once only.`
- then only two blanks are provided

Current answer:

- `(1) Table; (2) Record`

This creates an impossible instruction as staged:

- three supplied words
- two blanks
- “each word is used once only”

Why this matters:

- even if this came from the source pack as written, it is not acceptable for student use in this form
- it would confuse students and undermine confidence in the app

### 4. Match and true/false items are still staged as raw prose rather than structured runtime-safe objects

Examples:

- `database-applications.past_paper.topics_03_04.q007`
- `database-applications.past_paper.topics_03_04.q016`
- `database-applications.past_paper.topics_03_04.q027`
- `database-applications.past_paper.topics_03_04.q029`
- `database-applications.past_paper.topics_03_04.q034`
- `database-applications.past_paper.topics_03_04.q035`

These are strong revision questions in principle, but they are currently staged as:

- text prompt
- raw answer string

rather than as normalized pairs/rows/options.

Why this matters:

- this topic contains many good database-structure and tool-identification tasks
- but until they are normalized, they are still not safe to render and mark automatically

### 5. The topic uses good diagram-backed prompts, and asset resolution is strong

Positive finding:

Resolved figure-backed questions include:

- `database-applications.past_paper.topics_03_04.q001`
- `database-applications.past_paper.topics_03_04.q007`
- `database-applications.past_paper.topics_03_04.q017`
- `database-applications.past_paper.topics_03_04.q039`
- `database-applications.past_paper.topics_03_04.q053`

Result:

- `5` prompt assets
- `0` unresolved

Why this matters:

- the pipeline is successfully preserving the visual/database-schema layer of the exam experience
- that is a significant strength compared with the old prototype bank

### 6. Practice-bank content appears broadly useful, but still needs source-normalization and terminology review

The practice bank is giving useful additional coverage for:

- SQL
- validation
- file transfer
- ER diagrams
- data types
- big data

However, it still carries `practice_question_needs_source_normalization` throughout, and some terminology should be reviewed carefully before student release.

Example:

- `database-applications.practice_bank.topic_02_03_software_database.q031`
  - option `BOOLE` is used where students may expect `BOOLEAN`

This may be source terminology rather than a strict factual error, but it still deserves review before publication.

### 7. Explanation quality remains absent throughout the topic

All `120` staged Database questions still require explanation enrichment.

Why this matters:

- database concepts often depend on precise distinctions:
  - record vs field
  - key field vs foreign key
  - query vs report
  - presence vs range vs type vs format checks
- these are exactly the areas where a short teaching explanation would add revision value

## What I Trust In This Topic So Far

I am comfortable saying the following:

- the imported database bank has broad and useful coverage
- the factual quality in the first-pass review appears stronger than the Network practice bank
- prompt-image handling is working well
- the source pack provides a strong basis for a serious revision topic

## What I Do Not Yet Trust

I do **not** yet trust:

- the current transformed-item review coverage
- the self-marking readiness of short-answer items with alternative accepted answers
- the self-marking readiness of raw match/true-false items
- any item that presents impossible or self-contradictory instructions after staging

## Recommendation Before Promotion

Before `Database applications` is allowed into a live student bank, it should go through:

1. transformed-item detection fix
2. accepted-answer extraction into structured marking rules
3. normalization of match/true-false structures
4. review of impossible or contradictory prompts
5. explanation enrichment
6. final topic QA

## Bottom Line

This topic is closer to trustworthy than `Network technologies` on raw factual quality, but it still fails the student-readiness test at present.

The biggest issue here is not obvious wrong facts so much as the gap between:

- a well-captured source question
and
- a safely auto-markable student experience

That gap still needs careful work before students should rely on this topic for exam revision.
