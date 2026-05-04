# Stage 5 Phase 1 Implementation Spec (2026-05-03)

## Purpose
This document turns the Stage 4 audit and remediation work into the first concrete corrective build specification.

It defines the exact implementation scope for the first engineering phase that must happen before any topic can be promoted safely for student use.

This is the phase that restores trust in four areas:
1. the runtime question contract;
2. the session lifecycle;
3. server-side scoring authority; and
4. fair handling of core self-marking question types.

## Why This Phase Exists
The current prototype has enough content and infrastructure to prove the idea, but not enough trust to deserve student reliance yet.

The audits confirmed that the current system still has these structural problems:
- the live frontend consumes an older raw `questions` shape;
- staged Stage 4 content does not match that live shape cleanly;
- the browser still decides correctness and submits it back to Supabase;
- true/false, fill-gap, list, and match-style items are not yet normalized into a dependable marking contract.

Until these are fixed, better explanations or better adaptive recommendations would be sitting on an unreliable foundation.

## Scope of Phase 1
Phase 1 covers four workstreams from the remediation plan:
1. Runtime Trust Boundary
2. Question-Type Normalization and Fair Marking
3. Staged-to-live transformation design
4. Minimum release gating for promoted questions

Phase 1 does **not** yet try to complete:
- full explanation enrichment;
- final mastery/statistics redesign;
- final adaptive routing logic;
- full topic cleanup beyond confirmed high-risk blockers;
- bulk teacher upload UI.

## Current Stage 4 Gate Baseline
After tightening the Stage 4 gate on 2026-05-03, the project now has a much
more honest pre-promotion baseline:

- `904` staged questions
- `0` `ready_for_review`
- `904` `draft`

This is correct at the current state and should be treated as a trust signal,
not a regression. It means the app no longer pretends the bank is ready for
teacher approval while explanations, objective gaps, grading-risk items, and
confirmed defects are still unresolved.

## Current Runtime Snapshot
### Frontend assumptions today
The current student runtime expects raw `Question` rows shaped like this:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/QuestionRenderer.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/scoring.ts`

Important current assumptions:
- `mcq` expects `options_json.choices: string[]`
- `match_table` expects `options_json.pairs` and `correct_answer_json.pairs`
- text formats (`fill_gap`, `short_text`, `structured_response`) use one textarea path
- `diagram_label` is partly radio-based and partly free-text
- client-side `evaluateAnswer()` decides correctness before save

### Session save flow today
The student page:
- evaluates each answer in the browser;
- stores `isCorrect` in local state;
- computes `score`, `accuracyPct`, `pointsEarned` in the browser;
- sends those values to `save_session_submission()`.

Relevant files:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentSessionPage.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/api.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260214170000_init_schema.sql`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`

### Why this is not good enough
Even after the Stage 3 migration draft improved snapshots and marks fields, the database function still trusts client-submitted correctness when it assigns `marks_awarded`.

That means the first engineering priority is not cosmetic. It is to move authority away from the browser.

## Phase 1 Target Architecture
Phase 1 introduces a clear separation between three layers:

1. **Staged Question Layer**
   - rich editorial/import structure
   - used for review and promotion

2. **Live Runtime Question Layer**
   - strict, normalized, student-safe structure
   - only this shape is used in active sessions

3. **Attempt / Scoring Layer**
   - server-side session plan
   - server-side grading
   - server-side completion totals

This means the live student app must no longer read or trust the raw editorial shape directly.

## Canonical Live Runtime Contract
Phase 1 should introduce a single normalized frontend/runtime type called `RuntimeQuestion`.

Suggested TypeScript shape:

```ts
export type RuntimeQuestionFormat =
  | "mcq"
  | "true_false"
  | "match_table"
  | "fill_gap"
  | "short_text"
  | "multi_select"
  | "drag_drop"
  | "diagram_label";

export interface RuntimeQuestion {
  session_item_id: string;
  question_id: string;
  topic_id: string;
  difficulty: "easy" | "medium" | "expert";
  adaptive_tier: "support" | "core" | "challenge";
  format: RuntimeQuestionFormat;
  max_marks: number;
  family_code: string | null;
  stem: string;
  prompt_blocks: RuntimePromptBlock[];
  assets: RuntimeAsset[];
  response_schema: RuntimeResponseSchema;
  autograde_rules: RuntimeAutogradeRules;
  explanation: string;
  tags: string[];
  objective_ids: string[];
}
```

### Important design decision
The live app should not directly render from `questions.options_json` and `questions.correct_answer_json` anymore.

Instead:
- the promotion layer produces a normalized runtime payload;
- session start returns that payload;
- session snapshots store that payload;
- the frontend renders only this runtime shape.

That avoids repeated contract drift.

## Supported Student-Facing Formats in Phase 1
Phase 1 should only allow these formats into live student sessions once normalized:

### 1. `mcq`
Use for single correct option.

```json
{
  "response_schema": {
    "kind": "single_choice",
    "choices": [
      { "id": "a", "label": "Bluetooth" },
      { "id": "b", "label": "Wi-Fi" }
    ]
  },
  "autograde_rules": {
    "kind": "single_choice",
    "correct_choice_id": "a"
  }
}
```

### 2. `true_false`
Use for one statement with a boolean answer.

```json
{
  "response_schema": {
    "kind": "true_false",
    "statement": "Fibre optic cable transmits data as electrical signals.",
    "true_label": "True",
    "false_label": "False"
  },
  "autograde_rules": {
    "kind": "true_false",
    "correct_value": false
  }
}
```

This replaces the current bad practice of storing single-statement T/F as `match_table`.

### 3. `match_table`
Use only where there is a genuine multi-row matching task.

```json
{
  "response_schema": {
    "kind": "match_table",
    "rows": [
      { "id": "row1", "label": "Connects devices within one LAN" },
      { "id": "row2", "label": "Stores shared files" }
    ],
    "choices": [
      { "id": "switch", "label": "Switch" },
      { "id": "file_server", "label": "File server" }
    ]
  },
  "autograde_rules": {
    "kind": "match_table",
    "pairs": [
      { "row_id": "row1", "choice_id": "switch" },
      { "row_id": "row2", "choice_id": "file_server" }
    ]
  }
}
```

### 4. `fill_gap`
Use where the prompt explicitly contains gap identifiers and accepted-answer rules.

This category now also includes transformed `Any 2 / Any 3 from` practice-bank
items when the safest self-marking representation is a fixed number of answer
boxes drawing from a shared accepted-answer pool with distinct entries
required.

Where a single conceptual answer has more than one acceptable wording, the
runtime contract may use `accepted_groups` instead of a flat `accepted` list.
This lets the grader:

- accept aliases such as `RSI` / `Repetitive Strain Injury`;
- preserve concise concept labels such as `Reusability`;
- enforce `require_distinct` at the concept level rather than just the typed
  string level.

```json
{
  "response_schema": {
    "kind": "fill_gap",
    "gaps": [
      { "id": "gap1", "label": "Gap 1" },
      { "id": "gap2", "label": "Gap 2" }
    ]
  },
  "autograde_rules": {
    "kind": "fill_gap",
    "gaps": [
      {
        "id": "gap1",
        "accepted": ["router"],
        "normalization": "token"
      },
      {
        "id": "gap2",
        "accepted": ["switch"],
        "normalization": "token"
      }
    ],
    "require_all": true,
    "require_distinct": true
  }
}
```

### 5. `short_text`
Use for short factual responses only.

```json
{
  "response_schema": {
    "kind": "short_text",
    "placeholder": "Type your answer",
    "max_length": 120
  },
  "autograde_rules": {
    "kind": "accepted_terms",
    "accepted": ["bluetooth"],
    "normalization": "token",
    "match_mode": "exact"
  }
}
```

### 6. `multi_select`
Use for select-all-that-apply items only after explicit rule normalization.

```json
{
  "response_schema": {
    "kind": "multi_select",
    "choices": [
      { "id": "a", "label": "High bandwidth" },
      { "id": "b", "label": "Electrical signals" },
      { "id": "c", "label": "Less susceptible to interference" }
    ],
    "min_select": 1,
    "max_select": 2
  },
  "autograde_rules": {
    "kind": "multi_select",
    "correct_choice_ids": ["a", "c"],
    "require_exact_set": true
  }
}
```

### 7. `drag_drop`
Keep only for clearly ordered sequences.

### 8. `diagram_label`
Keep only where the answer is still objectively markable, ideally as choice-based marker identification rather than open free text.

## Blocked or Deferred Formats in Phase 1
These should not reach students unchanged in Phase 1:

### Raw `structured_response`
Reason:
- current implementation is just textarea plus exact string equality;
- audits showed this is unfair and misleading.

Policy:
- a staged `structured_response` must be transformed into one of the supported live formats above;
- otherwise it stays out of student sessions.

### Prose-only match answers
If the answer still exists only as a raw text block like `1-A, 2-B, 3-C`, it is not Phase 1-ready.

### Raw `Any 2 from` prose
If accepted-answer logic is still trapped inside prose, it is not Phase 1-ready.

## Session Lifecycle v2
Phase 1 should replace the current client-led session flow with a server-authoritative flow.

### Step 1: `start_session_v2`
A new RPC should:
1. verify the student can start this difficulty today;
2. pick the session question set on the server;
3. create the `sessions` row;
4. create planned `session_questions` rows immediately;
5. snapshot the normalized runtime question payload for each planned row;
6. return the ordered runtime question list to the frontend.

This replaces the current pattern where:
- the client calls `pickSessionQuestions()`;
- then separately creates the session row;
- and does not persist the planned question set until completion.

### Step 2: `grade_session_question_v2`
A new RPC should:
1. accept `session_item_id` and the student response only;
2. load the authoritative runtime payload from `question_snapshot_json`;
3. apply server-side grading rules;
4. persist:
   - `student_answer_json`
   - `is_correct`
   - `marks_awarded`
   - response time
   - hint used
5. return authoritative feedback to the frontend:
   - correctness state
   - marks awarded
   - expected corrections where relevant
   - explanation text

This preserves the current user experience of immediate feedback without relying on browser authority.

### Step 3: `complete_session_v2`
A new RPC should:
1. verify all required session items are in a graded state;
2. total marks from stored server-side values;
3. update `sessions.completed_at`, `points_earned`, `points_available`, `accuracy_pct`, `score`;
4. increment `daily_caps`;
5. return the summary payload used by the summary page.

Important rule:
- the client must no longer submit `score`, `accuracyPct`, or `isCorrect` as authoritative values.

## Server-Side Scoring Authority
### Phase 1 principle
The browser may still help with draft UX, but the database becomes the source of truth.

### What stays client-side
Safe client-side roles:
- capturing draft responses;
- tracking local input state;
- showing loading/saving UI;
- optionally pre-validating that a response is not empty.

### What moves server-side
Must move server-side:
- exact correctness decision;
- partial-mark logic;
- accepted-answer normalization;
- total marks and accuracy calculation;
- session completion state.

### Scoring result model
Phase 1 should support this server-side result shape per question:

```json
{
  "result": "correct | partial | incorrect",
  "marks_awarded": 1,
  "marks_available": 1,
  "feedback": {
    "summary": "Correct",
    "corrections": [],
    "accepted_answer_preview": []
  }
}
```

That gives us room for partial marks later without redesigning the contract again.

## Staged-to-Live Transformation Layer
Phase 1 needs a dedicated promotion step between `staged_questions` and live `questions`.

Suggested new script:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

Suggested responsibilities:
1. read approved staged questions only;
2. reject unsupported or blocked shapes;
3. normalize staged metadata into runtime-safe structures;
4. generate:
   - live `questions` row payloads;
   - `question_assets` payloads;
   - `question_asset_links` payloads;
   - `question_objectives` payloads;
   - source-link payloads;
5. validate every promoted question against the canonical live contract.

### Promotion gates
A staged question must fail promotion if any of these are true:
- `staging_status` is not approved;
- `explanation` is empty;
- `needs_explanation_enrichment` remains present;
- `needs_objective_mapping` remains present;
- format is unsupported for live use;
- true/false is still modeled as match-table;
- accepted-answer logic is still raw prose;
- linked prompt assets are unresolved;
- review notes contain an unresolved blocker;
- the question belongs to a confirmed content defect not yet closed.

## Schema Touchpoints
Phase 1 should touch these schema areas.

### 1. `question_format` enum
Add:
- `true_false`

Keep:
- `mcq`
- `drag_drop`
- `match_table`
- `fill_gap`
- `short_text`
- `diagram_label`
- `multi_select`

Do not release raw `structured_response` questions in student sessions until transformed.

### 2. `questions`
Continue using the Stage 3 enriched fields, but with a stricter policy:
- `content_blocks_json` becomes the authoritative prompt-block source;
- `response_schema_json` becomes the authoritative renderer contract;
- `autograde_rules_json` becomes the authoritative scoring contract;
- `options_json` may be retained for backward compatibility/admin preview, but Phase 1 student runtime should stop depending on it as the primary contract.

### 3. `session_questions`
Use it as the authoritative session-plan table, not just a completion dump.

Phase 1 expectations:
- rows are created at session start;
- `question_snapshot_json` stores the live runtime question payload actually delivered;
- `marks_available` and `marks_awarded` are authoritative;
- `question_id` remains linked when possible, but the snapshot is what protects historical integrity.

### 4. New or replaced RPCs
Recommended additions:
- `public.start_session_v2(...)`
- `public.grade_session_question_v2(...)`
- `public.complete_session_v2(...)`

Recommended deprecation path:
- keep `pick_session_questions()` for now during migration work only;
- retire student-facing reliance on `save_session_submission()` once v2 flow exists.

### 5. Optional helper functions
Recommended SQL helper functions:
- `public.normalize_answer_token(text)`
- `public.normalize_answer_phrase(text)`
- `public.grade_runtime_question(jsonb, jsonb)`

These would make grading rules reusable inside RPCs.

## File-by-File Implementation Plan
### Frontend
#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts`
Add:
- `RuntimeQuestionFormat`
- `RuntimeQuestion`
- typed prompt block definitions
- typed response schema definitions
- typed grading result definitions

Keep legacy `Question` temporarily only while migration work is incomplete.

#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/api.ts`
Add new API wrappers for:
- `startSessionV2()`
- `gradeSessionQuestionV2()`
- `completeSessionV2()`

Deprecate the direct student use of:
- `pickSessionQuestions()`
- `createSession()`
- `saveSessionSubmission()`

#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/QuestionRenderer.tsx`
Refactor to render from `RuntimeQuestion.response_schema` rather than ad hoc `options_json` assumptions.

Phase 1 renderer paths:
- single choice
- true/false
- match table
- fill gap
- short text
- multi select
- drag drop
- diagram label

#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/scoring.ts`
Reduce this file’s authority.

After Phase 1 it should no longer be the source of truth for final student marking.

Possible retained roles:
- local draft completeness checks
- correction-format helpers for UI rendering
- optimistic preview only if it uses exactly the same normalized contracts

#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentSessionPage.tsx`
Refactor to:
- start a full server-planned session;
- store `session_item_id` per question;
- submit each answer to `gradeSessionQuestionV2()` on `Check Answer`;
- move to the next question only after authoritative feedback is returned;
- complete the session with `completeSessionV2()`.

### Supabase SQL / schema
#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260214170000_init_schema.sql`
Do not patch this migration directly if avoidable.

Instead create a new migration that:
- adds `true_false` support;
- introduces v2 session RPCs;
- leaves old functions in place temporarily for compatibility during local transition.

#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`
Keep this as the structural baseline.

Add a follow-on migration rather than rewriting this file again unless absolutely necessary.

New migration should:
- formalize `question_snapshot_json` contents expected by v2;
- create v2 grading/session functions;
- align policies/permissions if needed.

### Pipeline scripts
#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
Tighten format inference so it can explicitly emit:
- `true_false`
- structured fill-gap gap arrays
- structured match rows and choices
- accepted-answer schemas for short factual items

#### `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
Tighten the review gate so missing explanation and missing objective mapping remain blocking rather than merely flagged.

#### New script
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

This becomes the normalization bridge from staged editorial data to live runtime-safe data.

## Release Gates for Phase 1 Completion
Phase 1 should be considered complete only when all of these are true:

1. Student sessions no longer trust browser-submitted correctness.
2. Session totals are computed entirely server-side.
3. True/false uses its own normalized runtime path.
4. Live student questions render from `response_schema_json` and `autograde_rules_json`, not raw legacy `options_json` assumptions.
5. `session_questions` rows are created at session start and store question snapshots.
6. Promotion tooling rejects unsupported or unresolved staged items.
7. At least one audited high-risk topic can be promoted end-to-end through the new contract successfully.
8. Browser refresh during an in-progress session can rehydrate the planned session question set safely.

## Recommended First Topic for End-to-End Validation
Use `Network technologies` as the first full contract-validation topic after the infrastructure work.

Reason:
- it is high-risk;
- it has diagrams/assets;
- it has confirmed content defects already known;
- if the contract works there, it will be a meaningful proof.

## Testing Plan for Phase 1
### Contract tests
- every live question payload validates against the runtime schema;
- no `true_false` item is still shaped like `match_table`;
- no blocked staged format promotes successfully.

### SQL / grading tests
- identical answers always grade identically on repeated submission;
- client cannot inflate score by lying about correctness;
- partial marks behave as designed where enabled;
- daily cap increments only on completed sessions.

### Frontend tests
- student can start a session;
- answer a question;
- receive authoritative feedback;
- refresh the page;
- continue the session;
- finish the session;
- view a correct summary.

### Content safety tests
- one corrected high-risk topic passes end-to-end;
- one true/false-heavy topic passes end-to-end;
- one diagram-heavy topic passes end-to-end.

## Open Decisions That Can Be Deferred Briefly
These do not need to block the first Phase 1 build, but they should be noted:
1. whether `structured_response` should later become a supported live type or always be transformed;
2. whether live question payloads should be materialized into a dedicated view/RPC JSON shape or assembled inside grading/session RPCs;
3. whether partial-mark support for list questions should be enabled in Phase 1 or Phase 2.

## Immediate Next Build Order
Once this spec is approved, the next coding sequence should be:
1. create the follow-on Supabase migration for `true_false` and v2 RPCs;
2. add `RuntimeQuestion` and response-schema types in frontend code;
3. implement `startSessionV2`, `gradeSessionQuestionV2`, and `completeSessionV2` client wrappers;
4. refactor `QuestionRenderer` and `StudentSessionPage` onto the new contract;
5. build `build_phase1_live_payload.py`;
6. tighten the Stage 4 staging gate;
7. run the first end-to-end validation topic through the new flow.

## Progress Update (2026-05-03, later verification)
The first four implementation steps above are now complete in the repo:

1. Phase 1 migration draft created:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260503221500_phase1_runtime_v2.sql`
2. Runtime frontend types added:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts`
3. V2 API wrappers added:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/api.ts`
4. Renderer and session page refactored:
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/QuestionRenderer.tsx`
   - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentSessionPage.tsx`

Verification completed for this refactor pass:

- `tsc -b --verbose` passed
- `npm run build` passed

Important limitations still in force:

- the migration is still repo-only and has not been applied to Supabase
- the v2 path therefore remains a coded-but-not-yet-activated runtime path
- `StudentSessionPage` currently relies on explicit fallback to the legacy session flow until the backend migration is applied and validated

That means the next build priority has now shifted to:

1. building `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`
2. aligning staging rejection rules with the new runtime contract
3. then validating a corrected first topic end to end

## Progress Update (2026-05-03, live payload bridge)
The Stage 5 promotion bridge now exists:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

Its current responsibilities are:

1. read the Stage 4 staging payload;
2. require approved staging status by default;
3. reject questions with:
   - missing explanations;
   - unresolved objective mapping;
   - unresolved prompt assets;
   - open defect-register entries;
   - unsupported/unsafe live-format shapes;
4. normalize promotable items into runtime-safe question payloads;
5. emit sidecar payloads for:
   - `content_sources`
   - `question_source_links`
   - `question_assets`
   - `question_asset_links`
   - `question_objectives`

### Verified behaviour

#### Strict default run
Input:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

Output:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_phase1_live_payload.json`

Observed result:
- `904` staged questions
- `0` promoted
- `904` rejected

This is the correct outcome at the current project state because the staged bank is still blocked by:
- `ready_for_review` rather than approved status;
- missing explanations everywhere;
- unresolved objective mapping in some items; and
- confirmed open defects in the defect register.

This is an important trust signal, not a failure. It proves the bridge is refusing to over-promote weak content.

#### Controlled fixture test
A temporary 3-question approved fixture was created locally and passed through the bridge successfully.

Verified promoted formats:
- `mcq`
- `match_table`
- `fill_gap`

Observed result:
- `3` promoted
- `0` rejected

This confirms the bridge is not only rejecting content correctly but also normalizing safe items into:
- runtime `response_schema_json`
- runtime `autograde_rules_json`
- legacy-compatible `options_json`
- legacy-compatible `correct_answer_json`

The bridge is therefore working in both directions that matter:
- strict rejection of unsafe staged content;
- valid runtime payload construction for safe approved content.

#### 2026-05-04 extension: structured multi-answer fill gaps
A follow-on structural pass normalized the residual `Any 2 / Any 3 from`
family into explicit multi-gap `fill_gap` payloads with:

- a shared accepted-answer pool;
- distinct-answer enforcement;
- successful controlled bridge promotion for a representative fixture item.

This means the Phase 1 bridge/runtime contract now has a trustworthy path for
multi-answer text-entry items without inventing distractors or weakening the
original revision demand.

#### 2026-05-04 extension: ordering / drag-drop promotion
The Phase 1 promotion bridge now supports `drag_drop` questions that use the
runtime `ordering` schema. The remaining storage-unit ordering residual:

- `digital-data.practice_bank.topic_01_digital_data.q012`

now imports as:

- `format`: `drag_drop`
- `response_schema_json.kind`: `ordering`
- `autograde_rules_json.kind`: `ordering`

A controlled one-question promotion fixture verified:

- `1` staged
- `1` promoted
- `0` rejected
- promoted format: `drag_drop`

This clears the remaining `needs_autograde_rule_review` residual from the
staged bank.

## Relationship to Existing Docs
This spec should now be read alongside:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-audit-review-2026-05-02.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-cross-topic-audit-synthesis-2026-05-03.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-remediation-plan-2026-05-03.md`

Together, those documents now answer:
- what is wrong;
- why it matters;
- what order to fix it in; and
- exactly how the first engineering correction phase should be built.
