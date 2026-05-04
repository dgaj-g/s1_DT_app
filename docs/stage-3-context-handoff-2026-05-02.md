# Stage 3 Context Handoff

This file is a meticulous continuity handoff for the rebuild of the S1 / GCSE Digital Technology Unit 1 revision app.

It is intended to let a new session pick up with a detailed understanding of:

- what the app is
- what has already been done
- what the user cares most about
- what the current rebuild stages mean
- what has and has not been applied yet
- the nuanced design decisions already agreed

This is not a verbatim transcript. It is a careful working reconstruction of the decisions, constraints, and context from the current thread.

## Most Recent Verified Progress (2026-05-04)

The current corrective phase is still focused on trust-first remediation, not release.

Recent verified progress:

- Completed the Stage 4 autograde-rule structural re-audit:
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-autograde-rule-structural-reaudit-2026-05-04.md`
- Tightened the Stage 4 gate so it no longer blanket-flags structurally safe:
  - `accepted_texts`
  - `ordered_gaps`
  - `shared_gap_pool`
  - simple one-answer exact text/gap items
- Extended the importer for:
  - stem-aligned multi-blank phrase answers
  - four-answer shared pools
  - one-answer slash alternatives
  - an explicit ER-diagram accepted-text override
- Tightened the Phase 1 promotion bridge so it now rejects unresolved:
  - `needs_autograde_rule_review`
  - `needs_structured_answer_normalization`
  - `misclassified_true_false`
- Rewrote two long-definition source items into concise concept-label prompts:
  - `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_05_06.md`
  - `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_01_digital_data.md`
- Verified controlled promotion dry run:
  - `8` staged
  - `7` promoted
  - `1` rejected for the correct reason: `flag_needs_autograde_rule_review`

- Added grouped fill-gap normalization and ordered-gap support in:
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260503221500_phase1_runtime_v2.sql`
- Closed these defect families after focused re-audits:
  - `DD-003`
  - `EMP-002`
  - `HS-002`
  - `DA-002`
  - `SW-001`
  - `SW-002`
  - `CL-003`
  - `EL-003`
  - `SS-002`
- Corrected the Topic 9 objective-mapping edge case so GPS/privacy prompts are no longer polluted by a spurious copyright objective when the actual question text is clearly about privacy/social-media risk.

Important process note:

- `build_stage4_import_bundle.py` and `build_stage4_staging_payload.py` should be run **sequentially**, not in parallel, because the staging payload depends on the freshly written import bundle. A parallel rebuild previously produced a stale staging result and briefly hid the corrected objective mapping.

Current staged baseline after the latest sequential rebuild and defect closures:

- `904` staged questions
- `29` staged assets
- `0` `ready_for_review`
- `904` `draft`
- `known_content_defect`: `0`
- `needs_explanation_enrichment`: `904`
- `needs_objective_mapping`: `0`
- `needs_autograde_rule_review`: `1`
- `transformed_exam_item`: `263`
- `supplementary_derived_item`: `6`
- `practice_question_needs_source_normalization`: `483`

## Project Identity

- Repo: `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app`
- Supabase project ref: `omksuffrkbnoekszrgcq`
- Hosting target: GitHub Pages
- Backend: Supabase Auth, Postgres, RLS, Edge Functions
- Frontend: React + TypeScript + Vite

## Core Product Goal

Build a login-protected revision app for CCEA GCSE Digital Technology Unit 1 that:

- uses student usernames and passwords already issued
- supports all 12 Unit 1 topics
- includes accurate past-paper-style revision content
- includes diagrams, tables, screenshots, and other visuals where needed
- auto-marks reliably
- gives meaningful student stats
- provides stronger adaptive support for weaker students and better challenge for stronger students
- gives the teacher a clear, useful admin side

## Current Major User Priorities

The user has explicitly said:

1. Existing student usernames and passwords must stay.
2. Old student attempt/progress history does **not** need preserved for the rebuilt launch.
3. Final app will be behind username/password access.
4. All 12 Unit 1 topics must be populated before study leave.
5. Only the user’s account should edit/publish content for now.

## Primary Source Materials

The rebuild is now based on the newer resource folder:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project`

Important files in that folder include:

- `GCSE DT Unit 1 - Past Paper Questions by Topic.docx`
- `GCSE DT Unit 1 - Past Paper Questions (Auto-Markable) by Topic.docx`
- `GCSE DT Unit 1 - Practice Questions by Topic.docx`
- Unit 1 fact files
- supporting QA and extraction files

These topic names must be matched exactly in the app:

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

## What Happened Before This Rebuild

Earlier work created a working prototype with:

- student logins `s1dt001` to `s1dt100`
- admin dashboard
- Supabase-backed question bank
- student sessions and stats
- GitHub Pages deployment

But the user later identified major problems:

- instability and freezing/crashing
- weak content quality and question design
- weak student stats
- weak adaptive behaviour
- admin UX that was not good enough

That moved the project from “polish the prototype” to “rebuild v2 on the same auth/account foundation”.

## Stage Model Agreed In This Thread

The rebuild was staged as:

1. Stage 1: Safeguard and baseline
2. Stage 2: Stability rebuild
3. Stage 3: Supabase schema redesign
4. Stage 4: Content pipeline and full population
5. Stage 5: Adaptive engine and student stats rebuild
6. Stage 6: Admin overhaul and release prep

## Stage 1: What Was Done

Stage 1 created the groundwork documents and reset prep:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-1-baseline.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/manual/reset_student_progress_for_relaunch.sql`

Important Stage 1 decision:

- keep current credentials
- do not preserve old student progress history for the rebuilt launch

## Stage 2: What Was Done

Stage 2 focused on stability and session robustness.

Files added or changed:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/request.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/AppErrorBoundary.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/App.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/hooks/useAuth.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/ProtectedRoute.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/AppShell.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/LoginPage.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentTopicPage.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentSessionPage.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentSummaryPage.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/AdminDashboardPage.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/api.ts`

Key stability improvements made:

- safer auth bootstrap
- better timeout handling
- error boundary support
- cleaner retry/error handling
- safer route protection
- safer sign-out flow
- less fragile session and dashboard loading

The user then tested locally and confirmed these flows all worked:

- student login
- browser refresh after login
- start session
- complete session
- summary page
- sign out
- admin login
- admin dashboard load

Stage 1 and Stage 2 should therefore be treated as complete.

## Local Dev Environment Notes

At one point `npm run dev` failed because `esbuild` had been installed for the wrong platform.

The user fixed this locally by running:

```zsh
cd "/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app"
rm -rf node_modules
rm -f tsconfig.app.tsbuildinfo tsconfig.node.tsbuildinfo
npm install
npm run dev
```

This matters because:

- the local dev server now runs properly
- `tsconfig.app.tsbuildinfo` and `tsconfig.node.tsbuildinfo` were removed during cleanup
- those files may show as deleted in git status even though they are generated cache files

## Stage 3: What Existed Before Refinement

Stage 3 began as a schema foundation pass with these files:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-3-schema-blueprint.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`

The original Stage 3 foundation already covered:

- aligning `topics` to the exact 12 Unit 1 titles
- enriching `questions`
- adding `learning_objectives`
- adding `content_sources`
- adding `question_source_links`
- adding `question_assets`
- adding `question_asset_links`
- adding `question_objectives`
- adding `student_topic_mastery`
- adding `student_objective_mastery`
- future-proofing session history with question snapshots and marks

Most importantly:

- this migration has **not** been applied to Supabase yet
- it remains a repo-only design file at this stage

## Stage 3: Additional Refinements Agreed

The user then raised a very important design concern:

They may later create additional spreadsheet and database questions in a similar exam style and want the app to support importing those questions into the system.

The agreed design direction is:

- do **not** build AI into the live student app
- do **not** rely on a magical free-text “paste anything” uploader
- instead build an owner-only structured import/staging workflow
- use AI offline only as an assistant for converting messy source material into the structured format

This means the app should eventually support:

1. staging batches of teacher-prepared questions
2. attaching supporting images to those staged questions
3. reviewing them before they go live
4. then promoting them into the live question bank

## Duplicate-Question and Randomisation Decisions

The user explicitly said:

- duplicate questions must not be asked in the same session
- question order should be randomised intelligently

Important nuance:

- the current question picker already avoids selecting the **same row twice** in a session
- but it does **not** avoid near-duplicate question variants, because there was no family/group concept

So the refined Stage 3 design now includes:

- `question_family_code`
- `selection_weight`

Meaning:

- `question_family_code` groups related variants of the same core idea
- later session selection should avoid repeated families inside the same session
- `selection_weight` supports controlled randomisation rather than blind shuffling

## Owner-Only Import and Content Control

The user wants content editing/importing/publishing controlled by their account, not by every admin forever.

To prepare for that, the refined Stage 3 design now includes:

- `content_owner_settings`
- `import_batches`
- `staged_questions`
- `staged_question_assets`

### Purpose of Each

#### `content_owner_settings`

Stores the auth user id of the content owner.

This gives the schema a proper concept of:

- who is allowed to run staged imports
- who is allowed to review staged questions
- who is allowed to apply staged question batches

#### `import_batches`

Represents a structured upload/import batch.

Useful for:

- CSV/XLSX/JSON/manual imports
- keeping the import grouped and auditable
- tracking batch status such as draft, uploaded, ready for review, approved, applied

#### `staged_questions`

Stores questions before they become live student questions.

Important fields include:

- topic
- difficulty
- format
- adaptive tier
- `question_family_code`
- `selection_weight`
- structured prompt/answer data
- objective code hints
- source metadata
- review notes
- dedupe fingerprint

#### `staged_question_assets`

Stores supporting visuals for staged questions before promotion into the live asset system.

This is important because the user explicitly wanted a proper place for:

- prompt diagrams
- screenshots
- image-based tables
- option images
- captions
- alt text

Supporting images must therefore be part of the staging design, not an afterthought.

## Current Refined Stage 3 Files

As of this handoff, the refined files are:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-3-schema-blueprint.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`

The migration now includes:

- new enums:
  - `import_batch_status`
  - `staged_question_status`
  - `import_source_format`
- new `questions` fields:
  - `question_family_code`
  - `selection_weight`
- new table:
  - `content_owner_settings`
- new function:
  - `public.is_content_owner(p_user_id uuid)`
- new tables:
  - `import_batches`
  - `staged_questions`
  - `staged_question_assets`
- indexes for import/staged content tables
- owner-focused RLS policies for staged import tables

## Important Limitation / Nuance

The refined Stage 3 foundation now has an owner-specific concept, but it still needs operational setup later:

- `content_owner_settings` must be populated with the user’s auth account id before owner-only import features can actually be used

That means:

- the schema is prepared
- the live database has not yet been configured
- later work will need to include a safe way to set the owner account once the migration is applied

## What Has Not Happened Yet

At the moment:

- Stage 3 migration has **not** been pushed/applied to remote Supabase
- no live database tables have changed from this Stage 3 work yet
- no existing student credentials have been touched
- no old progress reset has been run
- no live question imports from the new Unit 1 folder have happened yet
- no final upload UI for staged imports exists yet

## Stage 4: Current Progress

Stage 4 is no longer just a plan. A first real scaffold now exists.

New Stage 4 files:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-pipeline-blueprint.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-accuracy-gate.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-objective-mapping-framework.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/README.md`

### What The First Script Does

`build_stage4_import_bundle.py` reads the curated Unit 1 source pack and emits a normalized import bundle with:

- question records
- asset records
- proposed difficulty
- proposed format
- proposed adaptive tier
- proposed objective codes
- proposed `question_family_code`
- proposed `selection_weight`
- `dedupe_fingerprint`

### What The Second Script Does

`build_stage4_staging_payload.py` reads the normalized bundle and adds:

- review flags
- review priority
- staging status
- payload structure aligned to:
  - `import_batches`
  - `staged_questions`
  - `staged_question_assets`

### Real Test Run Results

The Stage 4 builder was run successfully against the real source pack.

First-pass normalized bundle summary:

- 904 questions
- 29 prompt assets

Second-stage review payload summary:

- 904 questions
- 29 assets
- 904 `ready_for_review`
- 0 `draft`
- priority split:
  - 596 `medium`
  - 308 `high`

### Objective Mapping Progress

Stage 4 then moved beyond raw parsing into the first real enrichment layer:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-objective-mapping-framework.md`

This introduced a topic-by-topic learning-objective catalog across all 12 Unit 1 topics and wired first-pass objective inference into the Stage 4 bundle builder.

Latest verified objective-mapping results:

- 904 questions total
- 856 questions now carry proposed objective codes
- 48 questions remain flagged `needs_objective_mapping`

The remaining unmapped cases are being left unresolved on purpose rather than being forced into weak labels. That is an agreed design choice because the user prioritises accuracy over artificially complete metadata.

Main review flags currently present:

- `needs_explanation_enrichment`
- `needs_objective_mapping`
- `transformed_exam_item`
- `needs_autograde_rule_review`
- `practice_question_needs_source_normalization`

Important nuance:

- these are not publish-ready questions
- they are structurally review-ready staged records
- the accuracy gate is intentionally separating “parseable” from “safe to trust without content QA”
- objective mapping is now materially underway, but explanation enrichment and autograde refinement still remain

## Recommended Next Steps After This Handoff

The next sensible order is:

1. review refined Stage 3 structure in plain English with the user
2. if approved, keep refining the Stage 3 migration only in the repo until stable
3. use the Stage 4 import policy document:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-import-rules-and-template.md`
4. use the Stage 4 pipeline blueprint:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-pipeline-blueprint.md`
5. use the objective-mapping framework:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-objective-mapping-framework.md`
6. use the first scaffold importer:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
7. use the second-stage review transformer:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
8. continue refining heuristics and review rules from the `GCSE Unit 1 Revision Project` folder
9. read the deeper audit checkpoint before moving into more enrichment work:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-audit-review-2026-05-02.md`
10. do not move into explanation enrichment until the audit findings have been reviewed
11. only after that, consider applying schema changes to Supabase
12. Spreadsheet Applications content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-spreadsheet-applications-content-audit-2026-05-03.md`
13. Content defect register created:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`

## User Preferences And Collaboration Notes

The user values:

- accuracy above all
- adaptive teaching quality
- clear separation of easy / medium / expert experiences
- proper diagrams and assets where the exam expects them
- structured guidance, not guesswork
- patient, step-by-step support

The user does **not** want:

- AI hidden inside the live student marking/importing flow
- unreliable free-text long-answer marking without a dependable system
- vague stats
- meaningless admin workflow labels

## Other Relevant Existing Handoff Files

There are already older handoff files in the repo from previous continuity work:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/claude-code-forensic-handoff.txt`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/claude-code-prompt.txt`

Those are still useful, but this Markdown file is the more precise continuity record for the current rebuild stages and Stage 3 refinement decisions.

## Quick Restart Instructions For A New Session

If a new session needs to continue this work, it should:

1. read this file first:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-3-context-handoff-2026-05-02.md`
2. then read:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-3-schema-blueprint.md`
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`
3. treat Stage 1 and Stage 2 as complete
4. treat Stage 3 as in-progress and not yet applied remotely
5. continue from the refined schema / import-staging design rather than restarting from the old prototype assumptions
6. treat objective mapping as the current completed Stage 4 enrichment pass
7. read the current audit checkpoint:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-audit-review-2026-05-02.md`
8. treat explanation enrichment as the next recommended content-quality step only after the audit findings have been addressed or consciously accepted

## Final Status At Time Of Writing

- Stage 1: complete
- Stage 2: complete and locally tested successfully
- Stage 3: in progress, refined in repo only, not yet applied to Supabase
- Stage 4: started, with working import, review-payload, and first-pass objective-mapping scaffolds in the repo
- Audit status: a deeper review has now been written in `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-audit-review-2026-05-02.md`; it found material content/runtime risks that should be addressed before further promotion work
- Stage 5 onward: not started yet

12. Digital Data content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-digital-data-content-audit-2026-05-03.md`
13. Software content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-software-content-audit-2026-05-03.md`
14. Computer Hardware content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-computer-hardware-content-audit-2026-05-03.md`
15. Cyberspace, Network Security and Data Transfer content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-cyberspace-network-security-and-data-transfer-content-audit-2026-05-03.md`
16. Cloud Technology content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-cloud-technology-content-audit-2026-05-03.md`
17. Ethical, Legal and Environmental Impact content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-ethical-legal-and-environmental-impact-content-audit-2026-05-03.md`
18. Changes in Employment Opportunities, Skills Requirements and Work Practices content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-changes-in-employment-opportunities-skills-requirements-and-work-practices-content-audit-2026-05-03.md`
19. Health and Safety content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-health-and-safety-content-audit-2026-05-03.md`
20. Digital Applications content audit completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-digital-applications-content-audit-2026-05-03.md`
21. Cross-topic Stage 4 audit synthesis completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-cross-topic-audit-synthesis-2026-05-03.md`
22. Stage 4 remediation plan completed:
    - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-remediation-plan-2026-05-03.md`

## Stage 5: Phase 1 Implementation Spec

A concrete implementation spec now exists here:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-5-phase-1-implementation-spec-2026-05-03.md`

This document converts the audit findings and remediation plan into the first corrective engineering build.

### Main conclusions from the spec

The first corrective build must focus on four things before any further student-facing trust claims are made:

1. a canonical live runtime question contract;
2. a server-authoritative session lifecycle;
3. a staged-to-live transformation layer; and
4. proper normalization of core self-marking formats, especially true/false and short factual answers.

### Important design choices in the spec

The spec recommends:

- introducing a normalized frontend/runtime `RuntimeQuestion` type;
- treating `content_blocks_json`, `response_schema_json`, and `autograde_rules_json` as the real live contract;
- stopping direct student reliance on legacy `options_json` assumptions;
- replacing client-led session completion with:
  - `start_session_v2`
  - `grade_session_question_v2`
  - `complete_session_v2`
- creating session-question rows at session start, not only at completion;
- moving correctness, marks, and totals fully server-side;
- adding an explicit `true_false` runtime path;
- keeping raw `structured_response` out of live student sessions unless transformed into a safer format.

### Key file targets identified by the spec

Frontend:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/api.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/scoring.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/QuestionRenderer.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentSessionPage.tsx`

Supabase:
- follow-on migration after:
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`

Pipeline:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- new promotion bridge to be created:
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

### Recommended next build order

1. create the follow-on Supabase migration for `true_false` and v2 session/grading RPCs;
2. add runtime contract types in the frontend;
3. add v2 API wrappers;
4. refactor renderer and session page onto the new contract;
5. build the staged-to-live transformation script;
6. tighten the Stage 4 staging gate;
7. validate the full flow using `Network technologies` as the first end-to-end topic.

### Phase 1 Migration Draft Now Exists

A first follow-on migration draft has now been created here:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260503221500_phase1_runtime_v2.sql`

This migration is still **repo-only** and has **not** been applied to Supabase yet.

Its purpose is to begin the corrective build described in the Phase 1 implementation spec by adding:

- `true_false` to the runtime question-format path;
- a new `session_question_status` enum;
- session-question grading state fields;
- runtime payload helpers:
  - `normalize_answer_token`
  - `normalize_answer_phrase`
  - `answer_text_matches`
  - `build_runtime_question_payload`
  - `grade_runtime_question`
- v2 session lifecycle RPCs:
  - `get_session_state_v2`
  - `start_session_v2`
  - `grade_session_question_v2`
  - `complete_session_v2`

Important nuance:
- this is the **first engineering draft** of the server-authoritative session/grading path;
- it has been written to coexist with the older session flow temporarily;
- frontend code has **not** yet been refactored onto these v2 functions.

### Recommended immediate next step after this draft

Before applying anything remotely, the next coding step should be:

1. review the migration draft carefully against the current frontend session flow;
2. then refactor frontend runtime types and API wrappers to target the new v2 path;
3. only after that consider local/remote migration application.

### Frontend Runtime Refactor Progress (2026-05-03, later update)

The first frontend refactor pass against the Phase 1 v2 runtime contract has now been completed in the repo:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts`
  - now includes runtime question/response schema/session types
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/api.ts`
  - now includes:
    - `isV2RuntimeUnavailableError`
    - `getSessionStateV2`
    - `startSessionV2`
    - `gradeSessionQuestionV2`
    - `completeSessionV2`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/QuestionRenderer.tsx`
  - now supports both:
    - runtime v2 question payloads
    - legacy question payloads
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentSessionPage.tsx`
  - now attempts the v2 session path first
  - and falls back explicitly to the verified legacy flow when the backend migration/RPC path is unavailable

Verification status from this pass:

- `tsc -b --verbose` completed successfully
- `npm run build` completed successfully

Important nuance:

- this was only possible after repairing a broken local dependency tree with:
  - `npm ci`
- the build failures encountered during this pass were dependency integrity issues (`rollup`, then `react-smooth`/`iceberg-js` under `recharts`), not frontend contract errors from the new session work

Important remaining boundary:

- the v2 frontend path is now coded and typechecked, but the Supabase migration
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260503221500_phase1_runtime_v2.sql`
  has still **not** been applied
- so the live app still depends on legacy fallback behaviour until that migration and related runtime payload work are applied and validated

Recommended next engineering step after this point:

1. build the staged-to-live promotion bridge:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`
2. align the staging gate to the runtime contract
3. only then begin applying/testing the v2 backend path against a corrected topic

### Phase 1 Promotion Bridge Now Exists (2026-05-03, later update)

The staged-to-live promotion bridge has now been created here:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

What it currently does:

- reads Stage 4 staging payloads;
- blocks promotion unless staging status is approved;
- blocks items with:
  - missing explanations;
  - unresolved objective mapping;
  - unresolved prompt assets;
  - open defect-register entries;
  - unsafe/unsupported live runtime shapes;
- normalizes safe approved items into:
  - live `questions` payload rows;
  - `content_sources`;
  - `question_source_links`;
  - `question_assets`;
  - `question_asset_links`;
  - `question_objectives`.

### Verification already completed for the bridge

#### Strict real-data run
Using:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

The bridge produced:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_phase1_live_payload.json`

Result:
- `904` staged questions
- `0` promoted
- `904` rejected

This is expected and desirable at the current state because:
- nothing is approved yet;
- explanations are still missing;
- some items still lack objective mapping; and
- open defect-register items are still unresolved.

#### Controlled fixture run
A temporary approved 3-question fixture was also run successfully to prove the positive path.

Verified promoted formats in that fixture:
- `mcq`
- `match_table`
- `fill_gap`

Result:
- `3` promoted
- `0` rejected

This confirms the bridge can successfully generate runtime-safe payloads, not just reject unsafe content.

### Recommended next step after the bridge

1. decide whether to tighten the Stage 4 staging gate further before any approvals;
2. then use corrected/closed items from a high-risk topic to test a real approved promotion subset;
3. only after that begin applying the v2 backend session/grading path against promoted live content.

### Stage 4 Gate Tightening Completed (2026-05-03, later update)

The Stage 4 staging gate has now been deliberately hardened in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

and documented in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-accuracy-gate.md`

What changed:

- the gate now reads the audited defect register:
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`
- transformed-item detection was broadened to catch more locator wording;
- single-statement true/false items hidden inside `match_table` are now flagged as structural blockers;
- explanation gaps, unresolved objective mapping, known defects, and unsafe auto-mark rule shapes now block `ready_for_review` rather than acting as decorative warnings only;
- the payload now records `gate_bucket` metadata:
  - `structural_draft`
  - `editorial_draft`
  - `review_ready`

#### Regenerated payload baseline after tightening

Using:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`

the regenerated staging payload:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

now reports:

- `904` questions
- `29` assets
- `0` `ready_for_review`
- `904` `draft`

with internal gate buckets:

- `65` `structural_draft`
- `839` `editorial_draft`

This is intentional and should be treated as the correct honest baseline at the
current project state.

Key revised flag counts:

- `needs_explanation_enrichment`: `904`
- `needs_objective_mapping`: `48`
- `transformed_exam_item`: `263`
- `needs_structured_answer_normalization`: `181`
- `needs_autograde_rule_review`: `145`
- `known_content_defect`: `105`
- `misclassified_true_false`: `65`
- `supplementary_derived_item`: `6`
- `practice_question_needs_source_normalization`: `483`

Interpretation:

- the earlier `904 ready_for_review` summary was too optimistic;
- the stricter gate is now aligned with the audits and defect register;
- no staged content should currently be treated as genuinely review-ready for
  student-facing promotion;
- the next work should focus on correction and normalization, not approval.

### First High-Risk Source Correction Pass Applied (2026-05-03, later update)

The first direct source-correction pass has now been applied to:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

This was the first priority source file because it contained confirmed
high-risk defects affecting both:

- `Network technologies`
- `Computer hardware`

Corrections applied at source:

- hardware `Q5`
  - Program Counter wording corrected to `the address of the next instruction to be fetched`
- hardware `Q7`
  - prompt corrected to ask for the register that stores the memory address of the data/instruction to be accessed
- hardware `Q25`
  - wording normalized from `part and end of the ... cycle` to `part of the ... cycle`
- hardware `Q27`
  - stem corrected so `Immediate Access Store` matches the concept being asked
- hardware `Q28`
  - register/component definitions and mapping corrected to a coherent fetch-execute model
- network `Q5`
  - rewritten so the correct answer `Router` now matches a gateway/LAN-to-internet concept rather than a switch description
- network `Q31`
  - router/switch definitions separated cleanly so the matching task no longer mixes device roles

After patching the source file, both were regenerated:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

The staged items now reflect the corrected source wording/answers.

Important nuance:

- the corrected items are still `draft`
- this is expected
- they remain blocked by the stricter Stage 4 gate until:
  - explanation enrichment exists;
  - structured answer normalization is completed where needed; and
  - the relevant topic defects are re-audited and explicitly closed

The defect register has been updated to reflect this intermediate state:

- source patched
- staged rebuild completed
- re-audit/closure still pending

### Focused Re-Audit Completed For Topic 5/6 Practice Source (2026-05-03, later update)

A focused re-audit has now been written here:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-topic-05-06-practice-source-reaudit-2026-05-03.md`

This re-audit verified the corrected source-family items against:

- the patched practice source file;
- the supporting automark/extraction context; and
- the regenerated Stage 4 import/staging payloads.

### Defect closure decisions from that re-audit

The following defects are now treated as closed at **source-content** level:

- `NT-001`
- `NT-002`
- `HW-001`

The following remains open:

- `HW-003`
  - partial source normalization applied
  - full closure still pending

Important nuance:

- these closures mean the **content defect itself** is considered repaired;
- they do **not** mean the affected questions are student-ready yet;
- the items are still blocked by Stage 4 for reasons like:
  - missing explanations;
  - unsafe answer normalization;
  - open self-marking structure work.

### Staging-gate effect after closure

After updating the defect register and rerunning:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

the `known_content_defect` count dropped:

- from `105`
- to `101`

This is the expected result.

It confirms that:

- closed source-content defects now fall out of the `known_content_defect` blocker path;
- unresolved runtime/normalization issues continue to block the same items for the right reasons.

Examples:

- `network-technologies.practice_bank.topic_05_06_hardware_networks.q005`
  - no longer carries `known_content_defect`
  - still carries:
    - `needs_explanation_enrichment`
    - `practice_question_needs_source_normalization`
- `network-technologies.practice_bank.topic_05_06_hardware_networks.q031`
  - no longer carries `known_content_defect`
  - still carries:
    - `needs_explanation_enrichment`
    - `needs_structured_answer_normalization`
    - `practice_question_needs_source_normalization`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q027`
  - no longer carries `known_content_defect`
  - still carries:
    - `needs_autograde_rule_review`
    - `needs_explanation_enrichment`
    - `needs_structured_answer_normalization`
    - `practice_question_needs_source_normalization`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q028`
  - no longer carries `known_content_defect`
  - still carries:
    - `needs_explanation_enrichment`
    - `needs_structured_answer_normalization`
    - `practice_question_needs_source_normalization`

This is the intended behaviour.

## 2026-05-03 update: focused re-audit of Topic 3/4 automark source

New re-audit doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-topic-03-04-automark-source-reaudit-2026-05-03.md`

This followed the next high-value source correction pass on:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`

### Outcome

The re-audit established a clean split:

- `DB-001` was a genuine source defect and is now closed
- `DB-002` remains open as a structural/runtime accepted-answer problem

### Source correction applied

In `topics_03_04.md`, the 2024 Q3(b) wording was corrected from:

- `Each word is used once only.`

to:

- `Not all words are used.`

This correction is supported by:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_3_4.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/apply_fixes.py`

### Regenerated outputs

After the source patch, these were rebuilt:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

### Staging-gate effect after closure

After updating the defect register and rebuilding the staging payload:

- `known_content_defect` dropped:
  - from `101`
  - to `100`

In the database topic summary:

- `database-applications` `known_content_defect` count dropped:
  - from `4`
  - to `3`

Examples:

- `database-applications.past_paper.topics_03_04.q042`
  - no longer carries `known_content_defect`
  - still carries:
    - `needs_autograde_rule_review`
    - `needs_explanation_enrichment`
- `database-applications.past_paper.topics_03_04.q003`
  - still carries `known_content_defect`
  - this is intentional because `DB-002` remains open
- `database-applications.past_paper.topics_03_04.q045`
  - still carries `known_content_defect`
  - this is intentional because `DB-002` remains open
- `database-applications.past_paper.topics_03_04.q046`
  - still carries `known_content_defect`
  - this is intentional because `DB-002` remains open

This is the intended behaviour and confirms the gate is now responding correctly to source-level closure versus still-open structural defects.

## 2026-05-03 update: focused re-audit of Topic 2/3 practice source

New re-audit doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-topic-02-03-practice-source-reaudit-2026-05-03.md`

This followed the next source-correction pass on:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_02_03_software_database.md`

### Outcome

The re-audit confirmed:

- `SW-004` was a genuine source wording defect and is now closed

The broader software defects (`SW-001`, `SW-002`, `SW-003`) remain open because they are transformation/structural issues, not source-content fixes.

### Source correction applied

In `topic_02_03_software_database.md`, the `q026` wording was corrected from:

- `The two microchips that make up the main memory in a computer's CPU are called __________ and __________.`

to:

- `The two main types of primary memory are called __________ and __________.`

This preserves the intended answer:

- `RAM; ROM`

while removing the unsafe implication that RAM and ROM are `the main memory in a computer's CPU`.

### Regenerated outputs

After the source patch, these were rebuilt:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

### Staging-gate effect after closure

After updating the defect register and rebuilding the staging payload:

- `known_content_defect` dropped:
  - from `100`
  - to `99`

In the software topic summary:

- `software` `known_content_defect` count dropped:
  - from `8`
  - to `7`

Example:

- `software.practice_bank.topic_02_03_software_database.q026`
  - no longer carries `known_content_defect`
  - still carries:
    - `needs_autograde_rule_review`
    - `needs_explanation_enrichment`
    - `practice_question_needs_source_normalization`

This is the intended behaviour and confirms the gate is now responding correctly to source-level closure versus still-open structural defects in the software topic too.

## 2026-05-03 update: focused re-audit of Topic 9/12 practice source

New re-audit doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-topic-09-12-practice-source-reaudit-2026-05-03.md`

This followed the next source-correction pass on:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`

### Outcome

The re-audit confirmed:

- `EL-001` was a genuine source-level MCQ safety defect and is now closed

The remaining ethical/legal defects stay open because they are still structural or transformation issues rather than source-content faults.

### Source correction applied

In `topic_09_12_wider_impact.md`, the GPS-process MCQ now reads:

- `A. Triangulation`
- `B. Encryption`
- `C. Geocoding`
- `D. Tessellation`
- answer: `A`

This replaced the unsafe distractor:

- `Trilateration`

which had created two technically plausible answers while the same source pack still taught:

- `Triangulation; 3`

later in Topic 9 Q16.

### Regenerated outputs

After the source patch, these were rebuilt:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

### Staging-gate effect after closure

After updating the defect register and rebuilding the staging payload:

- `known_content_defect` dropped:
  - from `99`
  - to `98`

In the ethical/legal topic summary:

- `ethical-legal-and-environmental-impact` `known_content_defect` count dropped:
  - from `7`
  - to `6`

Example:

- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q006`
  - no longer carries `known_content_defect`
  - now carries:
    - `needs_explanation_enrichment`
    - `practice_question_needs_source_normalization`

This is the intended behaviour and confirms the gate is now responding correctly to source-level closure versus still-open structural defects in the ethical/legal topic too.

## 2026-05-03 update: focused re-audit of Topic 7/8 practice source

New re-audit doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-topic-07-08-practice-source-reaudit-2026-05-03.md`

This followed the next source-correction pass on:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_07_08_cyberspace_cloud.md`

### Outcome

The re-audit confirmed:

- `CY-003` was a genuine source-level editorial defect and is now closed

The broader cyberspace defects remain open because they are still structural, transformation, or review-gate issues rather than source-content faults.

### Source correction applied

In `topic_07_08_cyberspace_cloud.md`, `q023` was rewritten from the brittle named-example prompt:

- `State one example of a website that specialises in sharing stolen data (whistleblowing).`
- answer: `Wikileaks`

to the concept-led prompt:

- `What term is used to describe the release of confidential information to expose wrongdoing in the public interest?`
- answer: `Whistleblowing`

This preserves the topic intent while removing the dependency on a specific website example and the loaded wording about `sharing stolen data`.

### Objective-mapping follow-up

Because the rewritten item no longer contained the keyword `Wikileaks`, the objective mapper briefly stopped assigning it to a cyberspace learning objective.

That was corrected in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`

by teaching the mapper to recognize:

- `whistleblowing`
- `confidential information`
- `public interest`
- `wrongdoing`

as valid signals for:

- `cyberspace-network-security-and-data-transfer.cybercrime`

### Regenerated outputs

After the source patch and mapper patch, these were rebuilt:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

### Staging-gate effect after closure

After updating the defect register and rebuilding the staging payload:

- `known_content_defect` dropped:
  - from `98`
  - to `97`

In the cyberspace topic summary:

- `cyberspace-network-security-and-data-transfer` `known_content_defect` count dropped:
  - from `7`
  - to `6`

Example:

- `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q023`
  - no longer carries `known_content_defect`
  - now carries:
    - `needs_autograde_rule_review`
    - `needs_explanation_enrichment`
    - `needs_structured_answer_normalization`
    - `practice_question_needs_source_normalization`

This is the intended behaviour and confirms the gate is now distinguishing correctly between a closed source-level content defect and the still-open downstream structural tasks.

## 2026-05-03 update: HW-003 boundary re-audit

New re-audit doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-hw-003-boundary-reaudit-2026-05-03.md`

This was a boundary check rather than a new source patch. It revisited:

- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q025`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q032`

to decide whether `HW-003` still belonged in the source-content defect register.

### Outcome

The re-audit confirmed:

- `HW-003` should now be closed as a **source-content** defect

Reason:

- `q025` is now cleanly worded:
  - `The ALU is a vital part of the ____________-____________ cycle.`
- `q032` is a fair source prompt:
  - `State one disadvantage of a wireless microphone.`
  - answer: `Limited range / limited battery life`

The remaining problem for `q032` is no longer source trust. It is structural:

- multiple accepted answers are still trapped in a raw string
- fair self-marking still requires answer normalization

### Register effect

The defect register entry for `HW-003` has been updated to closed as a source-content defect, with the remaining `q032` concern intentionally left to the structural/runtime workstream rather than the content-defect workstream.

## 2026-05-03 update: DB-002 structural re-audit

New re-audit doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-db-002-structural-reaudit-2026-05-03.md`

This did not patch source content. Instead, it corrected how accepted alternative answers are represented in the staging/import layer for:

- `database-applications.past_paper.topics_03_04.q003`
- `database-applications.past_paper.topics_03_04.q045`
- `database-applications.past_paper.topics_03_04.q046`

### Structural change applied

In:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`

the bundle builder now converts `accept:` prose into explicit:

- `correct_answer_json.accepted_texts`

For the difficult phrase case in `q003`, a safe override was added so the accepted alternatives become:

- `Uniquely identifies a record`
- `Uniquely identifies a member`
- `Uniquely identifies an individual`

instead of leaving:

- `accept: uniquely identifies a member / individual`

trapped in raw prose.

Supporting follow-on changes were also made in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

so the Stage 4 gate and Phase 1 promotion bridge both respect the richer accepted-answer structure.

### Regenerated outputs

After rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

the audited items now carry explicit accepted-answer lists, and no longer trigger `needs_structured_answer_normalization`.

### Gate effect after closure

Before closing the defect in the register, the structural improvement had already reduced:

- global `needs_structured_answer_normalization`
  - from `181`
  - to `174`

and for `Database applications`:

- topic `needs_structured_answer_normalization`
  - from `21`
  - to `15`

After updating the defect register and rebuilding the staging payload, `DB-002` is now closed as a structural defect.

Verified staging outcomes after the post-closure rebuild:

- global `known_content_defect`
  - from `95`
  - to `92`
- `database-applications` `known_content_defect`
  - from `3`
  - to `0`

The three audited items now remain draft only for:

- `needs_autograde_rule_review`
- `needs_explanation_enrichment`

and no longer carry `known_content_defect`.

### Important extra fix discovered during verification

While checking this, it became clear that:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

was still treating closed defects as open when parsing the defect register.

That parser has now been aligned with the Stage 4 gate logic so closed defects do not keep blocking later promotion checks unfairly.

## 2026-05-03 update: cross-topic true/false structural normalization

New re-audit doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-true-false-structural-reaudit-2026-05-03.md`

This structural fix addressed the repeated cross-topic defect where eligible single-statement binary judgment items were being staged as `match_table` instead of `true_false`.

### Structural change applied

In:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`

`infer_format(...)` now classifies an item as `true_false` when:

- the qtype explicitly says `True / False` or `True/False`
- the stem contains clear binary-judgment prompts such as:
  - `True or False`
  - `State whether`
  - `Select whether`
  - `Decide whether`
  - `Tick True or False`
- or the answer is exactly `True` / `False` and the item has neither options nor matching/list blocks

### Verified effects after rebuild

After rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

the staging summary now shows:

- `misclassified_true_false`
  - from `65`
  - to `0`
- `needs_structured_answer_normalization`
  - from `174`
  - to `101`

The Stage 4 gate no longer has any `structural_draft` / `critical` split caused by true/false misclassification:

- `editorial_draft`: `904`

Verified sample items now stage correctly as `true_false`:

- `digital-data.practice_bank.topic_01_digital_data.q008`
- `cyberspace-network-security-and-data-transfer.past_paper.topics_07_08_09.q047`
- `health-and-safety.practice_bank.topic_09_12_wider_impact.q011`

The Phase 1 promotion bridge was also rechecked via:

- `/private/tmp/unit1_phase1_live_payload_true_false_check.json`

and now reports:

- `true_false_still_modeled_as_match_table`
  - `0`

### Defects closed by this re-audit

- `SS-001`
- `DD-002`
- `SW-003`
- `HW-002`
- `CY-002`
- `CL-002`
- `EL-002`
- `EMP-001`
- `HS-001`
- `DA-001`

## 2026-05-03 update: cross-topic match-table structural normalization

New re-audit doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-match-table-structural-normalization-2026-05-03.md`

This structural pass targeted the repeated family of legitimate match-style questions that were still staged too loosely for trustworthy promotion.

### Structural change applied

In:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`

the builder now attempts to derive explicit match-table structures whenever enough information can be recovered safely from:

- list-block rows
- `Terms:` text
- arrow-mapped prompt/answer text
- simple coded stems like `Bitmap (B)` / `Vector (V)`

For those questions, the bundle now carries:

- `options_json.rows`
- `options_json.choices`
- `correct_answer_json.pairs`

The Phase 1 promotion bridge in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

was also updated to prefer these structured match payloads directly.

### Verified effects after rebuild

After rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

the bank now contains:

- `structured_match_table_questions`
  - `54`

and the staging summary shows:

- `needs_structured_answer_normalization`
  - from `72`
  - to `48`

Verified examples now staging correctly include:

- `digital-data.past_paper.topics_01_02.q006`
- `database-applications.past_paper.topics_03_04.q007`
- `database-applications.past_paper.topics_03_04.q027`
- `database-applications.past_paper.topics_03_04.q029`
- `database-applications.past_paper.topics_03_04.q035`
- `network-technologies.past_paper.topics_05_06.q014`
- `digital-data.practice_bank.topic_01_digital_data.q039`

### Bridge verification

A Phase 1 bridge check via:

- `/private/tmp/unit1_phase1_live_payload_post_match_norm.json`

showed no match-table-specific rejection reasons after this normalization pass.

This means the newly structured match items are no longer just “cleaner in staging”; they are also acceptable to the live-payload bridge shape.

## 2026-05-04 update: residual structured-answer normalization closed as a structural blocker family

New doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-residual-structured-answer-normalization-2026-05-04.md`

Follow-on structural work completed in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260503221500_phase1_runtime_v2.sql`

This pass did four things:

1. recovered the last comma-separated `Terms:` / `Measures:` practice-bank match items;
2. normalized `also accept ...` short-answer prose into explicit accepted-answer lists;
3. reclassified `Short factual` items from generic `structured_response` to `short_text`;
4. normalized the residual `Any 2 / Any 3 from` family into structured multi-gap `fill_gap` answers with distinct-answer enforcement.

### Verified outcome after rebuild

After rebuilding:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

The structural blocker count changed from:

- `needs_structured_answer_normalization`
  - `31`
  - to `12`
  - to `0`

At this point, the staging summary contains **no remaining structural-normalization flags**.

### Controlled fixture verification

A local approved fixture was run through the Phase 1 bridge using:

- `digital-data.practice_bank.topic_01_digital_data.q033`
- `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q038`

Result:

- the cyberspace item promoted cleanly as a `fill_gap` runtime payload with 3 answer boxes and `require_distinct: true`
- the digital-data item was rejected only because of the already-open defect `DD-003`

### Full-bank bridge verification

A full-bank bridge check at:

- `/private/tmp/unit1_phase1_live_payload_full_post_structural.json`

showed:

- `904` staged questions
- `0` promoted
- `904` rejected

But crucially, there were **no structural rejection reasons** left in the summary. Remaining blockers are now editorial / governance only:

- `staging_status_not_allowed:draft`
- `missing_explanation`
- `flag_needs_explanation_enrichment`
- `flag_needs_objective_mapping`
- open audited defects

### Current verified staging baseline

From the rebuilt staging payload:

- `question_count`: `904`
- `asset_count`: `29`
- `ready_for_review_count`: `0`
- `draft_count`: `904`
- `flag_counts`:
  - `needs_explanation_enrichment`: `904`
  - `needs_objective_mapping`: `48`
  - `transformed_exam_item`: `263`
  - `needs_autograde_rule_review`: `145`
  - `known_content_defect`: `51`
  - `supplementary_derived_item`: `6`
  - `practice_question_needs_source_normalization`: `483`

This is an important milestone: the remaining blockers are now about content trust, teaching explanations, unresolved objective mapping, and open audited defects rather than hidden parser/runtime ambiguity.

## 2026-05-04 update: grouped-alias structural re-audit closed four more defect families

New doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-grouped-alias-structural-reaudit-2026-05-04.md`

Follow-on work completed in:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_01_digital_data.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260503221500_phase1_runtime_v2.sql`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`

This pass did three important things:

1. removed the last ambiguous source prompt in `DD-003` by rewriting the `short video clip` storage-unit question to target `Megabyte (MB)` safely;
2. normalized the remaining ordered multi-gap answers such as:
   - `Teleworking; internet`
   - `productivity; job losses`
   - `spine; lumbar`
   - `Virtual; Learning`
3. introduced grouped alias support for shared-pool fill-gap answers so concept-level distinctness is preserved for items such as:
   - `RSI` / `Repetitive Strain Injury`
   - `Reusability`
   - `Accessibility`
   - `Environmentally friendly`

### Controlled promotion verification

A dry run was executed with an empty defect file at:

- `/private/tmp/stage4_alias_recheck_live_nodefects.json`

Summary:

- `14` staged
- `14` promoted
- `0` rejected

This confirmed that the normalized question shapes are promotable by the Phase 1 bridge and no longer structurally blocked.

### Defect-register closures

The following groups are now closed:

- `DD-003`
- `EMP-002`
- `HS-002`
- `DA-002`

### New verified staging baseline

After closing those groups and rebuilding the staging payload:

- `known_content_defect`
  - from `51`
  - to `36`

Current verified summary from:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

is now:

- `question_count`: `904`
- `asset_count`: `29`
- `ready_for_review_count`: `0`
- `draft_count`: `904`
- `flag_counts`:
  - `needs_explanation_enrichment`: `904`
  - `needs_objective_mapping`: `48`
  - `transformed_exam_item`: `263`
  - `needs_autograde_rule_review`: `145`
  - `known_content_defect`: `36`
  - `supplementary_derived_item`: `6`
  - `practice_question_needs_source_normalization`: `483`

This is a material trust improvement: the remaining blockers are increasingly concentrated in genuine content/editorial issues rather than answer-shape ambiguity.

## 2026-05-04 update: Software transformed-item defect family closed

New doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-software-focused-reaudit-2026-05-04.md`

Source file changed:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_01_02.md`

Corrected items:

- `software.past_paper.topics_01_02.q001`
- `software.past_paper.topics_01_02.q008`
- `software.past_paper.topics_01_02.q009`

These were rewritten from weak match-style transformations into safer, more faithful short/list prompts that now stage as `fill_gap` with explicit accepted concepts and distinct-answer enforcement.

### Controlled promotion verification

Dry run:

- `/private/tmp/stage4_software_recheck_live.json`

Summary:

- `3` staged
- `3` promoted
- `0` rejected

### Defect-register impact

Closed:

- `SW-001`
- `SW-002`

After closing those groups and regenerating the staging payload, the verified summary changed to:

- `known_content_defect`
  - from `36`
  - to `33`

Current baseline from:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

now includes:

- `question_count`: `904`
- `asset_count`: `29`
- `needs_explanation_enrichment`: `904`
- `needs_objective_mapping`: `48`
- `transformed_exam_item`: `263`
- `needs_autograde_rule_review`: `148`
- `known_content_defect`: `33`
- `supplementary_derived_item`: `6`
- `practice_question_needs_source_normalization`: `483`

The rise in `needs_autograde_rule_review` from `145` to `148` is expected here because the three corrected software items now stage as explicit text-entry/fill-gap questions, which is the correct shape for faithful auto-marking review.

## 2026-05-04 update: Topic 10 transformed-item defect family closed

New doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-topic-10-transformation-reaudit-2026-05-04.md`

Source file changed:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_10_11_12.md`

Corrected transformed past-paper items:

- `changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q001`
- `q002`
- `q004`
- `q005`
- `q006`
- `q007`

These were rewritten from weak recognition MCQs into stronger recall-oriented `short_text` / `fill_gap` items with explicit accepted-answer structures.

### Controlled promotion verification

Exact transformed-family dry run:

- `/private/tmp/stage4_topic10_pastpaper_live.json`

Summary:

- `6` staged
- `6` promoted
- `0` rejected
- promoted formats:
  - `short_text`: `5`
  - `fill_gap`: `1`

### Defect-register impact

Closed:

- `EMP-003`

After regenerating the staging payload, the verified baseline from:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

now includes:

- `question_count`: `904`
- `asset_count`: `29`
- `needs_explanation_enrichment`: `904`
- `needs_objective_mapping`: `50`
- `transformed_exam_item`: `263`
- `needs_autograde_rule_review`: `153`
- `known_content_defect`: `12`
- `supplementary_derived_item`: `6`
- `practice_question_needs_source_normalization`: `483`

Topic-level `known_content_defect` is now concentrated entirely in:

- `digital-applications`: `12`

Recommended next trust-first target:

- `DA-003`
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`

## 2026-05-04 update: Digital Applications transformed-item defect family closed

New doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-topic-12-transformation-reaudit-2026-05-04.md`

Source file changed:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_10_11_12.md`

Corrected transformed past-paper items:

- `digital-applications.past_paper.topics_10_11_12.q001`
- `q002`
- `q003`
- `q005`
- `q006`
- `q007`
- `q008`
- `q009`
- `q010`
- `q011`
- `q012`
- `q013`

These were rewritten from recognition-heavy MCQs into short-recall prompts with explicit accepted-answer structures.

### Controlled promotion verification

Exact transformed-family dry run:

- `/private/tmp/stage4_topic12_pastpaper_live.json`

Summary:

- `12` staged
- `12` promoted
- `0` rejected
- promoted formats:
  - `short_text`: `12`

### Defect-register impact

Closed:

- `DA-003`

After regenerating the staging payload, the verified baseline from:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

now includes:

- `question_count`: `904`
- `asset_count`: `29`
- `needs_explanation_enrichment`: `904`
- `needs_objective_mapping`: `50`
- `transformed_exam_item`: `263`
- `needs_autograde_rule_review`: `165`
- `known_content_defect`: `0`
- `supplementary_derived_item`: `6`
- `practice_question_needs_source_normalization`: `483`

This is the first verified baseline with no open `known_content_defect` blockers left in the bank.

Recommended next trust-first move:

- shift from source-level defect closure back to structural remediation
- best candidates:
  - remaining `needs_objective_mapping` gaps (`50`)
  - remaining `needs_autograde_rule_review` set (`165`)

## 2026-05-04 update: Objective mapping reached full staged coverage

New doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-objective-mapping-closure-2026-05-04.md`

Key file changed:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`

After a catalog-expansion pass and sequential rebuild of:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

The verified baseline in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

now reports:

- `objective_mapped_count`: `904`
- `objective_unmapped_count`: `0`
- `needs_objective_mapping`: removed from `flag_counts`
- `known_content_defect`: `0`

This means the two completed trust milestones are now:

1. no open `known_content_defect` blockers;
2. no unresolved objective-mapping gaps.

Recommended next trust-first workstream:

- `needs_autograde_rule_review` (`165` remaining)

## 2026-05-04 update: structural autograde blockers cleared

New/updated docs:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-autograde-rule-structural-reaudit-2026-05-04.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-accuracy-gate.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-5-phase-1-implementation-spec-2026-05-03.md`

Key files changed:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

The autograde gate was tightened so safe text-entry structures no longer carry
blanket `needs_autograde_rule_review` flags. The final residual item:

- `digital-data.practice_bank.topic_01_digital_data.q012`

is now treated as a real ordering task:

- `format`: `drag_drop`
- `response_schema_json.kind`: `ordering`
- `autograde_rules_json.kind`: `ordering`

Sequential rebuild of:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

now reports:

- `question_count`: `904`
- `asset_count`: `29`
- `known_content_defect`: `0`
- `needs_objective_mapping`: `0`
- `needs_autograde_rule_review`: `0`
- `needs_explanation_enrichment`: `904`
- `transformed_exam_item`: `263`
- `supplementary_derived_item`: `6`
- `practice_question_needs_source_normalization`: `483`

A controlled one-question promotion fixture for the ordering item promoted
successfully:

- `1` staged
- `1` promoted
- `0` rejected
- promoted format: `drag_drop`

Current trust-first blocker:

- explanation enrichment remains across all `904` questions

## 2026-05-04 update: first-pass explanations added

New doc:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-explanation-enrichment-pass-2026-05-04.md`

Key files changed:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/unit1_objectives.py`

The import bundle now generates a first-pass teaching explanation for every
question from:

- the normalized correct answer;
- the question format;
- mark-scheme points where available; and
- the mapped learning objective or objectives.

The explanation pass also tightened objective inference:

- MCQ objective inference now includes the correct option text, not just the
  answer letter.
- Network device terms such as router, switch, NIC and file server are
  prioritised toward the network-devices objective.
- Cloud-risk and GPS-risk/use prompts are routed to more appropriate
  objectives.
- The broad legal `act` cleanup signal was removed because it could falsely
  match words such as `fact`.

Sequential rebuild now reports:

- `question_count`: `904`
- `asset_count`: `29`
- `known_content_defect`: `0`
- `needs_objective_mapping`: `0`
- `needs_autograde_rule_review`: `0`
- `needs_explanation_enrichment`: removed from `flag_counts`
- `ready_for_review_count`: `904`
- `draft_count`: `0`

Remaining flags:

- `transformed_exam_item`: `263`
- `supplementary_derived_item`: `6`
- `practice_question_needs_source_normalization`: `483`

Promotion boundary check:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

returned:

- `904` staged
- `0` promoted
- `904` rejected
- only rejection reason: `staging_status_not_allowed:ready_for_review`

This confirms the bank is reviewable, not live. Questions still need explicit
owner approval before promotion.

Technical dry run:

- `/private/tmp/unit1_ready_for_review_live_dryrun.json`

was generated with `--allow-status ready_for_review` to test runtime
compatibility only.

Initial dry run exposed:

- multi-row true/false items that needed structured `match_table` promotion;
- one database short-answer item incorrectly detected as `drag_drop`.

Fixes were applied in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

Final technical dry run:

- `904` staged
- `904` technically promotable
- `0` rejected

Strict live payload was then regenerated normally and remains:

- `0` promoted
- `904` rejected
- rejection reason: `staging_status_not_allowed:ready_for_review`

Current trust-first blocker:

- transformed/practice review and owner approval

## 2026-05-04 update: teacher review export and readiness audit

New scripts:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_teacher_review_report.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/audit_stage4_question_bank_readiness.py`

Generated teacher review files:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-teacher-question-review.csv`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-teacher-question-review-summary.csv`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-teacher-question-review-summary.json`

Generated readiness audit:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-question-bank-readiness-audit-2026-05-04.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-question-bank-readiness-audit-2026-05-04.json`

Teacher review export status:

- `938` question rows exported
- `12` topic summary rows exported
- blank `teacher_decision` and `teacher_comment` columns included for review workflow
- each row includes topic, difficulty, format, review priority, review flags, source, objectives, family code, assets, stem, options/prompt, answer preview, mark-scheme points, explanation, and teacher notes

Readiness audit headline:

- staged bank remains technically structured and reviewable
- `938` questions are still `ready_for_review`, not approved/live
- linked visual assets: `29` assets across `29` questions
- difficulty distribution: `444` easy, `325` medium, `169` expert
- format distribution: `611` MCQ, `97` match table, `90` fill gap, `65` true/false, `74` short text, `1` drag-drop
- review flags: `263` transformed exam items, `40` supplementary derived items, `483` practice questions needing source-label normalisation review

Pedagogical readiness finding:

- a difficulty reclassification pass now treats defensible multi-mark/source-style items as expert
- a tracked supplementary file was added: `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/content/unit1_supplementary_questions/expert_balancing_2026_05.md`
- every topic/difficulty bucket now has at least `10` questions, so no level is blocked from forming a 10-question session on count alone
- several buckets remain thin or have weak family depth; this is a quality/depth issue rather than a hard runtime blocker

Infrastructure finding:

- `question_family_code` and `selection_weight` exist in the schema and payload
- new migration added: `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260504114500_weighted_family_session_picker.sql`
- the migration replaces `public.pick_session_questions` with a weighted family-aware picker
- the picker now prefers fresh questions, avoids duplicate question families where possible, respects `selection_weight`, and relaxes recency/family constraints only when the approved bucket is too thin
- this migration is in the repo only until `supabase db push` is run
- remaining content blocker: teacher approval; the generated bank is review-ready but not approved/live

Student dashboard update:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/StudentStatsPanel.tsx` was rebuilt around topic-centred revision stats
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/api.ts` now fetches topic title/slug with completed sessions
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts` now allows `sessions.topics`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentTopicPage.tsx` passes the full topic list into the stats panel
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/styles/global.css` includes styles for insight cards, topic snapshot table, and skill list

The student stats now show:

- strongest attempted topic
- topic needing attention
- least-recently revised topic
- streak
- topic revision snapshot table with sessions, average accuracy, last revised date, and advice
- progress by difficulty
- recent topic trend
- weakest question-skill tags

Verification after this update:

- `npm run build` passes
- Python script compile check passes
- `git diff --check` passes

## 2026-05-04 update: Stage 5 approval gate

New script:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage5_approval_payload.py`

Purpose:

- reads the teacher review CSV
- treats blank `teacher_decision` values as not approved
- accepts only explicit approval decisions into the approved Stage 5 payload
- keeps `reject` and `needs edit` rows out of student-facing payloads
- runs the strict Phase 1 live-payload promotion checks after approval
- writes local files only; it does not contact Supabase and does not deploy

Generated local outputs:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage5_approved_staging_payload.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage5_approved_live_payload.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-approval-summary.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-approval-bucket-summary.csv`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-5-approval-gate-2026-05-04.md`

Current real review CSV result:

- `938` source questions
- `0` approved
- `938` undecided
- `0` invalid decisions
- `0` promoted live questions

This is intentional because the teacher review file has not yet been marked.
The gate is therefore working as a safety control: nothing unapproved can reach
student sessions.

Temporary verification fixture:

- a temporary `/private/tmp/unit1-review-all-approved.csv` was generated with every row marked `approve`
- running the Stage 5 gate against that fixture promoted `938 / 938` questions
- runtime rejections: `0`
- linked assets: `29`
- linked objective rows: `1035`
- underfilled topic/difficulty buckets: `0`

This proves the approval gate is strict when the CSV is blank and complete when
the CSV is fully approved.

New local migration:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260504123000_stage5_external_import_keys.sql`

Purpose:

- adds stable `external_id` columns to `public.questions`, `public.content_sources`, and `public.question_assets`
- adds uniqueness constraints for repeatable imports
- does not affect student usernames, passwords, or auth accounts

Current status:

- Stage 5 approval tooling is local and verified
- no remote Supabase write has happened
- no GitHub Pages deployment has happened
- the next content gate is teacher approval in `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-teacher-question-review.csv`

## 2026-05-04 update: runtime visual-aid rendering check

Issue found during import-path review:

- Phase 1 runtime payloads already include `assets`
- the database runtime function can return those assets with bucket/path/caption/alt text
- however `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/QuestionRenderer.tsx` was not rendering runtime assets

Fix applied:

- runtime prompt blocks now render visual assets for `figure`, `diagram`, `table_image`, `screenshot`, `chart`, `photo`, and `image` style blocks
- unmatched prompt assets are still shown rather than ignored
- asset URLs are built from Supabase Storage public URLs using the returned bucket/path
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts` now allows `url` and `public_url` on runtime assets
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/styles/global.css` now includes responsive visual-aid styling

Verification:

- `npm run build` passes after the renderer change

Remaining deployment implication:

- the relevant image files still need to be uploaded into the matching Supabase Storage bucket/path before students can see them in the live app

## 2026-05-04 update: local visual-asset upload package

New script:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage5_asset_package.py`

Purpose:

- reads `staged_question_assets` from the Stage 4 staging payload
- resolves each asset back to the extracted source file under `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/figures`
- copies files into the local upload layout expected by Supabase Storage
- writes an upload manifest for later deployment
- does not upload anything to Supabase

Generated local package:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/question_assets_upload`

Generated manifests:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-asset-upload-manifest.csv`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-asset-upload-manifest.json`

Verification result:

- `29` asset references processed
- `25` unique storage files packaged
- `0` missing source files
- storage bucket represented: `question-imports`
