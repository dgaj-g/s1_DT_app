# Stage 4 Cross-Topic Audit Synthesis (2026-05-03)

## Purpose
This document synthesizes the full Stage 4 topic-by-topic audit across all 12 Unit 1 topics.

It is intended to answer four practical questions:
1. Which defects repeat most often across the bank?
2. Which topics are currently the strongest and weakest?
3. What absolutely must be fixed before any student-facing release?
4. What can be deferred until a later refinement phase?

## Evidence Base
This synthesis is based on:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-audit-review-2026-05-02.md`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/stage-4-content-defect-register-2026-05-03.md`
- all 12 topic audit files dated `2026-05-02` / `2026-05-03`

## Executive Verdict
The full Unit 1 bank is **not ready for student release**.

That is not because every topic is bad. In fact, several topics are already quite promising on raw factual quality. The problem is that the bank still has a mixture of:
- topic-specific factual/editorial defects,
- repeated transformation weaknesses,
- repeated self-marking contract problems, and
- unresolved runtime/pipeline blockers.

The strongest current conclusion is:

> The main risk is no longer “we do not have enough questions”.
> The main risk is “students could be taught, marked, or guided unreliably by questions that look finished but are not yet trustworthy enough.”

## Full Topic Coverage Status
All 12 Unit 1 topics have now been audited:
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

## Repeated Defect Patterns

### 1. True/False items misclassified as `match_table`
This is the single most widespread topic-level structural defect.

Confirmed in at least these 10 topics:
- Spreadsheet applications
- Digital data
- Software
- Computer hardware
- Cyberspace, network security and data transfer
- Cloud technology
- Ethical, legal and environmental impact
- Changes in employment opportunities, skills requirements and work practices
- Health and safety
- Digital applications

Impact:
- wrong runtime shape
- avoidable scorer/renderer ambiguity
- unnecessary complexity in a question type that should be simple and reliable

Priority:
- **must fix before student release**

### 2. Short-answer / fill-gap / list-style answers are not yet safely auto-markable
This is the next most serious repeated defect.

Observed across most of the bank, including:
- Database applications
- Spreadsheet applications
- Digital data
- Software
- Computer hardware
- Cyberspace, network security and data transfer
- Cloud technology
- Ethical, legal and environmental impact
- Changes in employment opportunities, skills requirements and work practices
- Health and safety
- Digital applications

Typical problem patterns:
- `Any 2 from` / `Any 3 from` prose
- `accept:` alternatives embedded in text
- long raw-answer strings
- valid multiple phrasings not formalized in marking rules

Impact:
- unfair student marking
- unreliable progress data
- weak adaptive guidance built on noisy scores

Priority:
- **must fix before student release**

### 3. Transformed exam items often flatten richer exam demand into recognition tasks
This is one of the largest assessment-quality risks.

It appears strongly in:
- Cloud technology
- Cyberspace, network security and data transfer
- Ethical, legal and environmental impact
- Changes in employment opportunities, skills requirements and work practices
- Health and safety
- Digital applications
- plus smaller but still important cases in Software, Spreadsheet Applications, Database Applications, and Computer Hardware

Typical transformation problem:
- a `list`, `state two`, or `discuss` source item is turned into one or more 1-mark recognition MCQs

Impact:
- weakens revision depth
- reduces the need for recall and explanation
- can distort the feel of the exam even when factually correct

Priority:
- **must fix before release for the highest-volume transformed topics**
- lower-volume cases can be handled during topic cleanup

### 4. Student explanations are missing everywhere
All staged topics still carry `needs_explanation_enrichment`.

Impact:
- poor revision experience
- weak learning feedback
- overstates readiness in the review gate

Priority:
- **must fix before student release**

### 5. Source/provenance blur exists in some later topics
Most clearly seen in:
- Cyberspace, network security and data transfer
- Cloud technology

Pattern:
- supplementary mark-scheme spin-offs are mixed into the `past_paper` stream as if they were direct question-paper imports

Impact:
- weakens teacher trust
- makes review/audit provenance less clear

Priority:
- **must fix before release**

### 6. Family grouping is still too coarse in some topics
Most clearly seen in:
- Digital data

Impact:
- distinct questions could later be suppressed as near-duplicates
- hurts coverage if session selection starts using these families naively

Priority:
- **must fix before intelligent adaptive session picking is enabled**

## Topic Strength Bands
These are relative bands, not absolute release decisions. No topic is currently student-ready.

### Band A: Strongest raw content foundations
These topics currently look strongest on factual reliability, even though they still have structural/runtime blockers.

#### 1. Health and safety
Strengths:
- raw source is comparatively stable
- no major factual howler found
- concept set is coherent

Weaknesses still blocking release:
- transformed micro-item overuse
- true/false misclassification
- unsafe list-style marking

#### 2. Digital applications
Strengths:
- broad and useful coverage
- strong factual base overall
- one known practice-source bug appears to have been repaired in staging

Weaknesses still blocking release:
- too many recognition-style MCQs for evaluative content
- true/false misclassification
- unsafe structured/list marking

#### 3. Cloud technology
Strengths:
- comparatively clean source quality
- QA evidence is reassuring

Weaknesses still blocking release:
- over-flattened transformed advantages/disadvantages items
- provenance blur with supplementary items
- one risky cloud-gaming statement

### Band B: Mixed / moderate-risk topics
These topics are workable, but need meaningful cleanup before we could trust them.

#### 4. Changes in employment opportunities, skills requirements and work practices
Strengths:
- raw source is broadly sound
- no objective mapping gaps

Weaknesses:
- topic is unusually thin
- over-reliance on transformed items because of that thinness
- open/list-style answers still unsafe

#### 5. Cyberspace, network security and data transfer
Strengths:
- terminology is broadly sound
- no major raw terminology collapse

Weaknesses:
- heavy transformation load
- provenance blur
- brittle named-example question
- unsafe short/fill/list marking

#### 6. Spreadsheet applications
Strengths:
- source quality better than some earlier topics
- good asset support

Weaknesses:
- true/false misclassification
- formula/list/range answers not safely markable
- transformation and scoring structure still weak

#### 7. Digital data
Strengths:
- broad raw concept coverage
- no major factual collapse found

Weaknesses:
- family-grouping heuristic is too broad
- true/false misclassification
- ambiguous short-answer handling

### Band C: Highest-risk topics
These are the topics where I would be least comfortable trusting the bank without significant correction.

#### 8. Network technologies
Why high-risk:
- confirmed switch/router answer-key issue
- repeated conceptual device-role confusion
- many transformed items still not structurally safe

#### 9. Computer hardware
Why high-risk:
- fetch-execute/register content is conceptually unreliable
- possible MAR/MDR/IAS teaching damage
- shared source file with Network Technologies increases risk concentration

#### 10. Database applications
Why high-risk:
- at least one impossible prompt
- accepted alternatives trapped in prose
- fairness risk is high even where raw facts are sound

#### 11. Ethical, legal and environmental impact
Why high-risk:
- GPS-process question is unsafe after normalization
- transformed material can look cleaner than it really is
- brittle fact-file-specific practice prompts remain

#### 12. Software
Why high-risk:
- some transformed items are pedagogically weak
- one practice-bank RAM/ROM prompt is technically careless
- lower trust in source-normalization layer than Band A/B topics

## What Must Be Fixed Before Any Student Release
These are release blockers.

### Platform / pipeline blockers
1. Build the staging-to-live transformation layer.
2. Move correctness and score authority to the server side.
3. Tighten the review gate so missing explanations do not still count as `ready_for_review`.
4. Normalize true/false into its own format.
5. Build proper accepted-answer rules for fill-gap, short-text, and list-style questions.
6. Tighten family-code generation before session selection starts using it heavily.
7. Separate direct PPQ-derived items from supplementary mark-scheme spin-offs in metadata and review flow.

### Content blockers
1. Correct confirmed factual/source-risk items in high-risk topics:
   - Network switch/router items
   - Computer hardware CPU/register items
   - Ethical/legal GPS-process item
   - Cloud gaming file-streaming statement
   - Software RAM/ROM wording issue
   - Database impossible prompt
2. Review high-volume transformed-item topics for lost exam demand.
3. Add student-facing explanations across the bank.

## What Can Wait Until Later Refinement
These are important, but they do not need to block the next corrective phase.

1. Fine-tuning `selection_weight`
2. Full adaptive session intelligence
3. Final student stats redesign
4. Advanced owner-only import UX polish
5. Any non-essential visual/admin polish

## Recommended Remediation Order
If we want the safest path forward, the order should be:

1. **Runtime contract fix**
   - staging-to-live transformation
   - server-side score authority

2. **Question-type normalization**
   - true/false format
   - structured autograde rules for fill-gap / short / list

3. **High-risk content correction**
   - Network, Computer Hardware, Database, Ethical/Legal, Software first

4. **Transformed-item tightening**
   - especially Cloud, Cyberspace, Topic 10, Health and Safety, Digital Applications

5. **Explanation enrichment**
   - once the above structure is trustworthy

6. **Adaptive/session/statistics rebuild**
   - only after the question bank is reliable enough to deserve it

## Final Recommendation
Do **not** move into student-facing promotion, explanation enrichment, or adaptive-behaviour tuning yet as if the question bank were already trustworthy.

The right next step is not “more questions” or “more polish”.
The right next step is to fix the content/runtime trust boundary first.

If we do that well, the existing bank becomes a strong foundation.
If we skip it, the app risks giving students confident but unreliable revision.
