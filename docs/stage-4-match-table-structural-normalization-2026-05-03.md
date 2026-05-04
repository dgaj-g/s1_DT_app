# Stage 4 Cross-Topic Re-Audit: Match-Table Structural Normalization (2026-05-03)

## Scope
This re-audit checks whether the repeated cross-topic defect of sensible match-style questions being staged without a usable structured rows/choices/pairs payload has now been partially resolved.

This is a structural normalization pass, not a source rewrite.

## Inputs Reviewed

### Scripts changed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

### Regenerated outputs reviewed
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_import_bundle.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`
- `/private/tmp/unit1_phase1_live_payload_post_match_norm.json`

## Structural change applied

In:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`

match-style items are now normalized into explicit structures when enough information can be recovered safely from the staged prompt and answer text.

The builder now attempts to construct:

- `options_json.rows`
- `options_json.choices`
- `correct_answer_json.pairs`

from patterns such as:
- list-block rows with `1 → A` style answers
- `Terms:` lines plus verbose `left → right` answer mappings
- `either Bitmap (B) or Vector (V)` style binary-choice match prompts

The Phase 1 bridge in:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_phase1_live_payload.py`

now prefers these structured match payloads directly before falling back to older text-parsing behaviour.

## Verified outcomes

### 1. A substantial portion of match-table items now carry real structure.
After the full match-table pass and its follow-on cleanup rebuilds:

- `structured_match_table_questions`
  - `71`

These questions now carry explicit rows, choices, and normalized answer pairs in the staged bundle.

### 2. Structural normalization noise dropped further across the bank.
After the same follow-on rebuild sequence:

- `needs_structured_answer_normalization`
  - from `72`
  - to `12`

That is a material reduction in unresolved structural blocker count.

### 3. Representative audited items now stage in a trustworthy match-table shape.
Verified examples:

- `digital-data.past_paper.topics_01_02.q006`
- `database-applications.past_paper.topics_03_04.q007`
- `database-applications.past_paper.topics_03_04.q027`
- `database-applications.past_paper.topics_03_04.q029`
- `database-applications.past_paper.topics_03_04.q035`
- `network-technologies.past_paper.topics_05_06.q014`
- `digital-data.practice_bank.topic_01_digital_data.q039`

These now expose:
- explicit row labels
- explicit choice labels
- explicit row-to-choice answer pairs

instead of relying only on raw prose or compact arrow strings.

### 4. The Phase 1 promotion bridge now accepts the structured match shape.
A verification run against:

- `/private/tmp/unit1_phase1_live_payload_post_match_norm.json`

showed no match-table-specific rejection reasons.

In particular, there were no remaining bridge rejections such as:
- inability to build a match-table schema
- match-table rows/choices parsing failure
- any fallback-only match-table failure mode

## Important boundary
This pass does **not** mean all match-style questions are fully promotion-ready.

Remaining blockers still include:
- `needs_explanation_enrichment`
- `needs_autograde_rule_review`
- topic-specific open content/editorial defects
- the still-open list-style / `Any X from` normalization family

At this point, there is no remaining match-table parser residue driving the
structural count. The residual `12` unresolved items are genuine multi-answer
open-response questions rather than hidden match-table extraction failures.

It also does **not** normalize every match-style question in the bank. Only the cases with enough safe recoverable structure are promoted into the richer staged shape.

## Conclusion
This re-audit supports treating the match-table structural layer as materially improved.

The bank still has major work left, but a large family of legitimate match questions is no longer being held back purely because the staged payload lacked explicit rows/choices/pairs structure.
