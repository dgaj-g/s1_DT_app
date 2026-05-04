# Unit 1 Question Bank Readiness Audit

- Generated: 2026-05-04
- Source payload: `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage4_staging_payload.json`
- Total staged questions: `938`
- Linked visual assets: `29` across `29` questions

## Current Position

The staged Unit 1 bank is technically structured and reviewable, but it should not be treated as fully student-ready yet.

- All staged questions are currently `ready_for_review`, not approved/live.
- A dry-run runtime promotion has already shown that the bank can technically convert into runtime questions.
- The content still needs teacher approval, especially transformed past-paper items and practice-bank items whose source labels were normalized from the source pack.
- Difficulty depth is uneven. This is the main pedagogical blocker for a genuinely adaptive app.

## Overall Counts

| Measure | Value |
| --- | --- |
| Questions | 938 |
| Visual assets | 29 |
| Questions with visual assets | 29 |
| Status counts | {"ready_for_review": 938} |
| Difficulty counts | {"medium": 325, "expert": 169, "easy": 444} |
| Format counts | {"mcq": 611, "match_table": 97, "short_text": 74, "fill_gap": 90, "true_false": 65, "drag_drop": 1} |
| Review priority counts | {"low": 152, "high": 263, "medium": 523} |
| Review flag counts | {"transformed_exam_item": 263, "supplementary_derived_item": 40, "practice_question_needs_source_normalization": 483} |

## Topic Coverage

| Topic | Total | Easy | Medium | Expert | Asset Qs | Transformed Exam | Practice Needs Source Normalisation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Changes in employment opportunities, skills requirements and work practices | 37 | 17 | 10 | 10 | 0 | 6 | 19 |
| Cloud technology | 41 | 14 | 17 | 10 | 0 | 19 | 15 |
| Computer hardware | 80 | 30 | 30 | 20 | 5 | 29 | 32 |
| Cyberspace, network security and data transfer | 88 | 36 | 29 | 23 | 0 | 32 | 40 |
| Database applications | 120 | 61 | 48 | 11 | 5 | 39 | 64 |
| Digital applications | 55 | 32 | 13 | 10 | 0 | 12 | 35 |
| Digital data | 177 | 108 | 46 | 23 | 7 | 21 | 120 |
| Ethical, legal and environmental impact | 54 | 19 | 25 | 10 | 0 | 19 | 20 |
| Health and safety | 37 | 16 | 11 | 10 | 0 | 9 | 19 |
| Network technologies | 84 | 32 | 33 | 19 | 4 | 29 | 34 |
| Software | 58 | 33 | 14 | 11 | 0 | 7 | 35 |
| Spreadsheet applications | 107 | 46 | 49 | 12 | 8 | 41 | 50 |

## Difficulty-Depth Findings

- Healthy topic/difficulty buckets: `13`
- Thin-depth buckets: `14`
- Family-depth risk buckets: `9`
- Blocking buckets with fewer than 10 questions: `0`

A topic/difficulty bucket needs at least 10 questions to support one 10-question session. The practical depth target is 30+ questions per topic/difficulty so students can repeat sessions without seeing the same material too often.

| Topic | Difficulty | Questions | Families | Status |
| --- | --- | --- | --- | --- |
| Changes in employment opportunities, skills requirements and work practices | easy | 17 | 16 | thin_depth |
| Changes in employment opportunities, skills requirements and work practices | medium | 10 | 10 | thin_depth |
| Changes in employment opportunities, skills requirements and work practices | expert | 10 | 10 | thin_depth |
| Cloud technology | easy | 14 | 10 | thin_depth |
| Cloud technology | medium | 17 | 15 | thin_depth |
| Cloud technology | expert | 10 | 9 | family_depth_risk |
| Computer hardware | expert | 20 | 14 | thin_depth |
| Cyberspace, network security and data transfer | medium | 29 | 28 | thin_depth |
| Cyberspace, network security and data transfer | expert | 23 | 17 | thin_depth |
| Database applications | expert | 11 | 6 | family_depth_risk |
| Digital applications | medium | 13 | 9 | family_depth_risk |
| Digital applications | expert | 10 | 10 | thin_depth |
| Digital data | expert | 23 | 13 | thin_depth |
| Ethical, legal and environmental impact | easy | 19 | 19 | thin_depth |
| Ethical, legal and environmental impact | medium | 25 | 25 | thin_depth |
| Ethical, legal and environmental impact | expert | 10 | 9 | family_depth_risk |
| Health and safety | easy | 16 | 15 | thin_depth |
| Health and safety | medium | 11 | 11 | thin_depth |
| Health and safety | expert | 10 | 8 | family_depth_risk |
| Network technologies | expert | 19 | 9 | family_depth_risk |
| Software | medium | 14 | 9 | family_depth_risk |
| Software | expert | 11 | 6 | family_depth_risk |
| Spreadsheet applications | expert | 12 | 6 | family_depth_risk |

## Infrastructure Findings

- `question_family_code` and `selection_weight` now exist in the staging/live payload design.
- The repo includes a weighted family-aware picker migration: `supabase/migrations/20260504114500_weighted_family_session_picker.sql`.
- That migration must still be applied to Supabase before the live app benefits from family-aware selection.
- The picker must continue to prevent duplicate questions in a session.
- The picker should prevent duplicate families in a session where enough family depth exists, then relax that rule only when the approved bucket is thin.
- Expert sessions should not simply mean harder wording. They need scenario, source, diagram/table, or multi-step reasoning depth.

## Recommended Next Build Step

Apply and test the weighted family-aware picker migration, then move into teacher review/approval using the generated review CSV.

There are no longer any topic/difficulty buckets below 10 questions. The remaining content-depth issue is family variety in thinner buckets, especially expert buckets, so a later polish pass should add more distinct scenario families where time allows.

## Thin Buckets

These buckets can potentially run a session but need more depth for strong adaptive revision:

- Changes in employment opportunities, skills requirements and work practices / easy: 17 questions, 16 families, thin_depth
- Changes in employment opportunities, skills requirements and work practices / medium: 10 questions, 10 families, thin_depth
- Changes in employment opportunities, skills requirements and work practices / expert: 10 questions, 10 families, thin_depth
- Cloud technology / easy: 14 questions, 10 families, thin_depth
- Cloud technology / medium: 17 questions, 15 families, thin_depth
- Cloud technology / expert: 10 questions, 9 families, family_depth_risk
- Computer hardware / expert: 20 questions, 14 families, thin_depth
- Cyberspace, network security and data transfer / medium: 29 questions, 28 families, thin_depth
- Cyberspace, network security and data transfer / expert: 23 questions, 17 families, thin_depth
- Database applications / expert: 11 questions, 6 families, family_depth_risk
- Digital applications / medium: 13 questions, 9 families, family_depth_risk
- Digital applications / expert: 10 questions, 10 families, thin_depth
- Digital data / expert: 23 questions, 13 families, thin_depth
- Ethical, legal and environmental impact / easy: 19 questions, 19 families, thin_depth
- Ethical, legal and environmental impact / medium: 25 questions, 25 families, thin_depth
- Ethical, legal and environmental impact / expert: 10 questions, 9 families, family_depth_risk
- Health and safety / easy: 16 questions, 15 families, thin_depth
- Health and safety / medium: 11 questions, 11 families, thin_depth
- Health and safety / expert: 10 questions, 8 families, family_depth_risk
- Network technologies / expert: 19 questions, 9 families, family_depth_risk
- Software / medium: 14 questions, 9 families, family_depth_risk
- Software / expert: 11 questions, 6 families, family_depth_risk
- Spreadsheet applications / expert: 12 questions, 6 families, family_depth_risk
