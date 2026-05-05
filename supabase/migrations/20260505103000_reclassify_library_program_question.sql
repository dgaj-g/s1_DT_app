-- Reclassify source-backed library-program question from Easy to Medium.
-- Rationale: Factfile Unit 1 - Software defines library programs, but this is
-- a niche system-software classification item rather than Easy recognition.

begin;

update public.questions
set difficulty = 'medium'::public.difficulty_level,
    adaptive_tier = 'core'::public.adaptive_tier,
    teacher_notes = concat_ws(
      ' | ',
      nullif(teacher_notes, ''),
      'Difficulty review 2026-05-05: moved from Easy to Medium after checking Software fact file and GCSE specification scope.'
    )
where external_id = 'software.practice_bank.topic_02_03_software_database.q006';

update public.session_questions sq
set question_snapshot_json = public.build_runtime_question_payload(sq.question_id, sq.id)
from public.sessions s, public.questions q
where s.id = sq.session_id
  and q.id = sq.question_id
  and s.completed_at is null
  and q.external_id = 'software.practice_bank.topic_02_03_software_database.q006';

do $$
declare
  easy_count integer;
  medium_count integer;
begin
  select count(*) into easy_count
  from public.questions
  where external_id = 'software.practice_bank.topic_02_03_software_database.q006'
    and difficulty = 'easy'::public.difficulty_level;

  if easy_count <> 0 then
    raise exception 'Library-program question is still classified as easy';
  end if;

  select count(*) into medium_count
  from public.questions
  where external_id = 'software.practice_bank.topic_02_03_software_database.q006'
    and difficulty = 'medium'::public.difficulty_level
    and adaptive_tier = 'core'::public.adaptive_tier;

  if medium_count <> 1 then
    raise exception 'Library-program question was not reclassified to medium/core';
  end if;
end $$;

commit;
