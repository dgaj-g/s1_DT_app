# Stage 4 Content Defect Register (2026-05-03)

This register tracks confirmed or strongly evidenced content-quality problems found during topic-by-topic auditing. It is intentionally short and only records defects that merit follow-up, not every review flag.

## Network Technologies

### NT-001 — Practice-bank switch/router answer appeared wrong
- Topic: `Network technologies`
- Source: `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`
- Imported item: `network-technologies.practice_bank.topic_05_06_hardware_networks.q005`
- Issue: prompt describes a `sophisticated switched hub` that forwards data efficiently, but stored answer is `Router`
- Impact: teaches the wrong network device concept
- Status: closed after focused re-audit on 2026-05-03; source wording now matches router/gateway concept

### NT-002 — Practice-bank matching definition mixed switch/router language
- Topic: `Network technologies`
- Source: `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`
- Imported item: `network-technologies.practice_bank.topic_05_06_hardware_networks.q031`
- Issue: matching definition combines `sophisticated switched hub` language with `gateway` language
- Impact: conceptually muddy device-role teaching
- Status: closed after focused re-audit on 2026-05-03; source wording now separates switch and router roles coherently

## Database Applications

### DB-001 — Imported item has impossible instructions
- Topic: `Database applications`
- Source: `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_03_04.md`
- Imported item: `database-applications.past_paper.topics_03_04.q042`
- Issue: prompt says words `RECORD; TABLE; COLUMN` are each used once, but only two blanks exist and answer only uses two terms
- Impact: student confusion and impossible self-marking
- Status: closed after focused re-audit on 2026-05-03; source wording now correctly states that not all supplied words are used

### DB-002 — Accepted alternative answers are trapped in prose, not structure
- Topic: `Database applications`
- Imported items:
  - `database-applications.past_paper.topics_03_04.q003`
  - `database-applications.past_paper.topics_03_04.q045`
  - `database-applications.past_paper.topics_03_04.q046`
- Issue: valid alternatives are still embedded in raw answer text using `accept:` notes
- Impact: likely unfair marking if promoted without enrichment
- Status: closed after structural re-audit on 2026-05-03; accepted alternatives are now carried in explicit `accepted_texts` structures instead of being trapped in prose

## Spreadsheet Applications

### SS-001 — True/False practice items are misclassified as `match_table`
- Topic: `Spreadsheet applications`
- Imported items:
  - `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q029`
  - `q030`
  - `q031`
  - `q032`
  - `q033`
- Issue: single-statement true/false prompts are staged as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### SS-002 — Formula/range/list short answers are not yet safely auto-markable
- Topic: `Spreadsheet applications`
- Imported items include:
  - `spreadsheet-applications.practice_bank.topic_04_spreadsheet.q039`
  - `q040`
  - `q041`
  - `q042`
  - `q043`
  - `q045`
  - `q046`
  - `spreadsheet-applications.past_paper.topics_03_04.q054`
- Issue: raw answers still stored as exact strings or `Any X from` prose rather than structured accepted-answer rules
- Impact: high risk of unfair student marking
- Status: closed after focused structural re-audit on 2026-05-04; the list-style items now use explicit shared-pool fill-gap structures and the remaining spreadsheet short answers promote cleanly as canonical exact-term responses in a controlled bridge dry run

## Cross-cutting Pipeline Defects

### PIPE-001 — Converted exam items are under-reported by transformed-item detection
- Affects at least:
  - `Database applications`
  - `Spreadsheet applications`
- Issue: many source locators say `converted from ...`, but current transformed-item detection misses them
- Impact: high-risk rewritten items are not being surfaced honestly in review summaries
- Status: confirmed pipeline defect

### PIPE-002 — Missing explanations do not block `ready_for_review`
- Affects all topics currently staged
- Issue: every question can still be `ready_for_review` while carrying `needs_explanation_enrichment`
- Impact: review gate overstates readiness
- Status: confirmed pipeline defect

## Digital Data

### DD-001 — Digital Data family grouping is too broad for safe duplicate suppression
- Topic: `Digital data`
- Example families:
  - `digital-data.graphics.choose`
  - `digital-data.data-measurement.choose`
- Issue: distinct concepts are being grouped as if they were near-duplicates
- Impact: later session selection could suppress valid revision coverage
- Status: confirmed pipeline/content-model defect

### DD-002 — Single-statement True/False items are staged as `match_table`
- Topic: `Digital data`
- Imported items include:
  - `digital-data.past_paper.topics_01_02.q042`
  - `digital-data.practice_bank.topic_01_digital_data.q008`
  - `q031`
  - `q037`
  - `q045`
  - `q056`
  - `q100`
- Issue: binary judgment prompts are being represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### DD-003 — Some short-answer prompts are too ambiguous or rely on prose-only accepted answers
- Topic: `Digital data`
- Imported items include:
  - `digital-data.practice_bank.topic_01_digital_data.q021`
  - `q033`
  - `q040`
  - `q044`
  - `digital-data.past_paper.topics_01_02.q047`
- Issue: accepted answers are stored as raw strings with multiple alternatives or `Any X from` prose
- Impact: likely unfair or inconsistent auto-marking if promoted unchanged
- Status: closed after focused structural/source re-audit on 2026-05-04; `q021` source wording now makes `Megabyte (MB)` the single intended unit and the remaining items now stage with explicit accepted-answer structures or grouped alternatives

## Software

### SW-001 — Some transformed past-paper items are weakened into low-value match questions
- Topic: `Software`
- Imported items:
  - `software.past_paper.topics_01_02.q001`
  - `software.past_paper.topics_01_02.q009`
- Issue: original `list two resources managed by the OS` prompts were transformed into match questions where both examples map to the same bucket
- Impact: weaker revision value and poorer fidelity to source demand
- Status: closed after focused re-audit on 2026-05-04; the two items were rewritten as faithful short/list prompts and now stage as distinct-answer fill-gap questions that promote cleanly in a controlled dry run

### SW-002 — Transformed utility-program item broadens beyond original source demand
- Topic: `Software`
- Imported item: `software.past_paper.topics_01_02.q008`
- Issue: source was `List two utility programs`; staged version becomes a 3-way utility-purpose match question
- Impact: expands content beyond a simple faithful adaptation of the source item
- Status: closed after focused re-audit on 2026-05-04; the source item now stages as a faithful `List TWO utility programs` shared-pool fill-gap question and promotes cleanly in a controlled dry run

### SW-003 — Single-statement True/False items are staged as `match_table`
- Topic: `Software`
- Imported items include:
  - `software.practice_bank.topic_02_03_software_database.q022`
  - `q023`
  - `q024`
  - `q025`
- Issue: binary judgment prompts are represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### SW-004 — Practice-bank RAM/ROM prompt is technically careless
- Topic: `Software`
- Imported item: `software.practice_bank.topic_02_03_software_database.q026`
- Issue: asks for `the two microchips that make up the main memory in a computer's CPU`
- Impact: risks teaching an inaccurate relationship between RAM/ROM and the CPU
- Status: closed after focused re-audit on 2026-05-03; source wording now refers safely to the two main types of primary memory

## Computer Hardware

### HW-001 — Practice-bank fetch-execute/register content was conceptually unreliable
- Topic: `Computer hardware`
- Imported items:
  - `computer-hardware.practice_bank.topic_05_06_hardware_networks.q027`
  - `computer-hardware.practice_bank.topic_05_06_hardware_networks.q028`
- Issue: wording around `Immediate Access Store`, `MAR`, and `MDR` is muddled and at least one mapping appears unsafe
- Impact: students could learn the wrong CPU/register model
- Status: closed after focused re-audit on 2026-05-03; source wording and register-role mapping are now coherent

### HW-002 — Single-statement True/False items are staged as `match_table`
- Topic: `Computer hardware`
- Imported items:
  - `computer-hardware.practice_bank.topic_05_06_hardware_networks.q021`
  - `q022`
  - `q023`
  - `q024`
- Issue: binary judgment prompts are represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### HW-003 — Hardware practice-bank wording needs normalization in several prompts
- Topic: `Computer hardware`
- Imported items include:
  - `computer-hardware.practice_bank.topic_05_06_hardware_networks.q025`
  - `q032`
- Issue: awkward or loose wording plus raw alternative-answer strings
- Impact: poorer student experience and unreliable self-marking
- Status: closed as a source-content defect after boundary re-audit on 2026-05-03; remaining concerns for `q032` belong to structural answer normalization rather than source trust

## Cyberspace, Network Security and Data Transfer

### CY-001 — Supplementary mark-scheme spin-off items are mixed into the past-paper stream
- Topic: `Cyberspace, network security and data transfer`
- Imported items:
  - `cyberspace-network-security-and-data-transfer.mark_scheme.topics_07_08_09.q047`
  - `cyberspace-network-security-and-data-transfer.mark_scheme.topics_07_08_09.q048`
- Issue: these are explicitly derived from mark-scheme content rather than direct source questions, but sit in the same `past_paper` namespace
- Impact: provenance becomes blurred and teacher review becomes less trustworthy
- Status: closed after focused provenance re-audit on 2026-05-04; supplementary items now stage in the `mark_scheme` namespace instead of `past_paper`

### CY-002 — Single-statement True/False items are staged as `match_table`
- Topic: `Cyberspace, network security and data transfer`
- Imported items include:
  - `cyberspace-network-security-and-data-transfer.past_paper.topics_07_08_09.q047`
  - `q048`
  - `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q017`
  - `q018`
  - `q019`
  - `q036`
- Issue: binary judgment prompts are represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### CY-003 — Named-example whistleblowing question is too brittle for trusted revision use
- Topic: `Cyberspace, network security and data transfer`
- Imported item: `cyberspace-network-security-and-data-transfer.practice_bank.topic_07_08_cyberspace_cloud.q023`
- Issue: relies on a specific named website example (`Wikileaks`) and uses loaded wording (`sharing stolen data`)
- Impact: weakens trust and creates editorial fragility without improving syllabus coverage
- Status: closed after focused re-audit on 2026-05-03; source wording now tests the concept of whistleblowing directly and objective mapping has been realigned to `cybercrime`

## Cloud Technology

### CL-001 — Supplementary mark-scheme spin-off items are mixed into the past-paper stream
- Topic: `Cloud technology`
- Imported items:
  - `cloud-technology.mark_scheme.topics_07_08_09.q020`
  - `cloud-technology.mark_scheme.topics_07_08_09.q021`
- Issue: these are explicitly derived from mark-scheme content rather than direct source questions, but sit in the same `past_paper` namespace
- Impact: provenance becomes blurred and teacher review becomes less trustworthy
- Status: closed after focused provenance re-audit on 2026-05-04; supplementary items now stage in the `mark_scheme` namespace instead of `past_paper`

### CL-002 — Single-statement True/False items are staged as `match_table`
- Topic: `Cloud technology`
- Imported items:
  - `cloud-technology.past_paper.topics_07_08_09.q020`
  - `q021`
  - `cloud-technology.practice_bank.topic_07_08_cyberspace_cloud.q010`
  - `q011`
- Issue: binary judgment prompts are represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### CL-003 — File-streaming cloud-gaming practice statement is factually risky
- Topic: `Cloud technology`
- Imported item: `cloud-technology.practice_bank.topic_07_08_cyberspace_cloud.q010`
- Issue: states that file-streaming cloud gaming requires a computer with sufficient power/specification to execute the game, which is risky as phrased
- Impact: could teach the wrong model of cloud-gaming delivery
- Status: closed after focused re-audit on 2026-05-04; source wording now tests the correct file-streaming delivery model directly

## Ethical, Legal and Environmental Impact

### EL-001 — GPS process practice item is unsafe after normalization
- Topic: `Ethical, legal and environmental impact`
- Source: `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_09_12_wider_impact.md`
- Imported item: `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q006`
- Issue: source QA flagged a broken distractor; staged version replaces it with `Trilateration` but still keeps `Triangulation` as the correct answer
- Impact: leaves two technically plausible answers in the same MCQ and undermines student trust
- Status: closed after focused re-audit on 2026-05-03; source distractor now uses `Geocoding`, preserving a single safe intended answer

### EL-002 — Single-statement True/False items are staged as `match_table`
- Topic: `Ethical, legal and environmental impact`
- Imported items include:
  - `ethical-legal-and-environmental-impact.past_paper.topics_07_08_09.q033`
  - `q034`
  - `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q013`
  - `q014`
  - `q015`
- Issue: binary judgment prompts are represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### EL-003 — Some practice-bank prompts are too brittle for a high-trust revision bank
- Topic: `Ethical, legal and environmental impact`
- Imported items include:
  - `ethical-legal-and-environmental-impact.practice_bank.topic_09_12_wider_impact.q008`
  - `q015`
- Issue: prompts rely on fact-file-specific or time-sensitive detail rather than strong exam-style concept revision
- Impact: weakens revision quality even when not strictly factually wrong
- Status: closed after focused re-audit on 2026-05-04; the revised prompts now test stable privacy/safety concepts rather than brittle source-specific detail

## Changes in Employment Opportunities, Skills Requirements and Work Practices

### EMP-001 — Single-statement True/False items are staged as `match_table`
- Topic: `Changes in employment opportunities, skills requirements and work practices`
- Imported items include:
  - `changes-in-employment-opportunities-skills-requirements-and-work-practices.practice_bank.topic_09_12_wider_impact.q010`
  - `q011`
  - `q012`
  - `q013`
- Issue: binary judgment prompts are represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### EMP-002 — Open and list-style employment-change questions are not yet safely auto-markable
- Topic: `Changes in employment opportunities, skills requirements and work practices`
- Imported items include:
  - `changes-in-employment-opportunities-skills-requirements-and-work-practices.practice_bank.topic_09_12_wider_impact.q014`
  - `q015`
  - `q016`
  - `q017`
  - `changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q007`
- Issue: accepted answers still rely on raw strings, `accept:` prose, or `Any THREE of` list logic
- Impact: high risk of unfair or inconsistent self-marking if promoted unchanged
- Status: closed after focused structural re-audit on 2026-05-04; the set now stages as ordered gaps, grouped single-answer alternatives, or shared fill-gap pools, and a controlled promotion dry run succeeded without structural rejection reasons

### EMP-003 — Topic 10 is unusually thin and therefore overly dependent on transformed items
- Topic: `Changes in employment opportunities, skills requirements and work practices`
- Imported items include:
  - `changes-in-employment-opportunities-skills-requirements-and-work-practices.past_paper.topics_10_11_12.q001`
  - `q002`
  - `q004`
  - `q005`
  - `q006`
- `q007`
- Issue: the QA report already notes that Topic 10 has genuinely thin source coverage, and the staged bank relies heavily on transformed teleworking/employment-impact items to fill it out
- Impact: if these transformations are weak, students have too little alternative coverage inside the topic to compensate
- Status: closed after focused transformation re-audit on 2026-05-04; the weakest recognition-style MCQs were rebuilt into short-answer/fill-gap recall items, the staged forms now carry explicit accepted-answer structures, and a controlled promotion dry run on the exact transformed past-paper family (`6/6` promoted, `0` rejected) confirmed that the remaining risk is topic breadth rather than an open item-level content defect

## Health and Safety

### HS-001 — Single-statement True/False items are staged as `match_table`
- Topic: `Health and safety`
- Imported items include:
  - `health-and-safety.practice_bank.topic_09_12_wider_impact.q011`
  - `q012`
  - `q013`
  - `q014`
- Issue: binary judgment prompts are represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### HS-002 — List-style and structured-response health-and-safety items are not yet safely auto-markable
- Topic: `Health and safety`
- Imported items include:
  - `health-and-safety.practice_bank.topic_09_12_wider_impact.q015`
  - `q016`
  - `q017`
- Issue: accepted answers still rely on raw strings or `Any THREE of` prose rather than structured accepted-answer rules
- Impact: high risk of unfair or inconsistent self-marking if promoted unchanged
- Status: closed after grouped-alias structural re-audit on 2026-05-04; the topic now uses explicit ordered gaps or grouped fill-gap acceptance, including safe alias handling for `RSI` / `Repetitive Strain Injury`

## Digital Applications

### DA-001 — Single-statement True/False items are staged as `match_table`
- Topic: `Digital applications`
- Imported items include:
  - `digital-applications.practice_bank.topic_09_12_wider_impact.q026`
  - `q027`
  - `q028`
  - `q029`
- Issue: binary judgment prompts are represented as match-table items
- Impact: unnecessary renderer/scorer ambiguity
- Status: closed after cross-topic structural re-audit on 2026-05-03; eligible single-statement items now stage as `true_false` instead of `match_table`

### DA-002 — Digital Applications structured/list items are not yet safely auto-markable
- Topic: `Digital applications`
- Imported items include:
  - `digital-applications.practice_bank.topic_09_12_wider_impact.q030`
  - `q032`
  - `q033`
- Issue: accepted answers still rely on raw strings or long list-style prose rather than structured accepted-answer rules
- Impact: high risk of unfair or inconsistent self-marking if promoted unchanged
- Status: closed after grouped-alias structural re-audit on 2026-05-04; ordered-gap and shared-pool fill-gap structures now carry the accepted concepts explicitly, including label-plus-explanation answer groups for online-training advantages

### DA-003 — Digital Applications relies heavily on recognition-style transformed pros/cons items
- Topic: `Digital applications`
- Imported items include:
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
- Issue: richer evaluative source material about online training, shopping and banking is frequently flattened into one-mark recognition MCQs
- Impact: weakens revision depth even where factual content is broadly sound
- Status: closed after focused transformation re-audit on 2026-05-04; the transformed online-training, shopping, gaming and banking prompts were rebuilt into short-answer recall items with explicit accepted-answer structures, and a controlled promotion dry run on the exact transformed past-paper family (`12/12` promoted, `0` rejected) confirmed that the remaining work is structural/pedagogical rather than an open item-level content defect
