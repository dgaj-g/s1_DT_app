-- Phase 1 runtime trust boundary and normalized session/grading RPCs.
-- This migration is additive: it keeps the older session flow available while
-- introducing the v2 path that will become the student-facing authority.

alter type public.question_format add value if not exists 'true_false';

do $$
begin
  if not exists (select 1 from pg_type where typname = 'session_question_status') then
    create type public.session_question_status as enum ('pending', 'graded');
  end if;
end
$$;

alter table public.session_questions
  add column if not exists grading_status public.session_question_status not null default 'pending',
  add column if not exists answered_at timestamptz,
  add column if not exists graded_at timestamptz,
  add column if not exists grading_feedback_json jsonb not null default '{}'::jsonb;

create index if not exists idx_session_questions_session_status_position
  on public.session_questions(session_id, grading_status, position);

create or replace function public.normalize_answer_token(p_input text)
returns text
language sql
immutable
as $$
  select trim(
    regexp_replace(
      regexp_replace(lower(coalesce(p_input, '')), '[^a-z0-9]+', ' ', 'g'),
      '\s+',
      ' ',
      'g'
    )
  );
$$;

create or replace function public.normalize_answer_phrase(p_input text)
returns text
language sql
immutable
as $$
  select trim(
    regexp_replace(lower(coalesce(p_input, '')), '\s+', ' ', 'g')
  );
$$;

create or replace function public.answer_text_matches(
  p_answer text,
  p_accepted jsonb,
  p_normalization text default 'phrase',
  p_match_mode text default 'exact'
)
returns boolean
language plpgsql
immutable
as $$
declare
  accepted_value text;
  normalized_answer text;
  normalized_accepted text;
  accepted_array jsonb := case
    when jsonb_typeof(coalesce(p_accepted, '[]'::jsonb)) = 'array' then coalesce(p_accepted, '[]'::jsonb)
    when p_accepted is null then '[]'::jsonb
    else jsonb_build_array(p_accepted)
  end;
begin
  normalized_answer := case
    when p_normalization = 'token' then public.normalize_answer_token(p_answer)
    else public.normalize_answer_phrase(p_answer)
  end;

  if normalized_answer = '' then
    return false;
  end if;

  for accepted_value in
    select jsonb_array_elements_text(accepted_array)
  loop
    normalized_accepted := case
      when p_normalization = 'token' then public.normalize_answer_token(accepted_value)
      else public.normalize_answer_phrase(accepted_value)
    end;

    if normalized_accepted = '' then
      continue;
    end if;

    if p_match_mode = 'contains' then
      if normalized_answer like '%' || normalized_accepted || '%'
         or normalized_accepted like '%' || normalized_answer || '%' then
        return true;
      end if;
    else
      if normalized_answer = normalized_accepted then
        return true;
      end if;
    end if;
  end loop;

  return false;
end;
$$;

create or replace function public.answer_text_match_group(
  p_answer text,
  p_groups jsonb,
  p_normalization text default 'phrase',
  p_match_mode text default 'exact'
)
returns text
language plpgsql
immutable
as $$
declare
  group_item jsonb;
  canonical_value text;
begin
  if jsonb_typeof(coalesce(p_groups, '[]'::jsonb)) <> 'array' then
    return null;
  end if;

  for group_item in
    select * from jsonb_array_elements(coalesce(p_groups, '[]'::jsonb))
  loop
    canonical_value := coalesce(group_item ->> 'canonical', '');
    if canonical_value = '' then
      continue;
    end if;

    if public.answer_text_matches(
      p_answer,
      group_item -> 'accepted',
      p_normalization,
      p_match_mode
    ) then
      return canonical_value;
    end if;
  end loop;

  return null;
end;
$$;

create or replace function public.build_runtime_question_payload(
  p_question_id uuid,
  p_session_question_id uuid default null
)
returns jsonb
language plpgsql
stable
set search_path = public
as $$
declare
  q public.questions%rowtype;
  prompt_blocks jsonb := '[]'::jsonb;
  response_schema jsonb := '{}'::jsonb;
  autograde_rules jsonb := '{}'::jsonb;
  assets jsonb := '[]'::jsonb;
  objective_ids jsonb := '[]'::jsonb;
  runtime_format text;
  pair_item jsonb;
  rows_json jsonb := '[]'::jsonb;
  choices_json jsonb := '[]'::jsonb;
  pair_rules_json jsonb := '[]'::jsonb;
  gap_rules_json jsonb := '[]'::jsonb;
  choice_text text;
  pair_key text;
  pair_value text;
  gap_id text;
  idx integer := 0;
  marker_value text;
  diagram_key text;
begin
  select *
  into q
  from public.questions
  where id = p_question_id;

  if not found then
    raise exception 'Question % not found', p_question_id;
  end if;

  runtime_format := case
    when q.format = 'structured_response' then 'short_text'
    else q.format::text
  end;

  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'asset_id', qa.id,
        'role', qal.asset_role,
        'kind', qa.asset_kind,
        'bucket', qa.storage_bucket,
        'path', qa.storage_path,
        'alt_text', qa.alt_text,
        'caption', qa.caption,
        'display_order', qal.display_order,
        'block_key', qal.block_key
      )
      order by qal.display_order asc
    ),
    '[]'::jsonb
  )
  into assets
  from public.question_asset_links qal
  join public.question_assets qa on qa.id = qal.asset_id
  where qal.question_id = q.id;

  select coalesce(
    jsonb_agg(qo.objective_id order by qo.is_primary desc, qo.display_order asc),
    '[]'::jsonb
  )
  into objective_ids
  from public.question_objectives qo
  where qo.question_id = q.id;

  prompt_blocks := case
    when jsonb_typeof(coalesce(q.content_blocks_json, '[]'::jsonb)) = 'array'
         and q.content_blocks_json <> '[]'::jsonb then q.content_blocks_json
    else '[]'::jsonb
  end;

  if coalesce(q.response_schema_json, '{}'::jsonb) <> '{}'::jsonb then
    response_schema := q.response_schema_json;
  end if;

  if coalesce(q.autograde_rules_json, '{}'::jsonb) <> '{}'::jsonb then
    autograde_rules := q.autograde_rules_json;
  end if;

  if response_schema = '{}'::jsonb then
    case runtime_format
      when 'mcq' then
        choices_json := '[]'::jsonb;
        for choice_text in
          select jsonb_array_elements_text(coalesce(q.options_json -> 'choices', '[]'::jsonb))
        loop
          choices_json := choices_json || jsonb_build_array(
            jsonb_build_object('id', md5(choice_text), 'label', choice_text)
          );
        end loop;

        response_schema := jsonb_build_object(
          'kind', 'single_choice',
          'choices', choices_json
        );

      when 'true_false' then
        response_schema := jsonb_build_object(
          'kind', 'true_false',
          'statement', coalesce(q.options_json ->> 'statement', q.stem),
          'true_label', 'True',
          'false_label', 'False'
        );

      when 'match_table' then
        rows_json := '[]'::jsonb;
        choices_json := '[]'::jsonb;

        for pair_item in
          select * from jsonb_array_elements(coalesce(q.options_json -> 'pairs', '[]'::jsonb))
        loop
          pair_key := coalesce(pair_item ->> 'left', pair_item ->> 'label', pair_item ->> 'id', 'row-' || idx::text);
          rows_json := rows_json || jsonb_build_array(
            jsonb_build_object('id', md5(pair_key), 'label', pair_key)
          );

          if coalesce(pair_item ->> 'right', '') <> '' then
            choices_json := choices_json || jsonb_build_array(
              jsonb_build_object('id', md5(pair_item ->> 'right'), 'label', pair_item ->> 'right')
            );
          end if;

          idx := idx + 1;
        end loop;

        if choices_json = '[]'::jsonb then
          for choice_text in
            select jsonb_array_elements_text(coalesce(q.options_json -> 'choices', '[]'::jsonb))
          loop
            choices_json := choices_json || jsonb_build_array(
              jsonb_build_object('id', md5(choice_text), 'label', choice_text)
            );
          end loop;
        end if;

        if choices_json = '[]'::jsonb then
          for pair_key, pair_value in
            select key, value from jsonb_each_text(coalesce(q.correct_answer_json -> 'pairs', '{}'::jsonb))
          loop
            choices_json := choices_json || jsonb_build_array(
              jsonb_build_object('id', md5(pair_value), 'label', pair_value)
            );
          end loop;
        end if;

        response_schema := jsonb_build_object(
          'kind', 'match_table',
          'rows', rows_json,
          'choices', choices_json
        );

      when 'fill_gap' then
        response_schema := jsonb_build_object(
          'kind', 'fill_gap',
          'gaps', jsonb_build_array(
            jsonb_build_object('id', 'gap1', 'label', 'Gap 1')
          )
        );

      when 'short_text' then
        response_schema := jsonb_build_object(
          'kind', 'short_text',
          'placeholder', 'Type your answer',
          'max_length', 180
        );

      when 'multi_select' then
        choices_json := '[]'::jsonb;
        for choice_text in
          select jsonb_array_elements_text(coalesce(q.options_json -> 'choices', '[]'::jsonb))
        loop
          choices_json := choices_json || jsonb_build_array(
            jsonb_build_object('id', md5(choice_text), 'label', choice_text)
          );
        end loop;

        response_schema := jsonb_build_object(
          'kind', 'multi_select',
          'choices', choices_json,
          'min_select', 1,
          'max_select', greatest(1, jsonb_array_length(coalesce(q.correct_answer_json -> 'correct_choice_ids', '[]'::jsonb)))
        );

      when 'drag_drop' then
        choices_json := '[]'::jsonb;
        for choice_text in
          select jsonb_array_elements_text(coalesce(q.options_json -> 'items', '[]'::jsonb))
        loop
          choices_json := choices_json || jsonb_build_array(
            jsonb_build_object('id', md5(choice_text), 'label', choice_text)
          );
        end loop;

        response_schema := jsonb_build_object(
          'kind', 'ordering',
          'items', choices_json
        );

      when 'diagram_label' then
        choices_json := '[]'::jsonb;
        for choice_text in
          select jsonb_array_elements_text(coalesce(q.options_json -> 'choices', '[]'::jsonb))
        loop
          choices_json := choices_json || jsonb_build_array(
            jsonb_build_object('id', md5(choice_text), 'label', choice_text)
          );
        end loop;

        marker_value := coalesce(q.options_json ->> 'marker', q.options_json ->> 'callout');
        diagram_key := q.options_json ->> 'diagram_key';

        response_schema := jsonb_build_object(
          'kind', 'diagram_label',
          'input_mode', case when choices_json = '[]'::jsonb then 'text' else 'single_choice' end,
          'diagram_key', diagram_key,
          'marker', marker_value,
          'choices', choices_json,
          'placeholder', 'Type your label'
        );
      else
        response_schema := jsonb_build_object(
          'kind', 'unsupported'
        );
    end case;
  end if;

  if autograde_rules = '{}'::jsonb then
    case runtime_format
      when 'mcq' then
        autograde_rules := jsonb_build_object(
          'kind', 'single_choice',
          'correct_choice_id', md5(coalesce(q.correct_answer_json ->> 'choice', ''))
        );

      when 'true_false' then
        autograde_rules := jsonb_build_object(
          'kind', 'true_false',
          'correct_value', coalesce((q.correct_answer_json ->> 'value')::boolean, false)
        );

      when 'match_table' then
        pair_rules_json := '[]'::jsonb;
        for pair_key, pair_value in
          select key, value from jsonb_each_text(coalesce(q.correct_answer_json -> 'pairs', '{}'::jsonb))
        loop
          pair_rules_json := pair_rules_json || jsonb_build_array(
            jsonb_build_object(
              'row_id', md5(pair_key),
              'choice_id', md5(pair_value)
            )
          );
        end loop;

        autograde_rules := jsonb_build_object(
          'kind', 'match_table',
          'pairs', pair_rules_json
        );

      when 'fill_gap' then
        gap_rules_json := jsonb_build_array(
          jsonb_build_object(
            'id', 'gap1',
            'accepted', coalesce(q.correct_answer_json -> 'accepted', '[]'::jsonb),
            'normalization', 'token'
          )
        );

        autograde_rules := jsonb_build_object(
          'kind', 'fill_gap',
          'gaps', gap_rules_json,
          'require_all', true
        );

      when 'short_text' then
        autograde_rules := jsonb_build_object(
          'kind', 'accepted_terms',
          'accepted', coalesce(q.correct_answer_json -> 'accepted', '[]'::jsonb),
          'normalization', 'phrase',
          'match_mode', 'exact'
        );

      when 'multi_select' then
        autograde_rules := jsonb_build_object(
          'kind', 'multi_select',
          'correct_choice_ids', coalesce(q.correct_answer_json -> 'correct_choice_ids', '[]'::jsonb),
          'require_exact_set', true
        );

      when 'drag_drop' then
        pair_rules_json := '[]'::jsonb;
        for choice_text in
          select jsonb_array_elements_text(coalesce(q.correct_answer_json -> 'order', '[]'::jsonb))
        loop
          pair_rules_json := pair_rules_json || jsonb_build_array(md5(choice_text));
        end loop;

        autograde_rules := jsonb_build_object(
          'kind', 'ordering',
          'correct_item_ids', pair_rules_json
        );

      when 'diagram_label' then
        if q.correct_answer_json ? 'choice' then
          autograde_rules := jsonb_build_object(
            'kind', 'single_choice',
            'correct_choice_id', md5(coalesce(q.correct_answer_json ->> 'choice', ''))
          );
        else
          autograde_rules := jsonb_build_object(
            'kind', 'accepted_terms',
            'accepted', coalesce(q.correct_answer_json -> 'accepted', '[]'::jsonb),
            'normalization', 'phrase',
            'match_mode', 'exact'
          );
        end if;
      else
        autograde_rules := jsonb_build_object('kind', 'unsupported');
    end case;
  end if;

  return jsonb_build_object(
    'session_item_id', coalesce(p_session_question_id::text, ''),
    'question_id', q.id,
    'topic_id', q.topic_id,
    'difficulty', q.difficulty,
    'adaptive_tier', q.adaptive_tier,
    'format', runtime_format,
    'max_marks', coalesce(q.max_marks, 1),
    'family_code', q.question_family_code,
    'stem', q.stem,
    'prompt_blocks', prompt_blocks,
    'assets', assets,
    'response_schema', response_schema,
    'autograde_rules', autograde_rules,
    'explanation', q.explanation,
    'tags', coalesce(q.tags_json, '[]'::jsonb),
    'objective_ids', objective_ids
  );
end;
$$;

create or replace function public.grade_runtime_question(
  p_runtime_question jsonb,
  p_student_answer jsonb
)
returns jsonb
language plpgsql
immutable
as $$
declare
  autograde_kind text := coalesce(p_runtime_question -> 'autograde_rules' ->> 'kind', 'unsupported');
  response_kind text := coalesce(p_runtime_question -> 'response_schema' ->> 'kind', '');
  marks_available integer := greatest(1, coalesce((p_runtime_question ->> 'max_marks')::integer, 1));
  marks_awarded integer := 0;
  result_text text := 'incorrect';
  is_correct boolean := false;
  feedback_summary text := 'Not quite right';
  corrections jsonb := '[]'::jsonb;
  accepted_preview jsonb := '[]'::jsonb;
  answer_text text;
  selected_choice text;
  expected_choice text;
  selected_value boolean;
  expected_value boolean;
  correct_count integer;
  total_count integer;
  row_rule jsonb;
  gap_rule jsonb;
  selected_pairs jsonb := coalesce(p_student_answer -> 'pairs', '{}'::jsonb);
  student_gaps jsonb := coalesce(p_student_answer -> 'gaps', '{}'::jsonb);
  require_distinct boolean := coalesce((p_runtime_question -> 'autograde_rules' ->> 'require_distinct')::boolean, false);
  seen_gap_answers text[] := array[]::text[];
  gap_normalized text;
  student_choice_ids text[];
  expected_choice_ids text[];
  student_order_ids text[];
  expected_order_ids text[];
  selected_text text;
  gap_text text;
  partial_marks integer;
  matched_group text;
begin
  case autograde_kind
    when 'single_choice' then
      selected_choice := coalesce(p_student_answer ->> 'choice', '');
      expected_choice := coalesce(p_runtime_question -> 'autograde_rules' ->> 'correct_choice_id', '');

      if selected_choice <> '' and selected_choice = expected_choice then
        marks_awarded := marks_available;
        is_correct := true;
      else
        corrections := jsonb_build_array(
          jsonb_build_object('expected_choice_id', expected_choice)
        );
      end if;

    when 'true_false' then
      selected_value := coalesce((p_student_answer ->> 'value')::boolean, false);
      expected_value := coalesce((p_runtime_question -> 'autograde_rules' ->> 'correct_value')::boolean, false);

      if selected_value = expected_value then
        marks_awarded := marks_available;
        is_correct := true;
      else
        corrections := jsonb_build_array(
          jsonb_build_object('expected_value', expected_value)
        );
      end if;

    when 'accepted_terms' then
      answer_text := coalesce(p_student_answer ->> 'text', '');
      accepted_preview := coalesce(p_runtime_question -> 'autograde_rules' -> 'accepted', '[]'::jsonb);

      if public.answer_text_matches(
        answer_text,
        p_runtime_question -> 'autograde_rules' -> 'accepted',
        coalesce(p_runtime_question -> 'autograde_rules' ->> 'normalization', 'phrase'),
        coalesce(p_runtime_question -> 'autograde_rules' ->> 'match_mode', 'exact')
      ) then
        marks_awarded := marks_available;
        is_correct := true;
      end if;

    when 'fill_gap' then
      correct_count := 0;
      total_count := 0;
      accepted_preview := '[]'::jsonb;

      for gap_rule in
        select * from jsonb_array_elements(coalesce(p_runtime_question -> 'autograde_rules' -> 'gaps', '[]'::jsonb))
      loop
        total_count := total_count + 1;
        gap_text := coalesce(student_gaps ->> (gap_rule ->> 'id'), p_student_answer ->> 'text', '');
        accepted_preview := accepted_preview || jsonb_build_array(
          jsonb_build_object(
            'gap_id', gap_rule ->> 'id',
            'accepted', coalesce(gap_rule -> 'accepted', '[]'::jsonb),
            'accepted_groups', coalesce(gap_rule -> 'accepted_groups', '[]'::jsonb)
          )
        );

        matched_group := null;
        if jsonb_typeof(gap_rule -> 'accepted_groups') = 'array'
           and jsonb_array_length(coalesce(gap_rule -> 'accepted_groups', '[]'::jsonb)) > 0 then
          matched_group := public.answer_text_match_group(
            gap_text,
            gap_rule -> 'accepted_groups',
            coalesce(gap_rule ->> 'normalization', 'token'),
            coalesce(gap_rule ->> 'match_mode', 'exact')
          );
        end if;

        if matched_group is not null or public.answer_text_matches(
          gap_text,
          gap_rule -> 'accepted',
          coalesce(gap_rule ->> 'normalization', 'token'),
          coalesce(gap_rule ->> 'match_mode', 'exact')
        ) then
          if require_distinct then
            gap_normalized := coalesce(
              matched_group,
              case coalesce(gap_rule ->> 'normalization', 'token')
                when 'phrase' then public.normalize_answer_phrase(gap_text)
                else public.normalize_answer_token(gap_text)
              end
            );

            if gap_normalized = any(seen_gap_answers) then
              corrections := corrections || jsonb_build_array(
                jsonb_build_object(
                  'gap_id', gap_rule ->> 'id',
                  'message', 'Duplicate answer not allowed',
                  'accepted', coalesce(gap_rule -> 'accepted', '[]'::jsonb),
                  'accepted_groups', coalesce(gap_rule -> 'accepted_groups', '[]'::jsonb)
                )
              );
            else
              seen_gap_answers := array_append(seen_gap_answers, gap_normalized);
              correct_count := correct_count + 1;
            end if;
          else
            correct_count := correct_count + 1;
          end if;
        else
          corrections := corrections || jsonb_build_array(
            jsonb_build_object(
              'gap_id', gap_rule ->> 'id',
              'accepted', coalesce(gap_rule -> 'accepted', '[]'::jsonb),
              'accepted_groups', coalesce(gap_rule -> 'accepted_groups', '[]'::jsonb)
            )
          );
        end if;
      end loop;

      if total_count > 0 then
        if correct_count = total_count then
          marks_awarded := marks_available;
          is_correct := true;
        elsif correct_count > 0 then
          partial_marks := floor((correct_count::numeric / total_count::numeric) * marks_available::numeric);
          marks_awarded := greatest(0, partial_marks);
        end if;
      end if;

    when 'match_table' then
      correct_count := 0;
      total_count := 0;

      for row_rule in
        select * from jsonb_array_elements(coalesce(p_runtime_question -> 'autograde_rules' -> 'pairs', '[]'::jsonb))
      loop
        total_count := total_count + 1;
        selected_text := coalesce(selected_pairs ->> (row_rule ->> 'row_id'), '');
        if selected_text = coalesce(row_rule ->> 'choice_id', '') then
          correct_count := correct_count + 1;
        else
          corrections := corrections || jsonb_build_array(
            jsonb_build_object(
              'row_id', row_rule ->> 'row_id',
              'expected_choice_id', row_rule ->> 'choice_id',
              'selected_choice_id', selected_text
            )
          );
        end if;
      end loop;

      if total_count > 0 then
        if correct_count = total_count then
          marks_awarded := marks_available;
          is_correct := true;
        elsif correct_count > 0 then
          partial_marks := floor((correct_count::numeric / total_count::numeric) * marks_available::numeric);
          marks_awarded := greatest(0, partial_marks);
        end if;
      end if;

    when 'multi_select' then
      student_choice_ids := array(
        select jsonb_array_elements_text(coalesce(p_student_answer -> 'choice_ids', '[]'::jsonb)) order by 1
      );
      expected_choice_ids := array(
        select jsonb_array_elements_text(coalesce(p_runtime_question -> 'autograde_rules' -> 'correct_choice_ids', '[]'::jsonb)) order by 1
      );

      if student_choice_ids = expected_choice_ids then
        marks_awarded := marks_available;
        is_correct := true;
      else
        corrections := jsonb_build_array(
          jsonb_build_object('expected_choice_ids', coalesce(p_runtime_question -> 'autograde_rules' -> 'correct_choice_ids', '[]'::jsonb))
        );
      end if;

    when 'ordering' then
      student_order_ids := array(
        select jsonb_array_elements_text(coalesce(p_student_answer -> 'order_ids', '[]'::jsonb))
      );
      expected_order_ids := array(
        select jsonb_array_elements_text(coalesce(p_runtime_question -> 'autograde_rules' -> 'correct_item_ids', '[]'::jsonb))
      );

      if student_order_ids = expected_order_ids then
        marks_awarded := marks_available;
        is_correct := true;
      else
        corrections := jsonb_build_array(
          jsonb_build_object('expected_order_ids', coalesce(p_runtime_question -> 'autograde_rules' -> 'correct_item_ids', '[]'::jsonb))
        );
      end if;

    else
      corrections := jsonb_build_array(
        jsonb_build_object('message', 'Unsupported grading contract', 'kind', autograde_kind, 'response_kind', response_kind)
      );
  end case;

  if is_correct then
    result_text := 'correct';
    feedback_summary := 'Correct';
  elsif marks_awarded > 0 then
    result_text := 'partial';
    feedback_summary := 'Partly correct';
  end if;

  return jsonb_build_object(
    'result', result_text,
    'is_correct', is_correct,
    'marks_awarded', marks_awarded,
    'marks_available', marks_available,
    'feedback', jsonb_build_object(
      'summary', feedback_summary,
      'corrections', corrections,
      'accepted_answer_preview', accepted_preview
    )
  );
end;
$$;

create or replace function public.get_session_state_v2(
  p_session_id uuid,
  p_student_id uuid
)
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  session_record public.sessions%rowtype;
  questions_payload jsonb := '[]'::jsonb;
begin
  if not public.owns_student_account(p_student_id)
     and not public.is_admin(auth.uid()) then
    raise exception 'Not allowed';
  end if;

  select *
  into session_record
  from public.sessions s
  where s.id = p_session_id
    and s.student_id = p_student_id;

  if not found then
    raise exception 'Session not found';
  end if;

  select coalesce(
    jsonb_agg(
      sq.question_snapshot_json
      || jsonb_build_object(
        'session_item_id', sq.id::text,
        'position', sq.position,
        'grading_status', sq.grading_status,
        'student_answer', sq.student_answer_json,
        'is_correct', case when sq.grading_status = 'graded' then sq.is_correct else null end,
        'marks_awarded', sq.marks_awarded,
        'marks_available', sq.marks_available,
        'feedback', sq.grading_feedback_json
      )
      order by sq.position asc
    ),
    '[]'::jsonb
  )
  into questions_payload
  from public.session_questions sq
  where sq.session_id = session_record.id;

  return jsonb_build_object(
    'session_id', session_record.id,
    'topic_id', session_record.topic_id,
    'difficulty', session_record.difficulty,
    'academic_year_id', session_record.academic_year_id,
    'started_at', session_record.started_at,
    'completed_at', session_record.completed_at,
    'questions', questions_payload
  );
end;
$$;

create or replace function public.start_session_v2(
  p_student_id uuid,
  p_academic_year_id uuid,
  p_topic_id uuid,
  p_difficulty public.difficulty_level,
  p_local_date date,
  p_count integer default 10,
  p_recency_buffer integer default 30
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  target_session_id uuid;
  picked_question public.questions%rowtype;
  inserted_session_question_id uuid;
  runtime_payload jsonb;
  can_start boolean;
  existing_rows integer := 0;
  position_counter integer := 0;
begin
  if not public.owns_student_account(p_student_id) then
    raise exception 'Not allowed';
  end if;

  select s.id
  into target_session_id
  from public.sessions s
  where s.student_id = p_student_id
    and s.academic_year_id = p_academic_year_id
    and s.topic_id = p_topic_id
    and s.difficulty = p_difficulty
    and s.completed_at is null
  order by s.started_at desc
  limit 1;

  if target_session_id is not null then
    select count(*)
    into existing_rows
    from public.session_questions sq
    where sq.session_id = target_session_id;

    if existing_rows > 0 then
      return public.get_session_state_v2(target_session_id, p_student_id)
        || jsonb_build_object('session_status', 'resumed');
    end if;
  end if;

  can_start := public.can_start_session(
    p_student_id,
    p_academic_year_id,
    p_difficulty,
    p_local_date,
    3
  );

  if not can_start then
    raise exception 'Difficulty locked for today';
  end if;

  if target_session_id is null then
    insert into public.sessions (
      student_id,
      academic_year_id,
      topic_id,
      difficulty,
      started_at
    )
    values (
      p_student_id,
      p_academic_year_id,
      p_topic_id,
      p_difficulty,
      timezone('utc'::text, now())
    )
    returning id into target_session_id;
  end if;

  for picked_question in
    select *
    from public.pick_session_questions(
      p_student_id,
      p_topic_id,
      p_difficulty,
      p_count,
      p_recency_buffer
    )
  loop
    position_counter := position_counter + 1;

    insert into public.session_questions (
      session_id,
      question_id,
      position,
      student_answer_json,
      is_correct,
      response_time_ms,
      hint_used,
      grading_status,
      question_snapshot_json,
      objective_ids_json,
      marks_available,
      marks_awarded,
      grading_feedback_json
    )
    values (
      target_session_id,
      picked_question.id,
      position_counter,
      '{}'::jsonb,
      false,
      0,
      false,
      'pending',
      '{}'::jsonb,
      '[]'::jsonb,
      coalesce(picked_question.max_marks, 1),
      0,
      '{}'::jsonb
    )
    returning id into inserted_session_question_id;

    runtime_payload := public.build_runtime_question_payload(
      picked_question.id,
      inserted_session_question_id
    );

    update public.session_questions
    set question_snapshot_json = runtime_payload,
        objective_ids_json = coalesce(runtime_payload -> 'objective_ids', '[]'::jsonb),
        marks_available = greatest(1, coalesce((runtime_payload ->> 'max_marks')::smallint, 1))
    where id = inserted_session_question_id;
  end loop;

  if position_counter = 0 then
    raise exception 'No questions are available for this topic and difficulty';
  end if;

  return public.get_session_state_v2(target_session_id, p_student_id)
    || jsonb_build_object('session_status', 'started');
end;
$$;

create or replace function public.grade_session_question_v2(
  p_session_id uuid,
  p_student_id uuid,
  p_session_question_id uuid,
  p_student_answer jsonb,
  p_response_time_ms integer default 0,
  p_hint_used boolean default false
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  session_question_record public.session_questions%rowtype;
  grading_result jsonb;
begin
  if not public.owns_student_account(p_student_id) then
    raise exception 'Not allowed';
  end if;

  select sq.*
  into session_question_record
  from public.session_questions sq
  join public.sessions s on s.id = sq.session_id
  where sq.id = p_session_question_id
    and sq.session_id = p_session_id
    and s.student_id = p_student_id
    and s.completed_at is null;

  if not found then
    raise exception 'Session question not found or session already completed';
  end if;

  grading_result := public.grade_runtime_question(
    session_question_record.question_snapshot_json,
    coalesce(p_student_answer, '{}'::jsonb)
  );

  update public.session_questions
  set student_answer_json = coalesce(p_student_answer, '{}'::jsonb),
      is_correct = coalesce((grading_result ->> 'is_correct')::boolean, false),
      response_time_ms = greatest(0, coalesce(p_response_time_ms, 0)),
      hint_used = coalesce(p_hint_used, false),
      marks_awarded = greatest(0, coalesce((grading_result ->> 'marks_awarded')::smallint, 0)),
      marks_available = greatest(1, coalesce((grading_result ->> 'marks_available')::smallint, session_question_record.marks_available, 1)),
      grading_status = 'graded',
      answered_at = timezone('utc'::text, now()),
      graded_at = timezone('utc'::text, now()),
      grading_feedback_json = coalesce(grading_result -> 'feedback', '{}'::jsonb)
  where id = session_question_record.id;

  return jsonb_build_object(
    'session_question_id', session_question_record.id,
    'grading', grading_result,
    'explanation', session_question_record.question_snapshot_json ->> 'explanation'
  );
end;
$$;

create or replace function public.complete_session_v2(
  p_session_id uuid,
  p_student_id uuid,
  p_academic_year_id uuid,
  p_local_date date
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  session_record public.sessions%rowtype;
  total_items integer := 0;
  graded_items integer := 0;
  earned_points integer := 0;
  available_points integer := 0;
  accuracy_value numeric(6,2) := 0;
  current_streak integer := 0;
  previous_accuracy numeric;
begin
  if not public.owns_student_account(p_student_id) then
    raise exception 'Not allowed';
  end if;

  select *
  into session_record
  from public.sessions s
  where s.id = p_session_id
    and s.student_id = p_student_id
    and s.academic_year_id = p_academic_year_id
    and s.completed_at is null;

  if not found then
    raise exception 'Session not found or already completed';
  end if;

  select
    count(*),
    count(*) filter (where sq.grading_status = 'graded'),
    coalesce(sum(sq.marks_awarded), 0),
    coalesce(sum(sq.marks_available), 0)
  into total_items, graded_items, earned_points, available_points
  from public.session_questions sq
  where sq.session_id = session_record.id;

  if total_items = 0 then
    raise exception 'Session has no planned questions';
  end if;

  if graded_items <> total_items then
    raise exception 'Session is not fully graded';
  end if;

  if available_points > 0 then
    accuracy_value := round((earned_points::numeric / available_points::numeric) * 100, 2);
  else
    accuracy_value := 0;
  end if;

  for previous_accuracy in
    select s.accuracy_pct
    from public.sessions s
    where s.student_id = p_student_id
      and s.academic_year_id = p_academic_year_id
      and s.completed_at is not null
    order by s.completed_at asc
  loop
    if coalesce(previous_accuracy, 0) >= 60 then
      current_streak := current_streak + 1;
    else
      current_streak := 0;
    end if;
  end loop;

  if accuracy_value >= 60 then
    current_streak := current_streak + 1;
  else
    current_streak := 0;
  end if;

  update public.sessions
  set completed_at = timezone('utc'::text, now()),
      score = earned_points,
      accuracy_pct = accuracy_value,
      points_earned = earned_points,
      points_available = available_points,
      streak_after = current_streak
  where id = session_record.id;

  insert into public.daily_caps (
    student_id,
    academic_year_id,
    difficulty,
    local_date,
    sessions_completed
  )
  values (
    session_record.student_id,
    session_record.academic_year_id,
    session_record.difficulty,
    p_local_date,
    1
  )
  on conflict (student_id, academic_year_id, difficulty, local_date)
  do update set sessions_completed = public.daily_caps.sessions_completed + 1;

  return jsonb_build_object(
    'session_id', session_record.id,
    'score', earned_points,
    'points_earned', earned_points,
    'points_available', available_points,
    'accuracy_pct', accuracy_value,
    'streak_after', current_streak,
    'completed_at', timezone('utc'::text, now())
  );
end;
$$;

grant execute on function public.normalize_answer_token(text) to authenticated;
grant execute on function public.normalize_answer_phrase(text) to authenticated;
grant execute on function public.answer_text_matches(text, jsonb, text, text) to authenticated;
grant execute on function public.build_runtime_question_payload(uuid, uuid) to authenticated;
grant execute on function public.grade_runtime_question(jsonb, jsonb) to authenticated;
grant execute on function public.get_session_state_v2(uuid, uuid) to authenticated;
grant execute on function public.start_session_v2(uuid, uuid, uuid, public.difficulty_level, date, integer, integer) to authenticated;
grant execute on function public.grade_session_question_v2(uuid, uuid, uuid, jsonb, integer, boolean) to authenticated;
grant execute on function public.complete_session_v2(uuid, uuid, uuid, date) to authenticated;
