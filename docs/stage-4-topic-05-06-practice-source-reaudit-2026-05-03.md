# Stage 4 Focused Re-Audit: Topic 5/6 Practice Source Corrections (2026-05-03)

## Scope
This re-audit checks the first direct source-correction pass applied to:

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

The aim is narrow and deliberate:

1. verify that the patched source wording and answer keys now make conceptual sense;
2. verify that the regenerated staged/import bundle reflects those source changes; and
3. decide which defect-register entries can honestly move from `patched` to `closed`.

This is **not** a full re-audit of all Topic 5/6 content. It only addresses the corrected high-risk items and the immediate neighboring cleanup in the same source family.

## Inputs Reviewed

### Source file
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_practice_questions/topic_05_06_hardware_networks.md`

### Supporting context
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_automark/markdown/topics_05_06.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_extraction/2022.md`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/_qa/qa_topics_5_6.md`

### Regenerated outputs reviewed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`

## Corrected Items Reviewed

### Computer hardware
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q005`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q007`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q025`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q027`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q028`

### Network technologies
- `network-technologies.practice_bank.topic_05_06_hardware_networks.q005`
- `network-technologies.practice_bank.topic_05_06_hardware_networks.q031`

## Findings

### 1. [Closed] The network switch/router source defect has been corrected cleanly.
The earlier problem was that the source described a switch-like device but marked `Router` as correct.

The patched source now reads:
- `Which network resource is often used as a gateway to connect a LAN to a larger network such as the internet?`
- answer: `Router`

That is conceptually coherent and aligns with the rest of the topic material.

Affected imported item:
- `network-technologies.practice_bank.topic_05_06_hardware_networks.q005`

Verdict:
- the underlying content defect identified as `NT-001` is now fixed at source-content level

### 2. [Closed] The network matching definition no longer mixes switch/router roles.
The earlier issue was that the router definition borrowed switch language (`sophisticated switched hub`) and mixed it with gateway language.

The patched definition now reads:
- `Connects a LAN to a larger network such as the internet and is often used as a gateway`

with:
- `NIC → 2`
- `Switch → 3`
- `Router → 1`

Affected imported item:
- `network-technologies.practice_bank.topic_05_06_hardware_networks.q031`

Verdict:
- the conceptual defect identified as `NT-002` is now fixed at source-content level

### 3. [Closed] The unreliable hardware fetch-execute/register source cluster has been materially corrected.
The strongest earlier defects were:
- a muddled IAS prompt
- an unsafe MAR/MDR/Program Counter mapping

The patched source now gives:

#### `q027`
- `Name the CPU component that temporarily stores programs and data while they are being used in the fetch-execute cycle.`
- answer: `Immediate Access Store`

This now aligns with the broader Topic 5 source material, especially the 2022 CPU-component explanatory content.

#### `q028`
- `Program Counter → 2`
- `MAR → 3`
- `MDR → 4`
- `ALU → 1`

with definitions:
- `2. Holds the address of the next instruction to be fetched`
- `3. Stores the memory address of the data or instruction to be accessed`
- `4. Temporarily holds the data or instruction fetched from memory`

This is coherent and no longer contains the unsafe `MAR → stores current instruction/data being executed` mapping that triggered the original defect.

Affected imported items:
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q027`
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q028`

Verdict:
- the source-content defect identified as `HW-001` is now fixed at source-content level

### 4. [Improved, not part of original closure set] Two nearby hardware MCQs are now safer and clearer.
These were not the main named defects, but they were weak enough to merit correction while the source file was open.

#### `q005`
Now asks:
- `What does the Program Counter hold?`
- correct answer:
  - `The address of the next instruction to be fetched`

This is stronger than the previous wording.

#### `q007`
Now asks:
- `Which register stores the memory address of the data or instruction to be accessed?`
- correct answer:
  - `Memory Address Register`

This is materially safer than the previous source wording.

Verdict:
- worthwhile cleanup
- not a separate defect-register closure item, but a good supporting improvement

### 5. [Still open] `HW-003` is only partially improved.
`computer-hardware.practice_bank.topic_05_06_hardware_networks.q025` is now better:
- `The ALU is a vital part of the ____________-____________ cycle.`

That removes the awkward `part and end of` wording.

However:
- `computer-hardware.practice_bank.topic_05_06_hardware_networks.q032` is still unresolved at source-quality level
- both items still rely on runtime-side answer normalization before student use

Verdict:
- `HW-003` should remain open as a partial fix

### 6. The corrected items still remain blocked from student release, but for the right reasons now.
After regeneration, the corrected questions are still staged as `draft`.

That is correct.

They are no longer being blocked because the source wording is conceptually wrong.
They are still blocked because:
- explanations are missing;
- some use runtime shapes that still need normalization;
- some still need better self-marking structure.

This is an important distinction:
- source-content defect fixed
- runtime/promotion readiness still pending

## Overall Verdict
This first correction pass was successful.

I am comfortable saying:
- `NT-001` is fixed at source-content level
- `NT-002` is fixed at source-content level
- `HW-001` is fixed at source-content level

I am **not** comfortable saying:
- Topic 5/6 practice-bank items are fully ready for student use
- runtime normalization concerns are resolved
- `HW-003` is fully closed

## Recommended Register Actions
1. Move `NT-001` to closed
2. Move `NT-002` to closed
3. Move `HW-001` to closed
4. Leave `HW-003` open as partial

## Recommended Next Move
The next sensible corrective step is:

1. remove the now-closed source defects from the `known_content_defect` blocker path; and
2. continue with question-type/runtime normalization so these corrected items can eventually move beyond `draft` for the right reasons.
