-- Ensure expert sessions always include at least one diagram question when available,
-- while still preventing repeated diagram families in a single session.

create or replace function public.pick_session_questions(
  p_student_id uuid,
  p_topic_id uuid,
  p_difficulty public.difficulty_level,
  p_count integer,
  p_recency_buffer integer default 30
)
returns setof public.questions
language plpgsql
stable
set search_path = public
as $$
begin
  if not exists (
    select 1
    from public.student_accounts sa
    where sa.id = p_student_id
      and sa.auth_user_id = auth.uid()
  ) and not public.is_admin(auth.uid()) then
    raise exception 'Not allowed';
  end if;

  return query
  with recent as (
    select sq.question_id
    from public.session_questions sq
    join public.sessions s on s.id = sq.session_id
    where s.student_id = p_student_id
      and s.topic_id = p_topic_id
      and s.difficulty = p_difficulty
      and s.completed_at is not null
    order by s.completed_at desc
    limit p_recency_buffer
  ),
  eligible as (
    select
      q.*,
      case
        when q.format = 'diagram_label'::public.question_format
          then coalesce(nullif(q.options_json ->> 'diagram_key', ''), q.id::text)
        else q.id::text
      end as selection_group
    from public.questions q
    where q.topic_id = p_topic_id
      and q.difficulty = p_difficulty
      and q.is_active = true
      and q.qa_status in ('reviewed', 'published')
      and q.id not in (select question_id from recent)
  ),
  grouped as (
    select distinct on (selection_group) id, format
    from eligible
    order by selection_group, random()
  ),
  forced_diagram as (
    select g.id
    from grouped g
    where p_difficulty = 'expert'::public.difficulty_level
      and g.format = 'diagram_label'::public.question_format
    order by random()
    limit 1
  ),
  remaining as (
    select g.id
    from grouped g
    where g.id not in (select id from forced_diagram)
    order by random()
    limit greatest(
      p_count - (
        case
          when p_difficulty = 'expert'::public.difficulty_level
            and exists (select 1 from forced_diagram)
          then 1
          else 0
        end
      ),
      0
    )
  ),
  picked as (
    select id from forced_diagram
    union all
    select id from remaining
  )
  select q.*
  from picked p
  join public.questions q on q.id = p.id
  order by random()
  limit p_count;
end;
$$;
