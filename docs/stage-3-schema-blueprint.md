# Stage 3 Schema Blueprint

This file defines the Stage 3 Supabase redesign for the Unit 1 rebuild.

The goal is to keep the current authentication/account setup intact while upgrading the data model so the app can support:

- all 12 Unit 1 topics
- exact topic names matching the new source documents
- richer auto-markable question content
- diagrams, screenshots, and tables
- objective-level tagging
- meaningful progress tracking by topic and objective
- a stronger adaptive engine in later stages

## What Stays

These remain the backbone of the app:

- `auth.users`
- `profiles`
- `student_accounts`
- `academic_years`

Existing usernames and passwords are not changed by Stage 3.

## What Is Wrong With The Current Schema

The current model was good enough for a single-topic prototype, but it has four structural limits:

1. `topics` only represents a partial Unit 1 structure and several titles do not match the new source documents exactly.
2. `questions` only stores a simple stem plus `options_json` and `correct_answer_json`, which is too thin for real exam items with tables, screenshots, diagrams, and richer answer logic.
3. There is no formal model for learning objectives, so we cannot track topic mastery or objective mastery reliably.
4. `session_questions` depends directly on live question rows, which makes content replacement awkward and risks historical breakage.

## Stage 3 Design Decisions

### 1. Align Topics To The New Unit 1 Resource Pack

The app should store these exact topic titles:

1. Digital data
2. Software
3. Database applications
4. Spreadsheet applications
5. Computer hardware
6. Network technologies
7. Cyberspace, network security and data transfer
8. Cloud technology
9. Ethical, legal and environmental impact
10. Changes in employment opportunities, skills requirements and work practices
11. Health and safety
12. Digital applications

The database keeps slugs for routing, but titles must match the document wording exactly.

### 2. Keep `questions`, But Make It Richer

We are not replacing the `questions` table yet. Instead, we extend it so it can support the current UI during transition and a richer content pipeline later.

New question fields support:

- `max_marks`
- `adaptive_tier`
- `question_family_code`
- `selection_weight`
- `content_blocks_json`
- `response_schema_json`
- `autograde_rules_json`
- `teacher_notes`

This allows us to move from a simple stem/options model to a richer structured model without breaking the current app immediately.

### 3. Add A Real Objective Model

We need a formal table for topic objectives:

- `learning_objectives`
- `question_objectives`

This is the foundation for:

- topic-based reporting
- objective-based reporting
- support/challenge pathways
- identifying what a student actually struggles with

### 4. Add Content Source Tracking

We need structured provenance, even if students never see it:

- `content_sources`
- `question_source_links`

This lets us map questions back to:

- past paper extracts
- mark scheme extracts
- practice-bank items
- fact files

The old `source_ref` text column remains useful for quick labels, but it is not enough on its own for the full Unit 1 rebuild.

### 5. Add Visual Asset Support

We need proper asset metadata for:

- diagrams
- screenshots
- prompt figures
- tables rendered as images when needed

New tables:

- `question_assets`
- `question_asset_links`

For Stage 4 we will use a Supabase Storage bucket named `question-assets`. The metadata table is created in Stage 3; the import/upload pipeline will use it later.

### 6. Add Owner-Only Import Staging

We also need a safe way to bring in future teacher-created questions without writing directly into the live student question bank.

This should be an owner-only staging workflow, not a live AI feature in the student app.

New staging tables:

- `content_owner_settings`
- `import_batches`
- `staged_questions`
- `staged_question_assets`

This gives us a clean editorial path:

1. upload or prepare a structured batch
2. attach any supporting images needed by those questions
3. review the staged records
4. apply approved staged questions into the live `questions` and `question_assets` tables

This is especially important for future spreadsheet and database questions, where the user may later create more items in a similar past-paper style and import them in batches.

For this workflow, the long-term goal is not just “admin-only”. It is “owner-only”, meaning the user’s specific account should control imports, review, and publication. Stage 3 now prepares for that with a dedicated owner setting rather than assuming every admin can edit content forever.

### 7. Future-Proof Session History

We are adding snapshot fields to `session_questions`:

- `question_snapshot_json`
- `objective_ids_json`
- `marks_available`
- `marks_awarded`

We also relax the question foreign key so historical attempts do not break if old questions are later retired or deleted.

This is important because the first version already showed that replacing questions cleanly is difficult when old session rows point at them rigidly.

### 8. Create Mastery Tables

We are creating:

- `student_topic_mastery`
- `student_objective_mastery`

These are not fully populated by Stage 3 yet. They are schema foundations for Stage 5, where the adaptive model and meaningful stats will be built.

## New Internal Concepts

### Adaptive Tier

Each question can sit inside an internal tier:

- `support`
- `core`
- `challenge`

This sits underneath the visible difficulty labels `easy`, `medium`, and `expert`.

That gives us two levels of control later:

- visible student-facing difficulty
- internal support/challenge tuning within and across difficulties

### Question Family

Each question can optionally belong to a `question_family_code`.

This is the foundation for later session rules such as:

- never repeat the exact same `question_id` in a session
- never repeat the same `question_family_code` in a session
- spread coverage across objectives and formats rather than accidentally clustering similar items

The current app already avoids selecting the same row twice. The new family code is what lets us avoid “the same question twice in disguise”.

### Intelligent Randomisation Support

`selection_weight` gives us controlled randomisation later.

It allows the session picker to vary question choice without behaving like a blind shuffle. Combined with objective links, family codes, and adaptive tiers, this gives us the schema basis for:

- balanced objective coverage
- better format mix
- avoiding near-duplicates
- controlled variation across sessions

### Staged Supporting Images

Future imports must support question visuals before publication.

That means staged questions need a proper place for:

- prompt diagrams
- screenshots
- image-based tables
- option images where relevant
- supporting figure captions and alt text

So staged imports should not just hold text. They should also support staged image metadata and storage paths before promotion into the live asset tables.

### Multi-Mark Readiness

The current app marks most questions as simply right or wrong. The new schema prepares for better scoring by storing:

- question `max_marks`
- per-attempt `marks_available`
- per-attempt `marks_awarded`
- session `points_available`

Even if the current frontend still behaves mainly as correct/incorrect, the data model will no longer trap us in a purely binary scoring system.

## Live-Data Impact

If this migration is applied later:

- usernames and passwords stay the same
- existing accounts stay the same
- current sessions/history are not automatically deleted
- the current app should still run because the old columns and RPC signatures remain in place
- future question imports can be staged and reviewed before they ever affect student sessions

The later relaunch reset is still handled separately by:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/manual/reset_student_progress_for_relaunch.sql`

## What Stage 3 Does Not Do Yet

Stage 3 does not:

- import the new Unit 1 questions
- upload diagram/screenshot assets
- implement the final owner-only upload UI
- populate learning objectives
- rebuild the student stats UI
- rebuild the adaptive engine
- rebuild the admin interface around the new schema

Those are later stages.

## Stage 4 Dependencies

Stage 4 will use this schema to:

- parse the new Unit 1 source pack
- import objective metadata
- upload question visuals
- stage future teacher-created question batches safely
- insert real PPQ-derived and practice questions for all 12 topics

## Stage 5 Dependencies

Stage 5 will use this schema to:

- calculate topic mastery
- calculate objective mastery
- identify strongest and weakest topics
- identify topics not revised recently
- produce clearer adaptive recommendations and support pathways

## Summary

Stage 3 is deliberately a foundation pass.

It keeps the accounts and auth model stable, but expands the schema so the app can stop being a one-topic prototype and become a proper Unit 1 revision platform.
