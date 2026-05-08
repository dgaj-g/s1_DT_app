-- Track distinct student logins by local date for the admin dashboard.
-- This records usernames only through the student_accounts table; no student names are stored.

create table if not exists public.student_login_events (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.student_accounts(id) on delete cascade,
  auth_user_id uuid not null references auth.users(id) on delete cascade,
  local_date date not null,
  timezone text not null default 'Europe/London',
  first_logged_in_at timestamptz not null default timezone('utc'::text, now()),
  last_logged_in_at timestamptz not null default timezone('utc'::text, now()),
  login_count integer not null default 1 check (login_count > 0),
  created_at timestamptz not null default timezone('utc'::text, now()),
  unique (student_id, local_date)
);

create index if not exists idx_student_login_events_local_date
  on public.student_login_events(local_date desc, student_id);

create index if not exists idx_student_login_events_student_date
  on public.student_login_events(student_id, local_date desc);

alter table public.student_login_events enable row level security;

drop policy if exists student_login_events_admin_select on public.student_login_events;
create policy student_login_events_admin_select
on public.student_login_events for select
using (public.is_admin(auth.uid()));

drop policy if exists student_login_events_student_self_select on public.student_login_events;
create policy student_login_events_student_self_select
on public.student_login_events for select
using (
  exists (
    select 1
    from public.student_accounts sa
    where sa.id = student_login_events.student_id
      and sa.auth_user_id = auth.uid()
  )
);

create or replace function public.record_student_login(p_timezone text default 'Europe/London')
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  current_user_id uuid := auth.uid();
  student_record public.student_accounts%rowtype;
  timezone_name text := coalesce(nullif(btrim(p_timezone), ''), 'Europe/London');
  login_local_date date;
begin
  if current_user_id is null then
    return;
  end if;

  select sa.*
  into student_record
  from public.student_accounts sa
  join public.profiles p on p.id = sa.auth_user_id
  where sa.auth_user_id = current_user_id
    and sa.is_active = true
    and p.role = 'student'::public.app_role
    and p.is_active = true;

  -- Admins and inactive accounts do not create student login rows.
  if not found then
    return;
  end if;

  begin
    login_local_date := (timezone(timezone_name, now()))::date;
  exception when others then
    timezone_name := 'Europe/London';
    login_local_date := (timezone(timezone_name, now()))::date;
  end;

  insert into public.student_login_events (
    student_id,
    auth_user_id,
    local_date,
    timezone,
    first_logged_in_at,
    last_logged_in_at,
    login_count
  ) values (
    student_record.id,
    student_record.auth_user_id,
    login_local_date,
    timezone_name,
    now(),
    now(),
    1
  )
  on conflict (student_id, local_date)
  do update set
    last_logged_in_at = excluded.last_logged_in_at,
    timezone = excluded.timezone,
    login_count = public.student_login_events.login_count + 1;
end;
$$;

create or replace function public.get_student_logins_past_week(
  p_days integer default 7,
  p_timezone text default 'Europe/London'
)
returns table (
  local_date date,
  usernames text[],
  student_count integer,
  login_events integer,
  latest_login_at timestamptz
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
    raise exception 'Only admins can view student login summaries.';
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
  )
  select
    days.day as local_date,
    coalesce(
      array_agg(sa.username order by sa.account_number) filter (where sa.username is not null),
      '{}'::text[]
    ) as usernames,
    count(sa.id)::integer as student_count,
    coalesce(sum(e.login_count), 0)::integer as login_events,
    max(e.last_logged_in_at) as latest_login_at
  from days
  left join public.student_login_events e on e.local_date = days.day
  left join public.student_accounts sa on sa.id = e.student_id
  group by days.day
  order by days.day desc;
end;
$$;

grant select on public.student_login_events to authenticated;
grant execute on function public.record_student_login(text) to authenticated;
grant execute on function public.get_student_logins_past_week(integer, text) to authenticated;
