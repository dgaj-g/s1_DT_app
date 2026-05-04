# Stage 5 Approval Gate Report (2026-05-04)

## Purpose
This report checks whether teacher review decisions can safely become student-facing questions.

Blank teacher decisions are deliberately treated as not approved. This prevents unreviewed questions from leaking into student sessions.

## Decision Summary
- Source staged questions: 938
- Approved by teacher review CSV: 938
- Rejected: 0
- Needs edit / held as draft: 0
- Undecided / blank: 0
- Invalid decisions: 0

## Live Payload Summary
- Promoted into live runtime payload: 938
- Rejected by runtime checks: 0
- Linked question assets: 29
- Linked objectives: 1035

## Session Readiness
- Minimum per topic/difficulty bucket used for this check: 10
- Buckets below minimum after approval: 0

## Outputs
- Approved staging payload: `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage5_approved_staging_payload.json`
- Approved live payload: `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/supabase/imports/unit1_stage5_approved_live_payload.json`
- JSON summary: `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-approval-summary.json`
- Bucket CSV: `/Users/damiengartland/Desktop/Codex Work/s1-network-revision-app/docs/unit1-stage5-approval-bucket-summary.csv`

## Safety Position
This script does not write to Supabase. It only creates local payload files. Remote import/deployment remains a separate deliberate step.
