# Stage 4 Focused Re-Audit: Supplementary Provenance Normalization (2026-05-04)

## Scope

This re-audit revisits the two metadata/provenance defect groups:

- `CY-001`
- `CL-001`

The issue was not factual correctness. The issue was that supplementary
mark-scheme-derived items were still living inside the `past_paper` namespace,
which made teacher review and provenance less trustworthy.

## Implementation change reviewed

The importer now normalizes any auto-mark item whose source locator contains:

- `supplementary item derived from`

from:
- `past_paper`

to:
- `mark_scheme`

Affected code:
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

## Items re-audited

### Cyberspace, network security and data transfer
- `cyberspace-network-security-and-data-transfer.mark_scheme.topics_07_08_09.q047`
- `cyberspace-network-security-and-data-transfer.mark_scheme.topics_07_08_09.q048`

### Cloud technology
- `cloud-technology.mark_scheme.topics_07_08_09.q020`
- `cloud-technology.mark_scheme.topics_07_08_09.q021`

## Findings

### 1. The supplementary items are no longer misrepresented as past-paper items.

Before:
- the four items used `past_paper` in their external IDs and source-set metadata

After:
- the four items now use `mark_scheme`

This is the correct provenance signal for review and later promotion.

### 2. Topic summaries now represent the split honestly.

After regeneration:

- `cyberspace-network-security-and-data-transfer`
  - `past_paper`: `46`
  - `mark_scheme`: `2`
- `cloud-technology`
  - `past_paper`: `19`
  - `mark_scheme`: `2`

This is a more truthful summary than the earlier all-in-one `past_paper` count.

### 3. The content still remains draft for the expected reasons.

These items still carry:
- `supplementary_derived_item`
- `needs_explanation_enrichment`
- other normal editorial follow-up flags where applicable

That is appropriate.

They are no longer being blocked because their provenance is misleading.

## Conclusion

I am comfortable closing:

- `CY-001`
- `CL-001`

The underlying content still needs normal editorial completion, but the
provenance defect itself is now fixed.
