# Supabase Import Artifacts

This folder is for generated Unit 1 import artifacts.

These files are not automatically written to Supabase. They are local review and
promotion payloads used to keep the question bank controlled before anything is
made available to students.

## Stage 4 Source-To-Review Flow

Current producers:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_import_bundle.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_staging_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage4_teacher_review_report.py`

Key outputs:

- `unit1_stage4_import_bundle.json`
- `unit1_stage4_staging_payload.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-teacher-question-review.csv`

## Stage 5 Approval Gate

Current producer:

- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage5_approval_payload.py`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/scripts/build_stage5_asset_package.py`

Key outputs:

- `unit1_stage5_approved_staging_payload.json`
- `unit1_stage5_approved_live_payload.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-approval-summary.json`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-approval-bucket-summary.csv`
- `question_assets_upload/`
- `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-asset-upload-manifest.csv`

Important rule:

- blank `teacher_decision` values are not approved
- only explicit approved rows can reach `unit1_stage5_approved_live_payload.json`
- the Stage 5 script does not contact Supabase or deploy anything

Recommended workflow:

1. build the import bundle from the curated source pack
2. transform the bundle into the Stage 4 staging payload
3. generate and review the teacher CSV
4. mark teacher decisions in the CSV
5. run the Stage 5 approval gate
6. package the visual assets into the expected storage layout
7. check the approval summary, bucket readiness, and asset manifest
8. only then apply a separate Supabase import/upload step
