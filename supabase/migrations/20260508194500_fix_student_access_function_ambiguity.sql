-- Fix ambiguous column references in the student access summary function.
-- PL/pgSQL exposes return column names as variables, so internal query names must avoid collisions.

create or replace function public.get_student_access_past_week(
  p_academic_year_id uuid default null,
  p_days integer default 7,
  p_timezone text default 'Europe/London'
)
returns table (
  local_date date,
  usernames text[],
  student_count integer,
  login_events integer,
  session_starts integer,
  latest_activity_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
declare
  days_count integer := least(greatest(coalesce(p_days, 7), 1), 31);
  timezone_name text := coalesce(nullif(btrim(p_timezone), ''), 'Europe/London');
  today_local date;
begin
  if not public.is_admin(auth.uid()) then
    raise exception 'Only admins can view student access summaries.';
  end if;

  begin
    today_local := (timezone(timezone_name, now()))::date;
  exception when others then
    timezone_name := 'Europe/London';
    today_local := (timezone(timezone_name, now()))::date;
  end;

  return query
  with report_days as (
    select generate_series(today_local - (days_count - 1), today_local, interval '1 day')::date as access_date
  ),
  login_rows as (
    select
      e.local_date as access_date,
      sa.username as username,
      e.login_count as login_count,
      e.last_logged_in_at as last_logged_in_at
    from public.student_login_events e
    join public.student_accounts sa on sa.id = e.student_id
    where e.local_date between today_local - (days_count - 1) and today_local
  ),
  session_rows as (
    select
      (timezone(timezone_name, s.started_at))::date as access_date,
      sa.username as username,
      s.started_at as started_at
    from public.sessions s
    join public.student_accounts sa on sa.id = s.student_id
    where (p_academic_year_id is null or s.academic_year_id = p_academic_year_id)
      and (timezone(timezone_name, s.started_at))::date between today_local - (days_count - 1) and today_local
  ),
  day_users as (
    select lr.access_date, lr.username from login_rows lr
    union
    select sr.access_date, sr.username from session_rows sr
  ),
  login_summary as (
    select
      lr.access_date,
      coalesce(sum(lr.login_count), 0)::integer as login_events_total,
      max(lr.last_logged_in_at) as latest_login_at
    from login_rows lr
    group by lr.access_date
  ),
  session_summary as (
    select
      sr.access_date,
      count(*)::integer as session_starts_total,
      max(sr.started_at) as latest_session_at
    from session_rows sr
    group by sr.access_date
  )
  select
    rd.access_date as local_date,
    coalesce(
      array_agg(du.username order by du.username) filter (where du.username is not null),
      '{}'::text[]
    ) as usernames,
    count(du.username)::integer as student_count,
    coalesce(ls.login_events_total, 0)::integer as login_events,
    coalesce(ss.session_starts_total, 0)::integer as session_starts,
    case
      when ls.latest_login_at is null then ss.latest_session_at
      when ss.latest_session_at is null then ls.latest_login_at
      else greatest(ls.latest_login_at, ss.latest_session_at)
    end as latest_activity_at
  from report_days rd
  left join day_users du on du.access_date = rd.access_date
  left join login_summary ls on ls.access_date = rd.access_date
  left join session_summary ss on ss.access_date = rd.access_date
  group by
    rd.access_date,
    ls.login_events_total,
    ls.latest_login_at,
    ss.session_starts_total,
    ss.latest_session_at
  order by rd.access_date desc;
end;
$$;

grant execute on function public.get_student_access_past_week(uuid, integer, text) to authenticated;
