-- Initial schema for S1 Network Technologies Revision App

create extension if not exists pgcrypto;

create type public.app_role as enum ('student', 'admin');
create type public.difficulty_level as enum ('easy', 'medium', 'expert');
create type public.question_format as enum (
  'mcq',
  'drag_drop',
  'match_table',
  'fill_gap',
  'short_text',
  'structured_response',
  'diagram_label'
);
create type public.question_source as enum ('adapted_exam', 'new_original');

create table public.academic_years (
  id uuid primary key default gen_random_uuid(),
  code text not null unique check (code ~ '^[0-9]{2}-[0-9]{2}$'),
  is_active boolean not null default false,
  timezone text not null default 'Europe/London',
  created_at timestamptz not null default timezone('utc'::text, now()),
  updated_at timestamptz not null default timezone('utc'::text, now())
);

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  role public.app_role not null,
  display_name text,
  is_active boolean not null default true,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table public.student_accounts (
  id uuid primary key default gen_random_uuid(),
  auth_user_id uuid not null unique references auth.users(id) on delete cascade,
  username text not null unique check (username ~ '^s1dt[0-9]{3}$'),
  account_number integer not null unique check (account_number between 1 and 100),
  is_active boolean not null default true,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table public.topics (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  is_enabled boolean not null default false,
  display_order integer not null,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table public.questions (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid not null references public.topics(id) on delete cascade,
  difficulty public.difficulty_level not null,
  format public.question_format not null,
  stem text not null,
  options_json jsonb,
  correct_answer_json jsonb not null,
  markscheme_points_json jsonb not null default '[]'::jsonb,
  explanation text not null,
  source_type public.question_source not null,
  source_ref text not null,
  tags_json jsonb not null default '[]'::jsonb,
  qa_status text not null default 'draft' check (qa_status in ('draft', 'reviewed', 'published')),
  reviewed_by uuid references public.profiles(id),
  reviewed_at timestamptz,
  is_active boolean not null default true,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table public.sessions (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.student_accounts(id) on delete cascade,
  academic_year_id uuid not null references public.academic_years(id) on delete cascade,
  topic_id uuid not null references public.topics(id) on delete cascade,
  difficulty public.difficulty_level not null,
  started_at timestamptz not null,
  completed_at timestamptz,
  score numeric(6,2),
  accuracy_pct numeric(6,2),
  points_earned integer,
  streak_after integer,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table public.session_questions (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.sessions(id) on delete cascade,
  question_id uuid not null references public.questions(id) on delete restrict,
  position integer not null,
  student_answer_json jsonb not null,
  is_correct boolean not null,
  response_time_ms integer not null,
  hint_used boolean not null default false,
  created_at timestamptz not null default timezone('utc'::text, now()),
  unique (session_id, position)
);

create table public.daily_caps (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.student_accounts(id) on delete cascade,
  academic_year_id uuid not null references public.academic_years(id) on delete cascade,
  difficulty public.difficulty_level not null,
  local_date date not null,
  sessions_completed integer not null default 0,
  created_at timestamptz not null default timezone('utc'::text, now()),
  unique (student_id, academic_year_id, difficulty, local_date)
);

create table public.achievements (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  title text not null,
  description text not null,
  icon text not null,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table public.student_achievements (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.student_accounts(id) on delete cascade,
  achievement_id uuid not null references public.achievements(id) on delete cascade,
  awarded_at timestamptz not null default timezone('utc'::text, now()),
  unique (student_id, achievement_id)
);

create table public.admin_events (
  id uuid primary key default gen_random_uuid(),
  admin_id uuid not null references public.profiles(id) on delete cascade,
  event_type text not null,
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create index idx_questions_topic_difficulty on public.questions(topic_id, difficulty);
create index idx_sessions_student_year on public.sessions(student_id, academic_year_id);
create index idx_sessions_topic_difficulty on public.sessions(topic_id, difficulty);
create index idx_session_questions_session on public.session_questions(session_id);
create index idx_daily_caps_lookup on public.daily_caps(student_id, academic_year_id, difficulty, local_date);

create function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, role, display_name)
  values (
    new.id,
    coalesce((new.raw_user_meta_data ->> 'role')::public.app_role, 'student'::public.app_role),
    coalesce(new.raw_user_meta_data ->> 'display_name', split_part(new.email, '@', 1))
  )
  on conflict (id) do nothing;

  return new;
end;
$$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_auth_user();

create function public.is_admin(p_user_id uuid default auth.uid())
returns boolean
language sql
stable
set search_path = public
as $$
  select exists (
    select 1
    from public.profiles
    where id = p_user_id
      and role = 'admin'::public.app_role
      and is_active = true
  );
$$;

create function public.owns_student_account(p_student_id uuid)
returns boolean
language sql
stable
set search_path = public
as $$
  select exists (
    select 1
    from public.student_accounts sa
    where sa.id = p_student_id
      and sa.auth_user_id = auth.uid()
      and sa.is_active = true
  );
$$;

create function public.set_active_academic_year(p_year_id uuid)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.is_admin(auth.uid()) then
    raise exception 'Admin access required';
  end if;

  update public.academic_years
  set is_active = false,
      updated_at = timezone('utc'::text, now());

  update public.academic_years
  set is_active = true,
      updated_at = timezone('utc'::text, now())
  where id = p_year_id;
end;
$$;

create function public.can_start_session(
  p_student_id uuid,
  p_academic_year_id uuid,
  p_difficulty public.difficulty_level,
  p_local_date date,
  p_max_sessions integer default 3
)
returns boolean
language plpgsql
stable
set search_path = public
as $$
declare
  completed_count integer;
begin
  if not public.owns_student_account(p_student_id) then
    return false;
  end if;

  select coalesce(dc.sessions_completed, 0)
  into completed_count
  from public.daily_caps dc
  where dc.student_id = p_student_id
    and dc.academic_year_id = p_academic_year_id
    and dc.difficulty = p_difficulty
    and dc.local_date = p_local_date;

  return coalesce(completed_count, 0) < p_max_sessions;
end;
$$;

create function public.pick_session_questions(
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
  )
  select q.*
  from public.questions q
  where q.topic_id = p_topic_id
    and q.difficulty = p_difficulty
    and q.is_active = true
    and q.qa_status in ('reviewed', 'published')
    and q.id not in (select question_id from recent)
  order by random()
  limit p_count;
end;
$$;

create function public.save_session_submission(
  p_session_id uuid,
  p_student_id uuid,
  p_academic_year_id uuid,
  p_local_date date,
  p_answers jsonb,
  p_accuracy_pct numeric,
  p_score numeric,
  p_points_earned integer,
  p_streak_after integer
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  item jsonb;
  answer_question_id uuid;
  answer_position integer;
  answer_json jsonb;
  answer_correct boolean;
  answer_response_time integer;
  answer_hint_used boolean;
  session_exists boolean;
begin
  if not public.owns_student_account(p_student_id) then
    raise exception 'Not allowed';
  end if;

  select exists (
    select 1
    from public.sessions s
    where s.id = p_session_id
      and s.student_id = p_student_id
      and s.completed_at is null
  ) into session_exists;

  if not session_exists then
    raise exception 'Session not found or already completed';
  end if;

  for item in select * from jsonb_array_elements(p_answers)
  loop
    answer_question_id := (item ->> 'questionId')::uuid;
    answer_position := (item ->> 'position')::integer;
    answer_json := (item -> 'answer');
    answer_correct := (item ->> 'isCorrect')::boolean;
    answer_response_time := (item ->> 'responseTimeMs')::integer;
    answer_hint_used := coalesce((item ->> 'hintUsed')::boolean, false);

    insert into public.session_questions (
      session_id,
      question_id,
      position,
      student_answer_json,
      is_correct,
      response_time_ms,
      hint_used
    )
    values (
      p_session_id,
      answer_question_id,
      answer_position,
      coalesce(answer_json, '{}'::jsonb),
      coalesce(answer_correct, false),
      coalesce(answer_response_time, 0),
      answer_hint_used
    )
    on conflict (session_id, position) do update
      set student_answer_json = excluded.student_answer_json,
          is_correct = excluded.is_correct,
          response_time_ms = excluded.response_time_ms,
          hint_used = excluded.hint_used;
  end loop;

  update public.sessions
  set completed_at = timezone('utc'::text, now()),
      score = p_score,
      accuracy_pct = p_accuracy_pct,
      points_earned = p_points_earned,
      streak_after = p_streak_after
  where id = p_session_id
    and student_id = p_student_id;

  insert into public.daily_caps (
    student_id,
    academic_year_id,
    difficulty,
    local_date,
    sessions_completed
  )
  select s.student_id, s.academic_year_id, s.difficulty, p_local_date, 1
  from public.sessions s
  where s.id = p_session_id
  on conflict (student_id, academic_year_id, difficulty, local_date)
  do update set sessions_completed = public.daily_caps.sessions_completed + 1;
end;
$$;

-- Row Level Security
alter table public.academic_years enable row level security;
alter table public.profiles enable row level security;
alter table public.student_accounts enable row level security;
alter table public.topics enable row level security;
alter table public.questions enable row level security;
alter table public.sessions enable row level security;
alter table public.session_questions enable row level security;
alter table public.daily_caps enable row level security;
alter table public.achievements enable row level security;
alter table public.student_achievements enable row level security;
alter table public.admin_events enable row level security;

create policy academic_years_read_all
on public.academic_years for select
using (auth.role() = 'authenticated');

create policy academic_years_admin_write
on public.academic_years for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy profiles_self_read
on public.profiles for select
using (id = auth.uid() or public.is_admin(auth.uid()));

create policy profiles_admin_update
on public.profiles for update
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy student_accounts_self_read
on public.student_accounts for select
using (auth_user_id = auth.uid() or public.is_admin(auth.uid()));

create policy student_accounts_admin_write
on public.student_accounts for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy topics_read_all
on public.topics for select
using (auth.role() = 'authenticated');

create policy topics_admin_write
on public.topics for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy questions_read_all
on public.questions for select
using (auth.role() = 'authenticated' and (is_active = true or public.is_admin(auth.uid())));

create policy questions_admin_write
on public.questions for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy sessions_student_read
on public.sessions for select
using (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.student_accounts sa
    where sa.id = sessions.student_id
      and sa.auth_user_id = auth.uid()
  )
);

create policy sessions_student_insert
on public.sessions for insert
with check (
  exists (
    select 1
    from public.student_accounts sa
    where sa.id = sessions.student_id
      and sa.auth_user_id = auth.uid()
  )
);

create policy sessions_student_update
on public.sessions for update
using (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.student_accounts sa
    where sa.id = sessions.student_id
      and sa.auth_user_id = auth.uid()
  )
)
with check (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.student_accounts sa
    where sa.id = sessions.student_id
      and sa.auth_user_id = auth.uid()
  )
);

create policy session_questions_student_read
on public.session_questions for select
using (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.sessions s
    join public.student_accounts sa on sa.id = s.student_id
    where s.id = session_questions.session_id
      and sa.auth_user_id = auth.uid()
  )
);

create policy session_questions_student_insert
on public.session_questions for insert
with check (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.sessions s
    join public.student_accounts sa on sa.id = s.student_id
    where s.id = session_questions.session_id
      and sa.auth_user_id = auth.uid()
  )
);

create policy daily_caps_student_read
on public.daily_caps for select
using (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.student_accounts sa
    where sa.id = daily_caps.student_id
      and sa.auth_user_id = auth.uid()
  )
);

create policy daily_caps_admin_write
on public.daily_caps for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy achievements_read_all
on public.achievements for select
using (auth.role() = 'authenticated');

create policy achievements_admin_write
on public.achievements for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy student_achievements_read
on public.student_achievements for select
using (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.student_accounts sa
    where sa.id = student_achievements.student_id
      and sa.auth_user_id = auth.uid()
  )
);

create policy student_achievements_admin_write
on public.student_achievements for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy admin_events_admin_only
on public.admin_events for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

grant usage on schema public to anon, authenticated;
grant select on public.topics, public.questions, public.academic_years, public.achievements to authenticated;
grant select, insert, update on public.sessions, public.session_questions, public.daily_caps to authenticated;
grant select on public.student_accounts, public.student_achievements, public.profiles to authenticated;
grant execute on function public.set_active_academic_year(uuid) to authenticated;
grant execute on function public.can_start_session(uuid, uuid, public.difficulty_level, date, integer) to authenticated;
grant execute on function public.pick_session_questions(uuid, uuid, public.difficulty_level, integer, integer) to authenticated;
grant execute on function public.save_session_submission(uuid, uuid, uuid, date, jsonb, numeric, numeric, integer, integer) to authenticated;

insert into public.academic_years (code, is_active, timezone)
values ('25-26', true, 'Europe/London')
on conflict (code) do nothing;

insert into public.topics (slug, title, is_enabled, display_order)
values
  ('digital-data', 'Digital Data', false, 1),
  ('software-applications', 'Software Applications', false, 2),
  ('computer-hardware', 'Computer Hardware', false, 3),
  ('network-technologies', 'Network Technologies', true, 4),
  ('cyberspace-security', 'Cyberspace, Security & Data Transfer', false, 5),
  ('cloud-technology', 'Cloud Technology', false, 6),
  ('legislation-impact', 'Legislation, Ethical and Social Impact', false, 7)
on conflict (slug) do update
set title = excluded.title,
    display_order = excluded.display_order;

insert into public.achievements (code, title, description, icon)
values
  ('streak_3', 'Momentum Builder', 'Complete 3 sessions in a row at 60%+ accuracy.', 'fire'),
  ('streak_5', 'Consistency Champion', 'Complete 5 sessions in a row at 60%+ accuracy.', 'star'),
  ('expert_clear', 'Expert Explorer', 'Complete an Expert session with 70%+.', 'compass')
on conflict (code) do nothing;
