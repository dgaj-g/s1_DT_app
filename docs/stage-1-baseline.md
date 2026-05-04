# Stage 1 Baseline

This file records the agreed baseline before the Unit 1 rebuild starts.

## Keep

- Existing student usernames and passwords
- Existing admin account
- Existing GitHub repo
- Existing Supabase project

## Replace or Reset

- Current question bank
- Current student attempt history
- Current weak stats model
- Current adaptive recommendation model

## Current Source Pack For Rebuild

- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/GCSE DT Unit 1 - Past Paper Questions by Topic.docx`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/GCSE DT Unit 1 - Past Paper Questions (Auto-Markable) by Topic.docx`
- `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/GCSE DT Unit 1 - Practice Questions by Topic.docx`
- All fact files in `/Users/damiengartland/Desktop/Codex Work/GCSE Unit 1 Revision Project/`
- QA notes and extraction files in the same folder

## Topic Names To Match Exactly

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

## Reset Strategy For Later Execution

The rebuild is expected to preserve:

- `auth.users`
- `profiles`
- `student_accounts`
- `academic_years`

The rebuild is expected to replace or archive data derived from the current live revision build:

- `sessions`
- `session_questions`
- `daily_caps`
- `student_achievements`

`admin_events` can be retained unless a clean reporting reset is preferred later.

## Current Repo State At Start Of Rebuild

- Branch: `main`
- Remote tracking branch: `origin/main`
- Working tree was clean apart from documentation files added during handoff and baseline work

## Stage 2 Stability Priorities

- Harden auth bootstrap and profile loading
- Add request timeouts so the UI does not sit on endless spinners
- Add retry paths for failed loads
- Add an app-level error boundary
- Reduce page crashes caused by async state updates after unmount
