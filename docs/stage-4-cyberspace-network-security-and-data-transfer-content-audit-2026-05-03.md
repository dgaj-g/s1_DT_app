# Stage 4 Content Audit: Cyberspace, Network Security and Data Transfer (2026-05-03)

## Scope
This audit checks the `Cyberspace, network security and data transfer` topic in the staged Stage 4 payload against the curated source materials. The aim is to determine whether the imported questions are factually trustworthy, faithful to source intent, and safe for auto-marked revision.

## Source Material Reviewed
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_07_08_09.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_07_08_cyberspace_cloud.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_7_12.md`

## Generated Payload Reviewed
- `/private/tmp/unit1_stage4_import_bundle.json`
- `/private/tmp/unit1_stage4_staging_payload.json`

## Topic Snapshot
- Total staged cyberspace questions: `88`
- Prompt assets linked: `0`
- Unresolved prompt assets: `0`
- Current staged formats:
  - `61` MCQ
  - `16` match_table
  - `8` fill_gap
  - `3` structured_response
- Current review flags:
  - `needs_explanation_enrichment`: `88`
  - `practice_question_needs_source_normalization`: `40`
  - `transformed_exam_item`: `32`
  - `needs_autograde_rule_review`: `11`
  - `needs_objective_mapping`: `5`

## Findings

### 1. [High] This topic is heavily dependent on transformed exam items, and some of those transformations flatten high-value security reasoning too aggressively.
The staged cyberspace bank contains `32` items flagged `transformed_exam_item`, including:
- firewall tasks split into separate MCQs (`q005`, `q006`)
- malware behaviour simplified into single-choice items (`q008`, `q009`, `q014`)
- protocol/encryption concepts converted from short-answer or describe questions into one-line MCQs (`q019`, `q021`, `q023`, `q024`, `q025`, `q029`)
- a full `2024 Q8` 6-mark QWC-style cybercrime/phishing/DoS response split into five 1-mark MCQs (`q035` to `q039`)

Many of those transformed items are not obviously factually wrong, but they do shrink richer reasoning and explanation demands into recognition tasks. That weakens their value as revision for a real exam, especially in a topic where students need to distinguish related threats and protections clearly.

### 2. [High] Supplementary mark-scheme-derived statements are currently mixed into the past-paper namespace as if they were original exam questions.
Two staged items are explicitly labeled as supplementary derivations rather than direct past-paper questions:
- `cyberspace-network-security-and-data-transfer.past_paper.topics_07_08_09.q047`
- `cyberspace-network-security-and-data-transfer.past_paper.topics_07_08_09.q048`

These are:
- `True or False: A firewall can prevent spam and viruses from entering a network.`
- `True or False: A secure password should be a real dictionary word so it is easy for the user to remember.`

These may be useful revision checks, but they are not the same thing as an imported exam item. They should not be indistinguishable from true past-paper-derived questions in the staged bank metadata.

### 3. [High] Several single-statement True/False items are again misclassified as `match_table`.
Examples include:
- `cyberspace-network-security-and-data-transfer.past_paper.topics_07_08_09.q047`
- `cyberspace-network-security-and-data-transfer.past_paper.topics_07_08_09.q048`
- `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q017`
- `q018`
- `q019`
- `q036`

These are ordinary binary judgment items, not matching tasks. As in other topics, this is the wrong structural contract for the runtime.

### 4. [Medium] The practice-bank `Wikileaks` item is too brittle and editorially loaded for a trusted revision app.
`cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q023` asks:
- `State one example of a website that specialises in sharing stolen data (whistleblowing).`
- answer: `Wikileaks`

This is not a good style of revision prompt for this app. It relies on a specific named example rather than a stable syllabus concept, and the wording itself (`sharing stolen data`) is loaded in a way that is not ideal for a student-revision platform. Even if the source file contains it, this item should be treated as an editorial risk.

### 5. [Medium] Several security/data-transfer short-answer or structured-response items are useful in principle but still unsafe for automatic marking in their current form.
Examples include:
- `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q020`
  - `unauthorised; keylogger / key logger`
- `q037`
  - `TCP/IP (Transmission Control Protocol/Internet Protocol)`
- `q038`
  - `Any three of: passwords; levels of access; backup; firewalls`
- `cyberspace-network-security-and-data-transfer.past_paper.topics_07_08_09.q012`
  - `rules; computers`
- `q017`
  - `encode; unreadable`
- `q031`
  - `ENCRYPTION; UNREADABLE; DECODED`
- `q032`
  - `HTTPS`

These are all potentially good questions, but they still depend on raw-string or list-style marking that would be too brittle or too permissive in the live app.

### 6. [Medium] Objective mapping is still incomplete in the practice side of this topic.
The following staged items remain flagged `needs_objective_mapping`:
- `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q005`
- `q024`
- `q028`
- `q034`
- `q039`

This is not a catastrophic failure, but it would weaken adaptive guidance later if left unresolved.

### 7. [Positive] The core cybercrime/malware/protocol terminology looks broadly sound.
The supporting QA report for Topics 7–12 is reassuring here. It explicitly says the key terminology checks all pass, including:
- phishing
- cyber defamation
- spamming
- cyber stalking
- denial of service
- worm
- Trojan horse
- spyware
- key logger
- virus
- backup

That means the biggest issues in this topic are not wholesale terminology failure. They are transformation quality, structural modeling, and a few editorially weak practice prompts.

### 8. [Positive, with caution] The topic does not rely on prompt images, which simplifies delivery.
There are `0` prompt assets and `0` unresolved assets. For this topic, that appears acceptable rather than a gap.

### 9. [Medium] No cyberspace question is explanation-ready yet.
All `88` staged questions still carry `needs_explanation_enrichment`, so the feedback/teaching layer students need is still absent.

## Overall Assessment
`Cyberspace, network security and data transfer` is stronger on raw terminology than some earlier topics, but it still is not safe for student release.

The strongest issues are:
1. a very heavy dependence on transformed exam items;
2. supplementary mark-scheme-derived questions being mixed into the past-paper stream;
3. repeated true/false misclassification; and
4. several structured-response items that are still unsafe for fair auto-marking.

## Recommendation
Do not promote cyberspace questions toward live student use yet.

Before this topic can be trusted in the revision app, we should:
1. distinguish true past-paper-derived questions from supplementary mark-scheme spin-offs in metadata and review workflow;
2. normalize single true/false items into a dedicated format;
3. treat large multi-part transformations, especially 2024 Q8, with stricter editorial review; and
4. remove or rewrite brittle named-example prompts such as the `Wikileaks` item.
