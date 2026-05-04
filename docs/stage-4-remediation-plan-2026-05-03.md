# Stage 4 Remediation Plan (2026-05-03)

## Purpose
This plan converts the Stage 4 audit findings into a practical execution order.

It answers:
1. what we fix first;
2. which files and schema areas are involved;
3. which topic defects are highest priority; and
4. what must be complete before any student-facing release is considered.

This plan assumes:
- existing student usernames/passwords stay as they are;
- old student progress history does not need preserved for the rebuilt launch;
- the project remains login-protected;
- trustworthiness of question content and marking is the priority over speed.

## Guiding Principle
The next phase is not about adding more content first.
It is about making the existing bank trustworthy enough to deserve student use.

That means the work order should be:
1. fix the runtime/content contract;
2. fix the worst confirmed question defects;
3. fix self-marking fairness;
4. only then expand teaching explanations and adaptive behaviour.

## Workstream A — Runtime Trust Boundary

### Goal
Make the app trustworthy enough that a student's saved result actually reflects authoritative question data and authoritative marking rules.

### Why this comes first
Right now, even correct content would still be sitting on top of a weak trust boundary:
- staging payloads do not match the current live runtime contract;
- the browser still decides correctness and sends it back to Supabase;
- session data therefore is not reliable enough to power student guidance.

### Required outcomes
1. Build a staging-to-live transformation layer.
2. Move answer verification and score calculation server-side.
3. Ensure the live app consumes one stable question contract only.

### Files / areas involved
Frontend/runtime:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/QuestionRenderer.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/scoring.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentSessionPage.tsx`

Pipeline:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

Supabase/schema:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`
- existing runtime schema in:
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260214170000_init_schema.sql`

### Concrete tasks
1. Define the canonical live question contract.
   - MCQ
   - true/false
   - match
   - fill-gap
   - short factual
   - list / multi-point
2. Create a promotion/transform script from staged question shape to live runtime shape.
3. Stop saving client-asserted `isCorrect`, `score`, `accuracyPct` as authoritative.
4. Recalculate score/marks from question data on the server side.
5. Store question snapshots with attempts so future bank changes do not corrupt historical interpretation.

### Release status
- **hard blocker**

## Workstream B — Question-Type Normalization and Fair Marking

### Goal
Make the core question types fair, predictable, and structurally consistent.

### Why this comes second
This is the single biggest repeated defect family across the bank.
If we do not solve it centrally, we will keep fixing the same problem topic by topic.

### Required outcomes
1. True/false gets its own format and runtime rendering/marking path.
2. Fill-gap and short factual items support structured accepted answers.
3. List-style questions support `any N from list` logic explicitly.
4. Match questions use structured pairs, not raw prose.

### Files / areas involved
Pipeline:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`

Frontend/runtime:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/QuestionRenderer.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/scoring.ts`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/lib/types.ts`

### Concrete tasks
1. Introduce explicit true/false format.
2. Replace raw `correct_answer_json.raw` for T/F with structured boolean answer schema.
3. Replace prose-only match answers with structured pair arrays.
4. Add accepted-answer schemas for:
   - exact alternatives
   - acceptable abbreviations
   - `Any 2 from`
   - `Any 3 from`
   - multi-blank fill-gap
5. Reclassify mis-typed questions in staged data after the new rules exist.

### Highest-impact topics for this workstream
- Spreadsheet applications
- Digital data
- Cyberspace, network security and data transfer
- Cloud technology
- Ethical, legal and environmental impact
- Topic 10
- Health and safety
- Digital applications

### Release status
- **hard blocker**

## Workstream C — High-Risk Content Corrections

### Goal
Correct confirmed source/content defects that would actively misteach or confuse students.

### Why this comes third
These are not just structural issues. These are the places where the content itself could directly damage trust or accuracy.

### Priority 1 topic defects
#### Network technologies
- `NT-001`
- `NT-002`

Files/source area:
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

#### Computer hardware
- `HW-001`
- `HW-003`

Source area:
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

#### Database applications
- `DB-001`
- `DB-002`

Source area:
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`

#### Ethical, legal and environmental impact
- `EL-001`
- `EL-003`

Source area:
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`

#### Software
- `SW-004`
- plus transformation-quality concerns `SW-001`, `SW-002`

Source area:
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_02_03_software_database.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_01_02.md`

#### Cloud technology
- `CL-003`

Source area:
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_07_08_cyberspace_cloud.md`

### Concrete tasks
1. Review and correct confirmed bad answers/prompts at source.
2. Rebuild staged payload after source correction.
3. Re-run topic audits for the corrected high-risk topics.
4. Update defect register status from `confirmed` to `fixed` only after verification.

### Release status
- **hard blocker** for any topic with confirmed content defects

## Workstream D — Transformation Quality Review

### Goal
Reduce distortion introduced by splitting or flattening real exam questions into low-demand recognition items.

### Why this matters
Some transformed questions are acceptable.
Too many transformed questions in a topic can quietly turn exam revision into trivia-style recognition.

### Highest-priority topics for transformation cleanup
1. Cloud technology
2. Cyberspace, network security and data transfer
3. Ethical, legal and environmental impact
4. Changes in employment opportunities, skills requirements and work practices
5. Health and safety
6. Digital applications

### Secondary transformation review topics
1. Software
2. Spreadsheet applications
3. Database applications
4. Computer hardware

### Concrete tasks
1. Decide transformation rules for source item types:
   - `state two`
   - `give one reason`
   - `discuss`
   - matching tasks with missing context
2. Set a threshold for when an item must remain a richer response format rather than being split into MCQs.
3. For high-volume transformed topics, rewrite the worst flattened items into better self-marking formats.
4. Separate direct PPQ-derived content from supplementary mark-scheme spin-offs in metadata.

### Files / areas involved
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-*-content-audit-*.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`

### Release status
- **hard blocker** for highest-volume transformed topics
- **important quality gate** for the rest

## Workstream E — Family Codes, Duplicate Suppression, and Selection Logic

### Goal
Make session composition intelligent without collapsing distinct coverage.

### Why this is later than A-D
We should not build smarter adaptive selection until the underlying question structures and content are trustworthy.

### Required outcomes
1. Tighten `question_family_code` generation.
2. Ensure exact duplicates never appear in a session.
3. Ensure near-duplicates are suppressed only when truly appropriate.
4. Use `selection_weight` only after family quality is strong enough.

### Files / areas involved
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`
- current picker logic in:
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260214170000_init_schema.sql`
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260215160000_expert_diagram_guarantee.sql`

### Concrete tasks
1. Narrow family grouping heuristics.
2. Add review surfacing for questionable family clusters.
3. Build session-selection logic around:
   - objective coverage
   - family avoidance
   - recency
   - format balance
   - difficulty/adaptive tier

### Release status
- required before final adaptive rollout
- not the first blocker to fix

## Workstream F — Explanation Enrichment

### Goal
Add the teaching/explanation layer students need for revision confidence.

### Why this is not first
Questions with bad structure or unsafe marking should not get polished explanations first.
We should explain the right thing, not explain an untrusted thing more beautifully.

### Required outcomes
1. Every student-facing question has a short teaching explanation.
2. Explanations are syllabus-aligned and concise.
3. Explanations match the final promoted question form, not an earlier draft.

### Files / areas involved
- future enriched staged/live question payloads
- topic source docs and fact files
- explanation fields in the Stage 3 schema

### Release status
- **hard blocker** before student release
- but should begin only after A-D are substantially under control

## Workstream G — Adaptive Model and Student Stats

### Goal
Only after question reliability is strong enough, rebuild the student-facing revision intelligence.

### Required outcomes
1. Topic/objective mastery becomes the basis of stats.
2. Session recommendations use objective performance, not raw difficulty averages.
3. Students can see:
   - strongest topics
   - weakest topics
   - topics needing attention
   - recent revision gaps

### Why this is later
Bad content + strong analytics is worse than simple analytics, because it gives false confidence.

### Files / areas involved
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/components/StudentStatsPanel.tsx`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/src/pages/StudentTopicPage.tsx`
- Stage 3 mastery tables in:
  - `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/migrations/20260502190000_stage3_unit1_schema_foundation.sql`

### Release status
- can follow once question reliability and authoritative scoring are in place

## Recommended Execution Order

### Phase 1 — Trust boundary and question-type contract
Do first:
1. Workstream A
2. Workstream B

Reason:
- this gives us a trustworthy runtime and marking contract
- it removes the biggest repeated structural risks across the whole bank

### Phase 2 — Correct the worst content defects
Do second:
1. Workstream C
2. the highest-priority parts of Workstream D

Topic order:
1. Network technologies
2. Computer hardware
3. Database applications
4. Ethical, legal and environmental impact
5. Software
6. Cloud technology

Reason:
- this removes the questions most likely to actively misteach or confuse students

### Phase 3 — Improve transformed-item quality in the broad theory topics
Do third:
1. remaining high-volume transformed topics from Workstream D

Topic order:
1. Cyberspace, network security and data transfer
2. Changes in employment opportunities, skills requirements and work practices
3. Health and safety
4. Digital applications
5. Spreadsheet applications
6. Digital data

### Phase 4 — Explanation layer and promotion gate tightening
Do fourth:
1. Workstream F
2. tighten review gating further

### Phase 5 — Session intelligence and stats
Do fifth:
1. Workstream E
2. Workstream G

## Release Gates
No topic should move toward live student use unless all of the following are true:
1. no confirmed factual/content defects remain open for that topic;
2. no question types in that topic are relying on unsupported marking contracts;
3. explanations exist for all promoted student-facing questions;
4. the live runtime shape matches the promoted question shape exactly;
5. scoring is verified server-side;
6. transformed PPQ-derived items in that topic have passed editorial review.

## Immediate Next Recommendation
The very next step should be a **Phase 1 implementation plan** scoped to:
1. the live question contract;
2. the staged-to-live transformation layer;
3. server-side scoring authority; and
4. true/false normalization.

That is the highest-leverage work we can do next.
