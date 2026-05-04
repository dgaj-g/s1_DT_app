# Stage 4 Focused Re-Audit: Cloud and Ethical/Legal Brittle Prompt Corrections (2026-05-04)

## Scope

This re-audit revisits two narrow editorial defect groups:

- `CL-003`
- `EL-003`

The goal was to confirm that the revised practice-bank prompts now test stable,
exam-relevant concepts instead of brittle or time-sensitive detail, and that the
staged payload reflects those source corrections cleanly.

## Source files reviewed

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_07_08_cyberspace_cloud.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`

## Regenerated outputs reviewed

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

## Items re-audited

### Cloud technology
- `cloud-technology.practice_bank.topic_07_08_cyberspace_cloud.q010`

### Ethical, legal and environmental impact
- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q008`
- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q015`

## Findings

### 1. [Closed] The cloud-gaming statement now tests the right delivery model.

Before:
- the prompt claimed that file-streaming cloud gaming requires a computer with
  enough power to execute the game locally

After:
- `In file streaming cloud gaming, the game is processed on a remote server and the output is streamed to the user's device.`

Answer:
- `True`

Verdict:
- this now tests the core concept safely and directly
- the earlier factual-risk concern in `CL-003` is no longer justified

### 2. [Closed] The GPS/social-media MCQ is now a stable privacy-risk question.

Before:
- the question depended on brittle fact-file-specific/trivia-like detail

After:
- `Why should users be cautious about sharing their GPS location on social media?`

Answer:
- `B. It can reveal where someone is and create a privacy or safety risk`

Verdict:
- this is a much stronger revision question
- it now tests a durable ethical/privacy concept rather than weak source-specific recall

### 3. [Closed] The social-media privacy-settings item is now stable and concept-led.

Before:
- the question depended on a time-sensitive claim about a specific platform's
  default settings

After:
- `True or False: Social media privacy settings should be checked regularly because default sharing settings can change over time.`

Answer:
- `True`

Verdict:
- this is now stable, concept-driven, and suitable for a high-trust revision bank

### 4. Objective mapping is now cleaner for the corrected Ethical/Legal items.

While verifying the corrected stems, a secondary issue appeared:
- generic `Sources:` metadata was polluting Topic 9 objective inference and
  dragging some GPS/privacy prompts into the copyright objective

The mapper was then tightened so that:
- Topic 9 GPS/privacy questions do not keep a spurious copyright objective when
  the actual question text is clearly about privacy or social-media risk

Verified staged results:
- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q008`
  now maps to:
  - `ethical-legal-and-environmental-impact.internet-misuse-and-ethics`
- `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q015`
  now maps to:
  - `ethical-legal-and-environmental-impact.internet-misuse-and-ethics`

This does not make them student-ready, but it does remove a misleading adaptive/statistics signal.

### 5. These items remain draft for the expected reasons, not content-trust reasons.

All three corrected items still carry:
- `needs_explanation_enrichment`
- `practice_question_needs_source_normalization`

That is appropriate.

They are no longer being held back because the source-content itself is unsafe.

## Conclusion

I am comfortable closing:

- `CL-003`
- `EL-003`

The re-audit evidence supports that:
- the source wording has been corrected
- the staged payload reflects the corrected stems
- the remaining blockers are structural/editorial follow-up items, not the original content-trust defects
