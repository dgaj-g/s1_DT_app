-- Keep QA and student-session availability aligned.
-- Draft questions should not be marked as in-session use.

update public.questions
set is_active = false
where qa_status = 'draft'
  and is_active = true;
