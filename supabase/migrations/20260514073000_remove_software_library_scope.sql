-- Remove code-library content from the Software topic scope.
-- Verification on 2026-05-14 found library programs only in the Software fact file
-- and generated practice material, not in the extracted past-paper packs or OCR'd
-- textbook Software scan. Keep compiler content where supported, but remove library
-- programs as taught/tested content from student sessions.

begin;

with retired_questions as (
  update public.questions q
  set
    is_active = false,
    qa_status = 'draft',
    teacher_notes = concat_ws(
      ' | ',
      nullif(q.teacher_notes, ''),
      'Scope correction 2026-05-14: removed from live student sessions because code-library/library-program content is outside the confirmed Software topic scope.'
    )
  from public.topics t
  where q.topic_id = t.id
    and t.slug = 'software'
    and q.external_id in (
      'software.practice_bank.topic_02_03_software_database.q004',
      'software.practice_bank.topic_02_03_software_database.q006',
      'software.practice_bank.expert_balancing_2026_05.q005'
    )
  returning q.id
)
delete from public.question_objectives qo
using retired_questions rq
where qo.question_id = rq.id;

-- Keep the valid system-software question, but remove the library distractor.
update public.questions q
set
  options_json = jsonb_set(q.options_json, '{choices,0}', to_jsonb('Spreadsheet software'::text), false),
  response_schema_json = jsonb_set(q.response_schema_json, '{choices,0,label}', to_jsonb('Spreadsheet software'::text), false),
  explanation = 'The correct option is System software. This question checks whether you can explain how system software allows the computer to operate and supports application software.',
  teacher_notes = concat_ws(
    ' | ',
    nullif(q.teacher_notes, ''),
    'Scope correction 2026-05-14: replaced library-software distractor with spreadsheet-software distractor.'
  )
from public.topics t
where q.topic_id = t.id
  and t.slug = 'software'
  and q.external_id = 'software.practice_bank.topic_02_03_software_database.q002';

-- Keep the valid batch-processing question, but remove the unrelated library-file distractor.
update public.questions q
set
  options_json = jsonb_set(q.options_json, '{choices,2}', to_jsonb('Backup file'::text), false),
  response_schema_json = jsonb_set(q.response_schema_json, '{choices,2,label}', to_jsonb('Backup file'::text), false),
  teacher_notes = concat_ws(
    ' | ',
    nullif(q.teacher_notes, ''),
    'Scope correction 2026-05-14: replaced library-file distractor with backup-file distractor.'
  )
from public.topics t
where q.topic_id = t.id
  and t.slug = 'software'
  and q.external_id = 'software.practice_bank.topic_02_03_software_database.q034';

-- Remove library wording from explanations on otherwise valid Software questions.
update public.questions q
set explanation = replace(
  explanation,
  'It also checks whether you can classify software as system, utility, application, translator or library software.',
  'It also checks whether you can classify software as system, utility and application software.'
)
from public.topics t
where q.topic_id = t.id
  and t.slug = 'software'
  and explanation like '%translator or library software%';

update public.questions q
set explanation = replace(
  explanation,
  'This question checks whether you can classify software as system, utility, application, translator or library software.',
  'This question checks whether you can classify software as system, utility and application software.'
)
from public.topics t
where q.topic_id = t.id
  and t.slug = 'software'
  and explanation like '%translator or library software%';

update public.questions q
set explanation = 'The correct option is To translate a high-level language program into machine code. This question checks whether you can explain the role of a compiler.'
from public.topics t
where q.topic_id = t.id
  and t.slug = 'software'
  and q.external_id = 'software.practice_bank.topic_02_03_software_database.q005';

-- Align teacher/admin objective labels with the tighter scope.
update public.learning_objectives lo
set description = 'Classify software as system, utility and application software.'
from public.topics t
where lo.topic_id = t.id
  and t.slug = 'software'
  and lo.objective_code = 'software.software-categories';

update public.learning_objectives lo
set
  objective_code = 'software.compiler-role',
  title = 'Compiler role',
  description = 'Explain the role of a compiler in translating high-level language into machine code.'
from public.topics t
where lo.topic_id = t.id
  and t.slug = 'software'
  and lo.objective_code = 'software.translators-and-libraries'
  and not exists (
    select 1
    from public.learning_objectives existing
    where existing.topic_id = t.id
      and existing.objective_code = 'software.compiler-role'
  );

update public.learning_objectives lo
set
  title = 'Compiler role',
  description = 'Explain the role of a compiler in translating high-level language into machine code.',
  is_active = true
from public.topics t
where lo.topic_id = t.id
  and t.slug = 'software'
  and lo.objective_code = 'software.compiler-role';

commit;
