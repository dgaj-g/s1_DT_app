-- Mobile/content wording cleanup after classroom testing.
-- Fixes relationship-direction ambiguity, removes public scaffold text, and refreshes active session snapshots.

create or replace function pg_temp.clean_public_scaffold(input_text text)
returns text
language sql
immutable
as $$
  select btrim(
    regexp_replace(
      regexp_replace(
        regexp_replace(coalesce(input_text, ''), E'\\s+Terms:\\s.*$', '', 'is'),
        E'\\s+Pairs:\\s.*$', '', 'is'
      ),
      E'\\s+[^.\\n]+→\\s*\\?(\\s*;[^.\\n]+→\\s*\\?)+',
      '',
      'is'
    )
  );
$$;

create or replace function pg_temp.is_public_scaffold_text(input_text text)
returns boolean
language sql
immutable
as $$
  select btrim(coalesce(input_text, '')) ~* '^(Terms|Pairs):';
$$;

-- 1. Clarify the bitmap resolution statement: true only when both pixel dimensions are doubled.
update public.questions
set stem = 'When both the width and height of a bitmap image are doubled, its file size approximately quadruples.',
    options_json = jsonb_build_object(
      'statement', 'When both the width and height of a bitmap image are doubled, its file size approximately quadruples.',
      'choices', jsonb_build_array('True', 'False')
    ),
    correct_answer_json = jsonb_build_object('choice', 'True'),
    markscheme_points_json = jsonb_build_array('True'),
    explanation = 'The statement is true when both pixel dimensions are doubled: twice the width and twice the height gives four times as many pixels, so the file size is approximately four times larger if colour depth and compression stay similar.',
    content_blocks_json = jsonb_build_array(jsonb_build_object(
      'kind', 'text',
      'text', 'When both the width and height of a bitmap image are doubled, its file size approximately quadruples.',
      'block_key', null
    )),
    response_schema_json = jsonb_build_object(
      'kind', 'true_false',
      'statement', 'When both the width and height of a bitmap image are doubled, its file size approximately quadruples.',
      'true_label', 'True',
      'false_label', 'False'
    ),
    autograde_rules_json = jsonb_build_object('kind', 'true_false', 'correct_value', true),
    teacher_notes = concat_ws(' | ', nullif(teacher_notes, ''), 'Classroom hotfix 2026-05-08: clarified that both bitmap dimensions are doubled before applying the quadruple file-size rule.')
where external_id = 'digital-data.practice_bank.topic_01_digital_data.q032';

-- 2. Remove positional wording from database questions so mobile layout cannot make "above" wrong.
update public.questions
set stem = 'Which data type is most suitable for the field DateOfBirth in the Member table?',
    content_blocks_json = jsonb_build_array(
      jsonb_build_object('kind', 'figure', 'caption', '2018 Q2 Database Structure (Member, MemberNewsletter, Newsletter)', 'block_key', 'figure_1'),
      jsonb_build_object('kind', 'text', 'text', 'Which data type is most suitable for the field DateOfBirth in the Member table?', 'block_key', null)
    ),
    teacher_notes = concat_ws(' | ', nullif(teacher_notes, ''), 'Classroom hotfix 2026-05-08: removed "shown above" mobile-dependent wording.')
where external_id = 'database-applications.past_paper.topics_03_04.q001';

update public.questions
set stem = 'Which data type is most suitable for the field JoiningFee in the Member table?',
    content_blocks_json = jsonb_build_array(jsonb_build_object(
      'kind', 'text',
      'text', 'Which data type is most suitable for the field JoiningFee in the Member table?',
      'block_key', null
    )),
    teacher_notes = concat_ws(' | ', nullif(teacher_notes, ''), 'Classroom hotfix 2026-05-08: removed unsupported "shown above" reference because no figure is linked to this item.')
where external_id = 'database-applications.past_paper.topics_03_04.q002';

-- 3. Make relationship-direction questions fair: one-to-many and many-to-one describe the same linked tables from opposite directions.
with relation_patch(external_id, explanation_text) as (
  values
    (
      'database-applications.past_paper.topics_03_04.q004',
      'One Member record can link to many MemberNewsletter records. Read in the opposite direction, many MemberNewsletter records link back to one Member, so one-to-many and many-to-one describe the same relationship from opposite sides.'
    ),
    (
      'database-applications.past_paper.topics_03_04.q015',
      'One member can have many loans. Read in the opposite direction, many loan records link back to one member, so one-to-many and many-to-one describe the same relationship from opposite sides.'
    ),
    (
      'database-applications.past_paper.topics_03_04.q017',
      'The diagram shows many tblCARSSOLD records can link to one tblCARS record. From the opposite direction, one car can link to many sale records, so one-to-many and many-to-one describe the same relationship from opposite sides.'
    )
)
update public.questions q
set options_json = jsonb_build_object(
      'choices', jsonb_build_array('One to one', 'One to many / many to one', 'Many to many', 'No relationship')
    ),
    correct_answer_json = jsonb_build_object('choice', 'One to many / many to one'),
    markscheme_points_json = jsonb_build_array('One to many / many to one'),
    explanation = relation_patch.explanation_text,
    response_schema_json = jsonb_build_object(
      'kind', 'single_choice',
      'choices', jsonb_build_array(
        jsonb_build_object('id', 'a', 'label', 'One to one'),
        jsonb_build_object('id', 'b', 'label', 'One to many / many to one'),
        jsonb_build_object('id', 'c', 'label', 'Many to many'),
        jsonb_build_object('id', 'd', 'label', 'No relationship')
      )
    ),
    autograde_rules_json = jsonb_build_object('kind', 'single_choice', 'correct_choice_id', 'b'),
    teacher_notes = concat_ws(' | ', nullif(q.teacher_notes, ''), 'Classroom hotfix 2026-05-08: combined one-to-many/many-to-one as one fair answer because relationship wording direction can be read both ways.')
from relation_patch
where q.external_id = relation_patch.external_id;

-- 4. Add context to the Event composite-key item and move it out of Easy.
update public.questions
set difficulty = 'medium'::public.difficulty_level,
    adaptive_tier = 'core'::public.adaptive_tier,
    stem = 'A database design is written as: Event(Event_Name, Gender, Gold_Medalist*, Time). In this design, Event_Name and Gender together can be used as a composite primary key.',
    options_json = jsonb_build_object(
      'statement', 'A database design is written as: Event(Event_Name, Gender, Gold_Medalist*, Time). In this design, Event_Name and Gender together can be used as a composite primary key.',
      'choices', jsonb_build_array('True', 'False')
    ),
    correct_answer_json = jsonb_build_object('choice', 'True'),
    markscheme_points_json = jsonb_build_array('True'),
    explanation = 'The statement is true. A composite primary key uses more than one field together to uniquely identify each record. Here, Event_Name and Gender together can distinguish records such as male and female versions of the same event.',
    content_blocks_json = jsonb_build_array(jsonb_build_object(
      'kind', 'text',
      'text', 'A database design is written as: Event(Event_Name, Gender, Gold_Medalist*, Time). In this design, Event_Name and Gender together can be used as a composite primary key.',
      'block_key', null
    )),
    response_schema_json = jsonb_build_object(
      'kind', 'true_false',
      'statement', 'A database design is written as: Event(Event_Name, Gender, Gold_Medalist*, Time). In this design, Event_Name and Gender together can be used as a composite primary key.',
      'true_label', 'True',
      'false_label', 'False'
    ),
    autograde_rules_json = jsonb_build_object('kind', 'true_false', 'correct_value', true),
    teacher_notes = concat_ws(' | ', nullif(teacher_notes, ''), 'Classroom hotfix 2026-05-08: made composite-key context self-contained and moved item from easy/support to medium/core.')
where external_id = 'database-applications.practice_bank.topic_02_03_software_database.q063';

-- 5. Remove public generator scaffold from stems and prompt blocks across the live bank.
update public.questions
set stem = pg_temp.clean_public_scaffold(stem),
    teacher_notes = concat_ws(' | ', nullif(teacher_notes, ''), 'Classroom hotfix 2026-05-08: stripped public scaffold text such as Terms:/Pairs: from the displayed stem.')
where stem ilike '%Terms:%'
   or stem ilike '%Pairs:%'
   or stem like '%→ ?%';

with transformed as (
  select q.id,
         coalesce(
           jsonb_agg(cleaned.block order by e.ord) filter (where cleaned.block is not null),
           '[]'::jsonb
         ) as next_blocks
  from public.questions q
  cross join lateral jsonb_array_elements(coalesce(q.content_blocks_json, '[]'::jsonb)) with ordinality as e(block, ord)
  cross join lateral (
    select case
      when e.block ? 'text' and pg_temp.is_public_scaffold_text(e.block ->> 'text') then null
      when e.block ? 'body' and pg_temp.is_public_scaffold_text(e.block ->> 'body') then null
      when e.block ? 'items' and jsonb_typeof(e.block -> 'items') = 'array' then
        jsonb_set(
          case
            when e.block ? 'text' then jsonb_set(e.block, '{text}', to_jsonb(pg_temp.clean_public_scaffold(e.block ->> 'text')), true)
            else e.block
          end,
          '{items}',
          (
            select coalesce(
              jsonb_agg(to_jsonb(pg_temp.clean_public_scaffold(item.value)) order by item.ord)
                filter (where not pg_temp.is_public_scaffold_text(item.value) and pg_temp.clean_public_scaffold(item.value) <> ''),
              '[]'::jsonb
            )
            from jsonb_array_elements_text(e.block -> 'items') with ordinality as item(value, ord)
          ),
          true
        )
      when e.block ? 'text' then jsonb_set(e.block, '{text}', to_jsonb(pg_temp.clean_public_scaffold(e.block ->> 'text')), true)
      when e.block ? 'body' then jsonb_set(e.block, '{body}', to_jsonb(pg_temp.clean_public_scaffold(e.block ->> 'body')), true)
      else e.block
    end as block
  ) cleaned
  where q.content_blocks_json::text ilike '%Terms:%'
     or q.content_blocks_json::text ilike '%Pairs:%'
     or q.content_blocks_json::text like '%→ ?%'
  group by q.id
)
update public.questions q
set content_blocks_json = transformed.next_blocks,
    teacher_notes = concat_ws(' | ', nullif(q.teacher_notes, ''), 'Classroom hotfix 2026-05-08: stripped public scaffold text from prompt blocks.')
from transformed
where q.id = transformed.id;

-- 6. Clean accidental scaffold from match-table row labels and matching keys.
with transformed as (
  select q.id,
         jsonb_set(
           q.options_json,
           '{pairs}',
           (
             select coalesce(
               jsonb_agg(
                 case
                   when pair.value ? 'left' then jsonb_set(pair.value, '{left}', to_jsonb(pg_temp.clean_public_scaffold(pair.value ->> 'left')), true)
                   else pair.value
                 end
                 order by pair.ord
               ),
               '[]'::jsonb
             )
             from jsonb_array_elements(coalesce(q.options_json -> 'pairs', '[]'::jsonb)) with ordinality as pair(value, ord)
           ),
           true
         ) as next_options
  from public.questions q
  where q.format = 'match_table'::public.question_format
    and q.options_json ? 'pairs'
    and q.options_json::text ilike '%Terms:%'
)
update public.questions q
set options_json = transformed.next_options
from transformed
where q.id = transformed.id;

with transformed as (
  select q.id,
         jsonb_set(
           q.correct_answer_json,
           '{pairs}',
           (
             select coalesce(jsonb_object_agg(pg_temp.clean_public_scaffold(pair.key), pair.value), '{}'::jsonb)
             from jsonb_each_text(coalesce(q.correct_answer_json -> 'pairs', '{}'::jsonb)) as pair(key, value)
           ),
           true
         ) as next_correct
  from public.questions q
  where q.format = 'match_table'::public.question_format
    and q.correct_answer_json ? 'pairs'
    and q.correct_answer_json::text ilike '%Terms:%'
)
update public.questions q
set correct_answer_json = transformed.next_correct
from transformed
where q.id = transformed.id;

with transformed as (
  select q.id,
         jsonb_set(
           q.response_schema_json,
           '{rows}',
           (
             select coalesce(
               jsonb_agg(
                 case
                   when row.value ? 'label' then jsonb_set(row.value, '{label}', to_jsonb(pg_temp.clean_public_scaffold(row.value ->> 'label')), true)
                   else row.value
                 end
                 order by row.ord
               ),
               '[]'::jsonb
             )
             from jsonb_array_elements(coalesce(q.response_schema_json -> 'rows', '[]'::jsonb)) with ordinality as row(value, ord)
           ),
           true
         ) as next_schema
  from public.questions q
  where q.format = 'match_table'::public.question_format
    and q.response_schema_json ? 'rows'
    and q.response_schema_json::text ilike '%Terms:%'
)
update public.questions q
set response_schema_json = transformed.next_schema
from transformed
where q.id = transformed.id;

with transformed as (
  select q.id,
         (
           select coalesce(
             jsonb_agg(to_jsonb(pg_temp.clean_public_scaffold(item.value)) order by item.ord),
             '[]'::jsonb
           )
           from jsonb_array_elements_text(coalesce(q.markscheme_points_json, '[]'::jsonb)) with ordinality as item(value, ord)
         ) as next_points
  from public.questions q
  where q.markscheme_points_json::text ilike '%Terms:%'
     or q.markscheme_points_json::text ilike '%Pairs:%'
)
update public.questions q
set markscheme_points_json = transformed.next_points
from transformed
where q.id = transformed.id;

-- 7. Refresh existing incomplete runtime snapshots so pupils do not keep seeing stale wording mid-session.
update public.session_questions sq
set question_snapshot_json = public.build_runtime_question_payload(sq.question_id, sq.id)
from public.sessions s
where s.id = sq.session_id
  and s.completed_at is null
  and sq.question_id is not null
  and sq.grading_status <> 'graded';

-- 8. Guardrails: fail the migration if the reported defects are still present in live active questions.
do $$
declare
  bad_count integer;
begin
  select count(*) into bad_count
  from public.questions
  where is_active
    and (
      stem ilike '%Terms:%'
      or stem ilike '%Pairs:%'
      or stem ilike '%shown above%'
      or stem ilike '%shown below%'
    );

  if bad_count > 0 then
    raise exception 'Classroom hotfix validation failed: % active question stems still contain public scaffold or positional wording.', bad_count;
  end if;

  select count(*) into bad_count
  from public.questions
  where external_id = 'database-applications.practice_bank.topic_02_03_software_database.q063'
    and difficulty <> 'medium'::public.difficulty_level;

  if bad_count > 0 then
    raise exception 'Classroom hotfix validation failed: Event composite-key question was not moved to medium.';
  end if;

  select count(*) into bad_count
  from public.questions
  where external_id in (
    'database-applications.past_paper.topics_03_04.q004',
    'database-applications.past_paper.topics_03_04.q015',
    'database-applications.past_paper.topics_03_04.q017'
  )
  and not (options_json::text ilike '%One to many / many to one%');

  if bad_count > 0 then
    raise exception 'Classroom hotfix validation failed: relationship-direction choices were not combined.';
  end if;
end $$;
