# Stage 4 Import Rules And Template

This document turns the Stage 3 metadata ideas into a practical import policy.

The goal is to make future question imports manageable without expecting the teacher to manually assign:

- `question_family_code` for every question
- `selection_weight` for every question
- visual-asset links by hand inside the live database

The system should do the first pass automatically, then allow light owner review where needed.

## Core Principle

The teacher should **not** have to sit and hand-tag hundreds of questions.

The intended workflow is:

1. prepare structured question data
2. import into staging
3. let the importer propose metadata
4. review only exceptions or a small sample
5. publish approved content

## What Gets Decided Automatically

The importer should automatically propose:

- `question_family_code`
- `selection_weight`
- `dedupe_fingerprint`
- basic asset linkage for supporting images

## What The Teacher Should Be Able To Override

The content owner should be able to override:

- the proposed family code
- the proposed weight
- the proposed objective mapping
- the asset order and role

But those should be refinements, not required manual work for every row.

## Question Family Code Policy

### Purpose

`question_family_code` exists to stop the app asking students the same core question twice in one session, even if the wording varies.

### Definition

Questions belong to the same family when they test the same underlying concept and answer logic closely enough that a student would reasonably feel:

> “I’ve basically just been asked that again.”

### What The Importer Should Use To Propose It

The importer should build a proposed family code from four layers:

1. `topic_slug`
2. `primary_objective_code`
3. `concept_key`
4. `interaction_key`

Suggested format:

```text
<topic_slug>.<objective_code>.<concept_key>.<interaction_key>
```

Example family codes:

```text
network-technologies.topology.bus.identify
network-technologies.media.bluetooth.sequence
database-applications.keys.primary.identify
spreadsheet-applications.formula.sum.construct
```

### How To Derive `concept_key`

`concept_key` should be derived from:

- normalized tags if available
- source objective wording
- repeated keywords in the stem
- correct answer concept

Examples:

- “bus”, “ring”, “star”
- “router”, “switch”, “nic”
- “bluetooth”, “wi-fi”, “5g”, “fibre”
- “primary-key”, “validation”, “query”, “sort”
- “formula”, “cell-reference”, “chart”, “lookup”

### How To Derive `interaction_key`

`interaction_key` should describe the response style or task pattern, not the content.

Recommended values:

- `identify`
- `choose`
- `match`
- `sequence`
- `label`
- `classify`
- `complete`
- `true-false`
- `compare`
- `apply`

Examples:

- “Which medium connects a phone to headphones?” -> `choose`
- “Put these steps in order” -> `sequence`
- “Match each item to the correct term” -> `match`
- “Which label belongs at point 3?” -> `label`

### When Two Questions Should Share A Family

They should share a family if all of these are true:

- same topic
- same main objective
- same concept
- same essential answer logic

Example:

- “Which topology uses one backbone cable?”
- “Choose the correct description of a bus network”
- “Identify the bus topology statement”

Those are not identical stems, but they are close enough that the app should normally avoid pairing them in one session.

### When Two Questions Should Not Share A Family

They should stay separate if they test meaningfully different performance, even inside the same concept.

Example:

- identifying a bus topology definition
- labelling a bus topology diagram
- analysing a bus topology disadvantage in a scenario

All three are related, but they may deserve different families if the answer behaviour is genuinely different.

### Fallback Rule

If the importer cannot confidently assign a shared family, it should generate a unique family code for that one question rather than risk a bad grouping.

## Selection Weight Policy

### Purpose

`selection_weight` controls how likely an eligible question is to be chosen once the session picker has already filtered by:

- topic
- difficulty
- objectives
- recency
- no repeated question id
- no repeated family code

It is not a difficulty score.
It is not a quality judgment shown to students.
It is just a controlled-randomisation aid.

### Default Rule

Every imported question should start with:

```text
selection_weight = 1.0
```

That is the baseline and should be used widely.

### Automatic Adjustment Rule

The importer should only adjust away from `1.0` in obvious cases.

Recommended starting rules:

#### Primary exemplar in a family

If a family has one strong “canonical” question, mark it:

```text
1.10
```

#### Secondary alternate in the same family

If a question is a clear alternate variant of the same family:

```text
0.90
```

#### Third or later close variant in the same family

If there are many similar variants:

```text
0.75
```

#### Visually important exam-practice question

If a question includes a meaningful diagram/table/screenshot that the exam regularly expects students to interpret:

```text
1.05
```

This is a gentle lift, not a dramatic one.

### What Not To Do

Do not try to finely hand-tune all weights before launch.

That would waste time and create false precision.

The practical launch rule is:

- most questions stay at `1.0`
- obvious primary/alternate cases get small automatic differences
- later QA can adjust a few if needed

## Dedupe Fingerprint Policy

Each staged question should also get a `dedupe_fingerprint`.

Purpose:

- catch near-identical imports before they go live
- help identify repeated past-paper extractions or duplicated practice items

Suggested fingerprint inputs:

- normalized stem
- normalized correct answer
- topic
- format

This is for import QA, not student-facing logic.

## Intelligent Randomisation Policy

Later, when the session picker is rebuilt, it should use this order:

1. filter to eligible questions
2. remove any already-used question ids in that session
3. remove any already-used family codes in that session
4. balance across objectives where possible
5. balance across formats where possible
6. choose among the remaining pool using `selection_weight`

That means:

- exact duplicates are blocked
- near-duplicates are blocked
- sessions stay varied
- weights guide the final choice without dominating it

## Structured Import Format

The cleanest future import format is an Excel workbook or a zipped CSV bundle with **two core sheets/files**:

1. `questions`
2. `question_assets`

An optional third sheet can hold notes or batch metadata, but the first two are the important ones.

## Questions Sheet

Recommended columns:

| Column | Required | Purpose |
|---|---|---|
| `question_external_id` | yes | Stable row id within the import batch |
| `topic_title` | yes | Must match one of the 12 agreed topic titles exactly |
| `objective_code` | recommended | Primary learning objective code |
| `difficulty` | yes | `easy`, `medium`, or `expert` |
| `format` | yes | e.g. `mcq`, `match_table`, `drag_drop`, `structured_response` |
| `adaptive_tier` | optional | `support`, `core`, or `challenge`; default `core` |
| `stem` | yes | Main question wording |
| `options_json` | conditional | Answer options for MCQ/matching/select formats |
| `correct_answer_json` | yes | Machine-readable answer |
| `markscheme_points_json` | recommended | Key marking points or structured answer parts |
| `explanation` | yes | Student-facing teaching explanation |
| `max_marks` | optional | Default `1` |
| `content_blocks_json` | optional | Rich content blocks if the question needs them |
| `response_schema_json` | optional | Defines answer structure |
| `autograde_rules_json` | optional | Marking logic metadata |
| `tags_json` | optional | Topic/concept tags |
| `source_kind` | optional | `past_paper`, `mark_scheme`, `practice_bank`, `fact_file`, `teacher_note` |
| `source_title` | optional | Human-readable source label |
| `source_file_name` | optional | Original document/file name |
| `source_locator` | optional | Page/section/slide reference |
| `teacher_notes` | optional | Private owner notes |
| `question_family_code` | optional | Leave blank if importer should propose it |
| `selection_weight` | optional | Leave blank for default rules |

### Important Guidance

For most future imports, the teacher should be able to leave these blank:

- `question_family_code`
- `selection_weight`

The importer should populate them automatically unless a specific value is supplied.

## Question Assets Sheet

Recommended columns:

| Column | Required | Purpose |
|---|---|---|
| `question_external_id` | yes | Links asset row back to the question |
| `asset_external_id` | yes | Unique id for the asset row in the batch |
| `asset_kind` | yes | `diagram`, `table_image`, `screenshot`, `figure`, `chart`, `photo` |
| `asset_role` | yes | `prompt`, `option`, `feedback`, `reference` |
| `file_name` | yes | Source image file name |
| `storage_path` | optional | Can be generated during upload if omitted |
| `mime_type` | optional | Image mime type if known |
| `alt_text` | yes | Accessibility text |
| `caption` | optional | Display caption |
| `display_order` | optional | Default `1` |
| `block_key` | optional | Link asset to a specific content block |
| `source_locator` | optional | Original page/slide/figure locator |

### Supporting Image Rule

If a question depends on a visual for proper exam-style practice, that visual should be imported as an asset row rather than hidden inside free-text notes.

That is the agreed place for:

- diagrams
- screenshots
- scanned prompt visuals
- tables rendered as images
- option images where relevant

## Import Review Burden

The intended review burden should be light.

The teacher should mainly review:

- questions flagged for uncertain family grouping
- questions flagged as likely duplicates
- questions missing required assets
- questions with missing objective mapping

The teacher should **not** be expected to audit every family code and every weight line-by-line before the importer is useful.

## Practical Launch Position

For the first full rebuild, the sensible launch rule is:

- auto-generate family codes
- default almost all weights to `1.0`
- lower clear alternates slightly
- keep owner review focused on flagged edge cases

That gives the app a strong enough session-selection foundation without turning metadata into a huge manual admin burden.
