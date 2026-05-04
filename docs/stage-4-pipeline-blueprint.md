# Stage 4 Pipeline Blueprint

This document describes the first implementation pass for Stage 4.

The purpose of Stage 4 is to convert the curated Unit 1 source pack into a
staged import bundle that can later be reviewed and promoted into the Stage 3
schema.

## Source Pack Used

Primary source folder:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project`

Useful source layers inside that folder:

- `_automark/markdown/`
  - curated past-paper-derived auto-markable content
- `_automark/figures/`
  - supporting prompt visuals for those questions
- `_practice_questions/`
  - additional practice questions by topic
- `_qa/`
  - quality notes about cohesion, missing context, and figure dependencies
- fact-file PDFs
  - official content support for future enrichment and checking

## Stage 4 Goal

The Stage 4 importer should not write live questions directly into Supabase.

Instead it should produce a normalized bundle that maps cleanly to:

- `import_batches`
- `staged_questions`
- `staged_question_assets`

That keeps the workflow safe and reviewable.

## Current Stage 4 Scripts

First scaffold script:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`

Accuracy-gate follow-on:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-accuracy-gate.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-objective-mapping-framework.md`

The bundle builder currently:

1. reads the curated markdown topic files
2. parses question headings, answers, options, figures, and list blocks
3. emits normalized question records
4. emits linked asset records for figure-backed questions
5. proposes:
   - topic slug
   - difficulty
   - format
   - adaptive tier
   - objective codes
   - `question_family_code`
   - `selection_weight`
   - `dedupe_fingerprint`

The second script then:

1. reads the normalized bundle
2. classifies structural and content-review risk
3. assigns review flags and review priority
4. separates `draft` from `ready_for_review`
5. produces a payload aligned to the Stage 3 staging tables

## Output

Default output path:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`

This output is a staging artifact, not a published content file.

## Command

Run from the repo root:

```zsh
python3 ./scripts/build_stage4_import_bundle.py --pretty
```

Optional overrides:

```zsh
python3 ./scripts/build_stage4_import_bundle.py \
  --source-root "/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project" \
  --output "/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json" \
  --pretty
```

## What The Script Produces

Each question record includes:

- external id
- topic title and slug
- source set (`past_paper` or `practice_bank`)
- source file and locator
- marks
- proposed difficulty
- proposed question format
- proposed adaptive tier
- structured content blocks
- raw answer payload
- objective code hints
- proposed family code
- default selection weight
- dedupe fingerprint

Each asset record includes:

- linked question external id
- asset kind
- asset role
- source image file name
- relative source path
- proposed storage path
- alt text
- caption
- block key

## Important Current Limitations

This is a first-pass normalization script, not the final enrichment engine.

At this stage it does **not** yet:

- guarantee fully reviewed objective codes
- produce polished teaching explanations
- fully encode all auto-marking rules
- deduplicate family variants across the entire bank with human-level precision
- insert anything into Supabase

Those are later Stage 4 and Stage 5 refinements.

## Why This Is Still Valuable

Even in this first-pass form, the script removes a large amount of manual work.

It gives us:

- a structured source bundle instead of raw docx/pdf dependence
- image linkage for prompt visuals
- a first pass at duplicate-family control
- a first pass at difficulty and format labeling
- a first pass at topic-level objective mapping
- a place to run QA before database import

## Current Snapshot

Latest verified real-data run produced:

- 904 staged questions
- 29 prompt assets
- 856 questions with objective codes proposed
- 48 questions intentionally left with `needs_objective_mapping`

This is the right direction for a first-pass framework:

- most of the bank now has objective structure
- unclear edge cases are still surfaced honestly for review
- no question has been promoted live or written into Supabase from this stage

## Next Recommended Steps After This Script

1. inspect the remaining `needs_objective_mapping` pockets topic by topic
2. begin explanation enrichment using fact-file language and mark-scheme intent
3. tighten auto-mark rules for fill-gap, short-text and structured-response items
4. only then consider shaping real staged database inserts
5. only after that, consider applying Stage 3 schema changes and loading staged data into Supabase
