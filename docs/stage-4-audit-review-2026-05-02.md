# Stage 4 Audit Review

Date: 2026-05-02

Purpose: document the deeper audit requested before any further enrichment or promotion work continues. This review covers:

- the current Stage 4 question-ingestion outputs
- the current app/runtime that would eventually render and score those questions
- the current selection, scoring, and progress infrastructure

## Verdict

The project is **not ready** to move from pipeline scaffolding into question promotion or further student-facing use without additional corrective work.

The app foundation is now more stable than before, but the question pipeline and the current runtime are still misaligned in ways that would undermine:

- question accuracy
- reliable self-marking
- trustworthy progress data
- intelligent adaptation

## High-Severity Findings

### 1. Staged question payloads are not yet compatible with the current runtime question contract

The Stage 4 bundle stores question data in a richer, staging-oriented shape, but the current runtime still expects the older live-question contract.

Examples:

- MCQ staging uses `options_json` as a list of `{ key, text }` items and stores the answer as `correct_answer_json.raw`.
- The current renderer expects `options_json.choices` and the current scorer expects `correct_answer_json.choice`.
- Match/true-false style items are currently staged with `correct_answer_json.raw` strings such as `1 → True; 2 → False`, but the renderer/scorer expect `pairs`.

Files:

- `scripts/build_stage4_import_bundle.py`
- `src/components/QuestionRenderer.tsx`
- `src/lib/scoring.ts`
- `src/lib/types.ts`

Impact:

- even a structurally successful import would not yet be safe to promote directly into the live student runtime
- a transformation layer is required between staging and live publishing

### 2. Session results are still trusted from the client rather than recalculated server-side

The student app currently evaluates correctness in the browser and sends `isCorrect`, `score`, and `accuracyPct` back to Supabase. The save function stores that result directly instead of recalculating it from authoritative question data.

Files:

- `src/pages/StudentSessionPage.tsx`
- `src/lib/scoring.ts`
- `supabase/migrations/20260214170000_init_schema.sql`

Impact:

- progress records are not robust enough to support high-trust reporting
- any future adaptive model built on top of these results would be drawing from untrusted client-side marking
- this is a serious infrastructure weakness because the whole value of the app depends on reliable revision data

### 3. The current family-grouping heuristic is too broad for safe duplicate suppression

The new `question_family_code` scaffolding is useful, but the current heuristic groups clearly different questions under the same family.

Observed examples from the generated payload:

- `digital-data.graphics.choose` includes questions about pixels, resolution, JPEG vs BMP compression, and vector vs bitmap differences
- `digital-data.data-measurement.choose` includes bit rate, kilobytes, and bit depth
- `database-applications.data-types.choose` covers multiple different field/data-type decisions

File:

- `scripts/build_stage4_import_bundle.py`

Impact:

- if these families are later used to suppress near-duplicates in a session, the picker will wrongly treat distinct revision opportunities as if they were the same question idea
- this would reduce topic coverage and weaken the adaptive value of sessions

## Medium-Severity Findings

### 4. Questions with no teaching explanation are still being marked `ready_for_review`

The staging transformer correctly flags missing explanations, but it does not treat them as blocking. As a result, all 904 staged questions are currently `ready_for_review` even though all 904 also have `needs_explanation_enrichment`.

Files:

- `scripts/build_stage4_staging_payload.py`

Impact:

- the workflow is currently too optimistic
- a question without a student-facing explanation is not close to student-ready for this project

### 5. Short factual and list-style answers are still being classified into formats that the current scorer cannot mark well

The current format inference sends several simple “name/state/list” items into `structured_response`, while the current scorer only supports exact normalized string matches for `short_text` and `structured_response`.

Files:

- `scripts/build_stage4_import_bundle.py`
- `src/lib/scoring.ts`

Impact:

- many valid student answers would still be marked wrong unless the transformation and marking layers are tightened significantly
- this is especially risky for factual exam-prep questions where wording variation should be tolerated predictably

### 6. Automatic transformation of exam items to MCQ is being surfaced for review, but not blocked

The pipeline is correctly flagging transformed exam items, and there are many of them. At present, these transformed items remain reviewable rather than blocked.

Observed payload summary:

- `transformed_exam_item`: 181

Files:

- `scripts/build_stage4_staging_payload.py`
- generated payload samples from `/private/tmp/unit1_stage4_staging_payload.json`

Impact:

- transformed exam items can be useful, but they are also one of the biggest risks for distorting exam style
- they need closer editorial scrutiny than ordinary imports

### 7. Current session picking is still mostly random and not yet aligned to the intended adaptive model

The current picker:

- excludes recent exact repeats
- forces one expert diagram when available
- otherwise still relies on random ordering

It does not yet use:

- `question_family_code`
- `selection_weight`
- objective balance
- support/core/challenge targeting

Files:

- `supabase/migrations/20260214170000_init_schema.sql`
- `supabase/migrations/20260215160000_expert_diagram_guarantee.sql`

Impact:

- current session composition is not yet intelligent enough for the adaptive revision experience you want

### 8. Current student stats are still based on tags and difficulty, not on topic/objective mastery

The student dashboard still derives stats from completed sessions plus `tags_json`.

Files:

- `src/components/StudentStatsPanel.tsx`
- `src/pages/StudentTopicPage.tsx`

Impact:

- the current student-facing analytics remain too shallow to guide meaningful revision decisions
- this confirms your earlier concern that the widgets are not yet useful enough

## Lower-Severity but Important Findings

### 9. Objective mapping has improved substantially but still has unresolved pockets

Current verified Stage 4 payload summary:

- `question_count`: 904
- `asset_count`: 29
- `objective_mapped_count`: 856
- `objective_unmapped_count`: 48

This is good progress, but the remaining 48 should be treated as real unresolved cases rather than silently guessed.

### 10. Supporting image infrastructure is in much better shape than before

The pipeline now carries prompt assets through:

- source-relative figure resolution
- asset metadata
- staged asset payloads

This is a positive finding. The main remaining issue is not asset support itself, but the still-incomplete transformation from staged content into live, renderable question records.

## What Must Be Fixed Before Moving Forward

1. Define and build the staging-to-live transformation layer.
2. Move answer verification and score calculation to the server side.
3. Tighten family-code generation so it groups true near-duplicates, not broad topic areas.
4. Make missing explanations a harder review gate for student-facing readiness.
5. Redesign format-specific autograde rules for short factual, list, fill-gap, and transformed exam items.
6. Replace the current session picker with one that uses objective coverage, family avoidance, and weighting.
7. Replace current tag-based student stats with topic/objective mastery views.

## Current Positive Position

Despite the issues above, the project is in a much better place than it was before:

- login/session stability is materially improved
- the Unit 1 source pack is now parseable
- prompt-image handling is scaffolded
- staged review payloads exist
- objective mapping is largely working
- the risks are now visible and explicit rather than hidden

That means the foundation work has value. It just should not yet be mistaken for a student-ready revision bank.
