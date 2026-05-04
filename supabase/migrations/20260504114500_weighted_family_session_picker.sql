-- Use question families and selection weights when building student sessions.
-- The picker prefers fresh, distinct families first, then relaxes recency/family
-- constraints only when the approved/live bucket is too thin to fill a session.

create or replace function public.pick_session_questions(
  p_student_id uuid,
  p_topic_id uuid,
  p_difficulty public.difficulty_level,
  p_count integer,
  p_recency_buffer integer default 30
)
returns setof public.questions
language plpgsql
volatile
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
      and sq.question_id is not null
    order by s.completed_at desc
    limit greatest(p_recency_buffer, 0)
  ),
  eligible_all as (
    select
      q.*,
      coalesce(
        nullif(q.question_family_code, ''),
        case
          when q.format = 'diagram_label'::public.question_format
            then coalesce(nullif(q.options_json ->> 'diagram_key', ''), q.id::text)
          else q.id::text
        end
      ) as session_family_key,
      (
        -ln(greatest(random(), 0.0000000001))
        / greatest(coalesce(q.selection_weight, 1)::double precision, 0.01)
      ) as weighted_pick_key
    from public.questions q
    where q.topic_id = p_topic_id
      and q.difficulty = p_difficulty
      and q.is_active = true
      and q.qa_status in ('reviewed', 'published')
  ),
  eligible_fresh as (
    select e.*
    from eligible_all e
    where e.id not in (select question_id from recent)
  ),
  fresh_family_ranked as (
    select
      e.*,
      row_number() over (
        partition by e.session_family_key
        order by e.weighted_pick_key asc
      ) as family_rank
    from eligible_fresh e
  ),
  fresh_family_candidates as (
    select *
    from fresh_family_ranked
    where family_rank = 1
  ),
  forced_diagram as (
    select f.id
    from fresh_family_candidates f
    where p_difficulty = 'expert'::public.difficulty_level
      and f.format = 'diagram_label'::public.question_format
    order by f.weighted_pick_key asc
    limit 1
  ),
  family_first_pass as (
    select f.id
    from fresh_family_candidates f
    where f.id not in (select id from forced_diagram)
    order by f.weighted_pick_key asc
    limit greatest(
      p_count - (select count(*) from forced_diagram),
      0
    )
  ),
  picked_after_family as (
    select id from forced_diagram
    union all
    select id from family_first_pass
  ),
  fresh_same_family_backfill as (
    select e.id
    from eligible_fresh e
    where e.id not in (select id from picked_after_family)
    order by e.weighted_pick_key asc
    limit greatest(
      p_count - (select count(*) from picked_after_family),
      0
    )
  ),
  picked_after_fresh as (
    select id from picked_after_family
    union all
    select id from fresh_same_family_backfill
  ),
  recency_relaxed_backfill as (
    select e.id
    from eligible_all e
    where e.id not in (select id from picked_after_fresh)
    order by e.weighted_pick_key asc
    limit greatest(
      p_count - (select count(*) from picked_after_fresh),
      0
    )
  ),
  picked as (
    select id from picked_after_fresh
    union all
    select id from recency_relaxed_backfill
  )
  select q.*
  from picked p
  join public.questions q on q.id = p.id
  order by random()
  limit greatest(p_count, 0);
end;
$$;

grant execute on function public.pick_session_questions(
  uuid,
  uuid,
  public.difficulty_level,
  integer,
  integer
) to authenticated;
