-- Provide the admin dashboard with a reliable past-week student access view.
-- It combines explicit login records with revision-session starts, so activity still appears
-- when students had a saved session or when login tracking was added after they began using the app.

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
  with days as (
    select generate_series(today_local - (days_count - 1), today_local, interval '1 day')::date as day
  ),
  login_rows as (
    select
      e.local_date,
      sa.username,
      e.login_count,
      e.last_logged_in_at
    from public.student_login_events e
    join public.student_accounts sa on sa.id = e.student_id
    where e.local_date between today_local - (days_count - 1) and today_local
  ),
  session_rows as (
    select
      (timezone(timezone_name, s.started_at))::date as local_date,
      sa.username,
      s.started_at
    from public.sessions s
    join public.student_accounts sa on sa.id = s.student_id
    where (p_academic_year_id is null or s.academic_year_id = p_academic_year_id)
      and (timezone(timezone_name, s.started_at))::date between today_local - (days_count - 1) and today_local
  ),
  day_users as (
    select local_date, username from login_rows
    union
    select local_date, username from session_rows
  ),
  login_summary as (
    select
      local_date,
      coalesce(sum(login_count), 0)::integer as login_events,
      max(last_logged_in_at) as latest_login_at
    from login_rows
    group by local_date
  ),
  session_summary as (
    select
      local_date,
      count(*)::integer as session_starts,
      max(started_at) as latest_session_at
    from session_rows
    group by local_date
  )
  select
    days.day as local_date,
    coalesce(
      array_agg(day_users.username order by day_users.username) filter (where day_users.username is not null),
      '{}'::text[]
    ) as usernames,
    count(day_users.username)::integer as student_count,
    coalesce(login_summary.login_events, 0)::integer as login_events,
    coalesce(session_summary.session_starts, 0)::integer as session_starts,
    case
      when login_summary.latest_login_at is null then session_summary.latest_session_at
      when session_summary.latest_session_at is null then login_summary.latest_login_at
      else greatest(login_summary.latest_login_at, session_summary.latest_session_at)
    end as latest_activity_at
  from days
  left join day_users on day_users.local_date = days.day
  left join login_summary on login_summary.local_date = days.day
  left join session_summary on session_summary.local_date = days.day
  group by
    days.day,
    login_summary.login_events,
    login_summary.latest_login_at,
    session_summary.session_starts,
    session_summary.latest_session_at
  order by days.day desc;
end;
$$;

grant execute on function public.get_student_access_past_week(uuid, integer, text) to authenticated;
