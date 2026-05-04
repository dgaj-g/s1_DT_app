-- Stage 3 foundation for the full Unit 1 rebuild.
-- This migration is additive and preparatory:
-- - keep existing credentials and auth model intact
-- - align topics to the new Unit 1 resource pack
-- - support richer questions, assets, objectives, and mastery tracking
-- - future-proof historical attempt storage

alter type public.question_format add value if not exists 'multi_select';

do $$
begin
  if not exists (select 1 from pg_type where typname = 'content_source_kind') then
    create type public.content_source_kind as enum (
      'past_paper',
      'mark_scheme',
      'practice_bank',
      'fact_file',
      'teacher_note'
    );
  end if;

  if not exists (select 1 from pg_type where typname = 'question_asset_kind') then
    create type public.question_asset_kind as enum (
      'diagram',
      'table_image',
      'screenshot',
      'figure',
      'chart',
      'photo'
    );
  end if;

  if not exists (select 1 from pg_type where typname = 'question_asset_role') then
    create type public.question_asset_role as enum (
      'prompt',
      'option',
      'feedback',
      'reference'
    );
  end if;

  if not exists (select 1 from pg_type where typname = 'adaptive_tier') then
    create type public.adaptive_tier as enum (
      'support',
      'core',
      'challenge'
    );
  end if;

  if not exists (select 1 from pg_type where typname = 'import_batch_status') then
    create type public.import_batch_status as enum (
      'draft',
      'uploaded',
      'ready_for_review',
      'approved',
      'applied',
      'cancelled'
    );
  end if;

  if not exists (select 1 from pg_type where typname = 'staged_question_status') then
    create type public.staged_question_status as enum (
      'draft',
      'ready_for_review',
      'approved',
      'rejected',
      'applied'
    );
  end if;

  if not exists (select 1 from pg_type where typname = 'import_source_format') then
    create type public.import_source_format as enum (
      'csv',
      'xlsx',
      'json',
      'manual',
      'docx_assisted',
      'pdf_assisted'
    );
  end if;
end
$$;

alter table public.questions
  add column if not exists max_marks smallint not null default 1 check (max_marks between 1 and 20),
  add column if not exists adaptive_tier public.adaptive_tier not null default 'core',
  add column if not exists question_family_code text,
  add column if not exists selection_weight numeric(6,2) not null default 1 check (selection_weight > 0 and selection_weight <= 100),
  add column if not exists content_blocks_json jsonb not null default '[]'::jsonb,
  add column if not exists response_schema_json jsonb not null default '{}'::jsonb,
  add column if not exists autograde_rules_json jsonb not null default '{}'::jsonb,
  add column if not exists teacher_notes text;

alter table public.sessions
  add column if not exists points_available integer;

alter table public.session_questions
  add column if not exists question_snapshot_json jsonb not null default '{}'::jsonb,
  add column if not exists objective_ids_json jsonb not null default '[]'::jsonb,
  add column if not exists marks_available smallint not null default 1,
  add column if not exists marks_awarded smallint not null default 0;

alter table public.session_questions
  alter column question_id drop not null;

do $$
begin
  if exists (
    select 1
    from pg_constraint
    where conname = 'session_questions_question_id_fkey'
      and conrelid = 'public.session_questions'::regclass
  ) then
    alter table public.session_questions
      drop constraint session_questions_question_id_fkey;
  end if;
end
$$;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'session_questions_question_id_fkey'
      and conrelid = 'public.session_questions'::regclass
  ) then
    alter table public.session_questions
      add constraint session_questions_question_id_fkey
      foreign key (question_id) references public.questions(id) on delete set null;
  end if;
end
$$;

create table if not exists public.learning_objectives (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid not null references public.topics(id) on delete cascade,
  objective_code text not null,
  title text not null,
  description text not null,
  display_order integer not null,
  is_active boolean not null default true,
  created_at timestamptz not null default timezone('utc'::text, now()),
  unique (topic_id, objective_code)
);

create table if not exists public.content_sources (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid references public.topics(id) on delete set null,
  source_kind public.content_source_kind not null,
  title text not null,
  file_name text not null,
  year_label text,
  locator_text text,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table if not exists public.question_source_links (
  id uuid primary key default gen_random_uuid(),
  question_id uuid not null references public.questions(id) on delete cascade,
  content_source_id uuid not null references public.content_sources(id) on delete cascade,
  source_role text not null check (source_role in ('prompt', 'mark_scheme', 'fact_support', 'practice_model')),
  note text,
  created_at timestamptz not null default timezone('utc'::text, now()),
  unique (question_id, content_source_id, source_role)
);

create table if not exists public.question_assets (
  id uuid primary key default gen_random_uuid(),
  asset_kind public.question_asset_kind not null,
  storage_bucket text not null default 'question-assets',
  storage_path text not null unique,
  mime_type text,
  alt_text text not null,
  caption text,
  source_name text,
  source_locator text,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table if not exists public.content_owner_settings (
  singleton boolean primary key default true check (singleton),
  owner_auth_user_id uuid not null unique references public.profiles(id) on delete cascade,
  created_at timestamptz not null default timezone('utc'::text, now()),
  updated_at timestamptz not null default timezone('utc'::text, now())
);

create or replace function public.is_content_owner(p_user_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.content_owner_settings cos
    where cos.owner_auth_user_id = p_user_id
  );
$$;

create table if not exists public.import_batches (
  id uuid primary key default gen_random_uuid(),
  created_by uuid references public.profiles(id) on delete set null,
  topic_id uuid references public.topics(id) on delete set null,
  batch_label text not null,
  source_format public.import_source_format not null,
  batch_status public.import_batch_status not null default 'draft',
  storage_bucket text not null default 'question-imports',
  manifest_storage_path text,
  source_file_name text,
  notes text,
  metadata_json jsonb not null default '{}'::jsonb,
  approved_at timestamptz,
  applied_at timestamptz,
  created_at timestamptz not null default timezone('utc'::text, now()),
  updated_at timestamptz not null default timezone('utc'::text, now())
);

create table if not exists public.staged_questions (
  id uuid primary key default gen_random_uuid(),
  import_batch_id uuid not null references public.import_batches(id) on delete cascade,
  topic_id uuid not null references public.topics(id) on delete cascade,
  live_question_id uuid references public.questions(id) on delete set null,
  row_number integer,
  staging_status public.staged_question_status not null default 'draft',
  difficulty public.difficulty_level not null,
  format public.question_format not null,
  adaptive_tier public.adaptive_tier not null default 'core',
  question_family_code text,
  selection_weight numeric(6,2) not null default 1 check (selection_weight > 0 and selection_weight <= 100),
  stem text not null,
  options_json jsonb not null default '[]'::jsonb,
  correct_answer_json jsonb not null default '{}'::jsonb,
  markscheme_points_json jsonb not null default '[]'::jsonb,
  explanation text not null default '',
  max_marks smallint not null default 1 check (max_marks between 1 and 20),
  content_blocks_json jsonb not null default '[]'::jsonb,
  response_schema_json jsonb not null default '{}'::jsonb,
  autograde_rules_json jsonb not null default '{}'::jsonb,
  objective_codes_json jsonb not null default '[]'::jsonb,
  tags_json jsonb not null default '[]'::jsonb,
  source_kind public.content_source_kind,
  source_title text,
  source_file_name text,
  source_locator text,
  teacher_notes text,
  review_notes text,
  dedupe_fingerprint text,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc'::text, now()),
  updated_at timestamptz not null default timezone('utc'::text, now())
);

create table if not exists public.staged_question_assets (
  id uuid primary key default gen_random_uuid(),
  staged_question_id uuid not null references public.staged_questions(id) on delete cascade,
  asset_kind public.question_asset_kind not null,
  asset_role public.question_asset_role not null,
  storage_bucket text not null default 'question-imports',
  storage_path text not null unique,
  mime_type text,
  alt_text text not null,
  caption text,
  original_file_name text,
  source_locator text,
  display_order integer not null default 1,
  block_key text,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc'::text, now())
);

create table if not exists public.question_asset_links (
  id uuid primary key default gen_random_uuid(),
  question_id uuid not null references public.questions(id) on delete cascade,
  asset_id uuid not null references public.question_assets(id) on delete cascade,
  asset_role public.question_asset_role not null,
  display_order integer not null default 1,
  block_key text,
  created_at timestamptz not null default timezone('utc'::text, now()),
  unique (question_id, asset_id, asset_role, display_order)
);

create table if not exists public.question_objectives (
  id uuid primary key default gen_random_uuid(),
  question_id uuid not null references public.questions(id) on delete cascade,
  objective_id uuid not null references public.learning_objectives(id) on delete cascade,
  is_primary boolean not null default false,
  display_order integer not null default 1,
  created_at timestamptz not null default timezone('utc'::text, now()),
  unique (question_id, objective_id)
);

create table if not exists public.student_topic_mastery (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.student_accounts(id) on delete cascade,
  academic_year_id uuid not null references public.academic_years(id) on delete cascade,
  topic_id uuid not null references public.topics(id) on delete cascade,
  sessions_completed integer not null default 0,
  questions_attempted integer not null default 0,
  questions_fully_correct integer not null default 0,
  marks_earned integer not null default 0,
  marks_available integer not null default 0,
  accuracy_pct numeric(6,2) not null default 0,
  mastery_score numeric(6,2) not null default 0,
  support_band text not null default 'steady' check (support_band in ('support', 'steady', 'challenge')),
  last_revised_at timestamptz,
  updated_at timestamptz not null default timezone('utc'::text, now()),
  unique (student_id, academic_year_id, topic_id)
);

create table if not exists public.student_objective_mastery (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.student_accounts(id) on delete cascade,
  academic_year_id uuid not null references public.academic_years(id) on delete cascade,
  objective_id uuid not null references public.learning_objectives(id) on delete cascade,
  questions_attempted integer not null default 0,
  marks_earned integer not null default 0,
  marks_available integer not null default 0,
  accuracy_pct numeric(6,2) not null default 0,
  mastery_score numeric(6,2) not null default 0,
  support_band text not null default 'steady' check (support_band in ('support', 'steady', 'challenge')),
  last_attempted_at timestamptz,
  updated_at timestamptz not null default timezone('utc'::text, now()),
  unique (student_id, academic_year_id, objective_id)
);

create index if not exists idx_learning_objectives_topic_order
  on public.learning_objectives(topic_id, display_order);

create index if not exists idx_content_sources_topic_kind
  on public.content_sources(topic_id, source_kind);

create index if not exists idx_import_batches_topic_status
  on public.import_batches(topic_id, batch_status, created_at desc);

create index if not exists idx_staged_questions_batch_status
  on public.staged_questions(import_batch_id, staging_status, row_number);

create index if not exists idx_staged_questions_topic_family
  on public.staged_questions(topic_id, question_family_code);

create index if not exists idx_staged_question_assets_question_order
  on public.staged_question_assets(staged_question_id, display_order);

create index if not exists idx_question_source_links_question
  on public.question_source_links(question_id);

create index if not exists idx_question_asset_links_question_order
  on public.question_asset_links(question_id, display_order);

create index if not exists idx_question_objectives_question
  on public.question_objectives(question_id);

create index if not exists idx_question_objectives_objective
  on public.question_objectives(objective_id);

create index if not exists idx_questions_topic_difficulty_tier
  on public.questions(topic_id, difficulty, adaptive_tier);

create index if not exists idx_questions_topic_family
  on public.questions(topic_id, question_family_code);

create index if not exists idx_student_topic_mastery_lookup
  on public.student_topic_mastery(student_id, academic_year_id, topic_id);

create index if not exists idx_student_objective_mastery_lookup
  on public.student_objective_mastery(student_id, academic_year_id, objective_id);

create or replace function public.save_session_submission(
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
  question_snapshot jsonb;
  objective_ids jsonb;
  question_marks smallint;
  earned_points integer;
  available_points integer;
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

    select
      jsonb_build_object(
        'id', q.id,
        'topic_id', q.topic_id,
        'topic_title', t.title,
        'difficulty', q.difficulty,
        'format', q.format,
        'stem', q.stem,
        'explanation', q.explanation,
        'tags_json', q.tags_json,
        'max_marks', q.max_marks,
        'content_blocks_json', q.content_blocks_json,
        'response_schema_json', q.response_schema_json,
        'autograde_rules_json', q.autograde_rules_json
      ),
      coalesce(
        (
          select jsonb_agg(qo.objective_id order by qo.is_primary desc, qo.display_order asc)
          from public.question_objectives qo
          where qo.question_id = q.id
        ),
        '[]'::jsonb
      ),
      coalesce(q.max_marks, 1)
    into question_snapshot, objective_ids, question_marks
    from public.questions q
    join public.topics t on t.id = q.topic_id
    where q.id = answer_question_id;

    insert into public.session_questions (
      session_id,
      question_id,
      position,
      student_answer_json,
      is_correct,
      response_time_ms,
      hint_used,
      question_snapshot_json,
      objective_ids_json,
      marks_available,
      marks_awarded
    )
    values (
      p_session_id,
      answer_question_id,
      answer_position,
      coalesce(answer_json, '{}'::jsonb),
      coalesce(answer_correct, false),
      coalesce(answer_response_time, 0),
      answer_hint_used,
      coalesce(question_snapshot, jsonb_build_object('id', answer_question_id)),
      coalesce(objective_ids, '[]'::jsonb),
      coalesce(question_marks, 1),
      case when coalesce(answer_correct, false) then coalesce(question_marks, 1) else 0 end
    )
    on conflict (session_id, position) do update
      set question_id = excluded.question_id,
          student_answer_json = excluded.student_answer_json,
          is_correct = excluded.is_correct,
          response_time_ms = excluded.response_time_ms,
          hint_used = excluded.hint_used,
          question_snapshot_json = excluded.question_snapshot_json,
          objective_ids_json = excluded.objective_ids_json,
          marks_available = excluded.marks_available,
          marks_awarded = excluded.marks_awarded;
  end loop;

  select
    coalesce(sum(sq.marks_awarded), 0),
    coalesce(sum(sq.marks_available), 0)
  into earned_points, available_points
  from public.session_questions sq
  where sq.session_id = p_session_id;

  update public.sessions
  set completed_at = timezone('utc'::text, now()),
      score = earned_points,
      accuracy_pct = case
        when available_points > 0 then round((earned_points::numeric / available_points::numeric) * 100, 2)
        else coalesce(p_accuracy_pct, 0)
      end,
      points_earned = earned_points,
      points_available = available_points,
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

alter table public.learning_objectives enable row level security;
alter table public.content_sources enable row level security;
alter table public.question_source_links enable row level security;
alter table public.question_assets enable row level security;
alter table public.content_owner_settings enable row level security;
alter table public.import_batches enable row level security;
alter table public.staged_questions enable row level security;
alter table public.staged_question_assets enable row level security;
alter table public.question_asset_links enable row level security;
alter table public.question_objectives enable row level security;
alter table public.student_topic_mastery enable row level security;
alter table public.student_objective_mastery enable row level security;

drop policy if exists learning_objectives_read_all on public.learning_objectives;
create policy learning_objectives_read_all
on public.learning_objectives for select
using (auth.role() = 'authenticated');

drop policy if exists learning_objectives_admin_write on public.learning_objectives;
create policy learning_objectives_admin_write
on public.learning_objectives for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

drop policy if exists content_sources_admin_only on public.content_sources;
create policy content_sources_admin_only
on public.content_sources for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

drop policy if exists question_source_links_admin_only on public.question_source_links;
create policy question_source_links_admin_only
on public.question_source_links for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

drop policy if exists question_assets_read_all on public.question_assets;
create policy question_assets_read_all
on public.question_assets for select
using (auth.role() = 'authenticated');

drop policy if exists question_assets_admin_write on public.question_assets;
create policy question_assets_admin_write
on public.question_assets for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

drop policy if exists content_owner_settings_admin_only on public.content_owner_settings;
create policy content_owner_settings_admin_only
on public.content_owner_settings for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

drop policy if exists import_batches_owner_only on public.import_batches;
create policy import_batches_owner_only
on public.import_batches for all
using (public.is_content_owner(auth.uid()))
with check (public.is_content_owner(auth.uid()));

drop policy if exists staged_questions_owner_only on public.staged_questions;
create policy staged_questions_owner_only
on public.staged_questions for all
using (public.is_content_owner(auth.uid()))
with check (public.is_content_owner(auth.uid()));

drop policy if exists staged_question_assets_owner_only on public.staged_question_assets;
create policy staged_question_assets_owner_only
on public.staged_question_assets for all
using (public.is_content_owner(auth.uid()))
with check (public.is_content_owner(auth.uid()));

drop policy if exists question_asset_links_read_all on public.question_asset_links;
create policy question_asset_links_read_all
on public.question_asset_links for select
using (auth.role() = 'authenticated');

drop policy if exists question_asset_links_admin_write on public.question_asset_links;
create policy question_asset_links_admin_write
on public.question_asset_links for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

drop policy if exists question_objectives_read_all on public.question_objectives;
create policy question_objectives_read_all
on public.question_objectives for select
using (auth.role() = 'authenticated');

drop policy if exists question_objectives_admin_write on public.question_objectives;
create policy question_objectives_admin_write
on public.question_objectives for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

drop policy if exists student_topic_mastery_student_read on public.student_topic_mastery;
create policy student_topic_mastery_student_read
on public.student_topic_mastery for select
using (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.student_accounts sa
    where sa.id = student_topic_mastery.student_id
      and sa.auth_user_id = auth.uid()
  )
);

drop policy if exists student_topic_mastery_admin_write on public.student_topic_mastery;
create policy student_topic_mastery_admin_write
on public.student_topic_mastery for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

drop policy if exists student_objective_mastery_student_read on public.student_objective_mastery;
create policy student_objective_mastery_student_read
on public.student_objective_mastery for select
using (
  public.is_admin(auth.uid())
  or exists (
    select 1
    from public.student_accounts sa
    where sa.id = student_objective_mastery.student_id
      and sa.auth_user_id = auth.uid()
  )
);

drop policy if exists student_objective_mastery_admin_write on public.student_objective_mastery;
create policy student_objective_mastery_admin_write
on public.student_objective_mastery for all
using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

grant select on public.learning_objectives, public.question_assets, public.question_asset_links, public.question_objectives, public.student_topic_mastery, public.student_objective_mastery to authenticated;
grant select on public.content_sources, public.question_source_links to authenticated;
grant select, insert, update, delete on public.content_owner_settings, public.import_batches, public.staged_questions, public.staged_question_assets to authenticated;
grant insert, update, delete on public.learning_objectives, public.content_sources, public.question_source_links, public.question_assets, public.question_asset_links, public.question_objectives, public.student_topic_mastery, public.student_objective_mastery to authenticated;

update public.topics
set slug = 'software',
    title = 'Software',
    display_order = 2
where slug = 'software-applications';

update public.topics
set slug = 'cyberspace-network-security-and-data-transfer',
    title = 'Cyberspace, network security and data transfer',
    display_order = 7
where slug = 'cyberspace-security';

update public.topics
set slug = 'ethical-legal-and-environmental-impact',
    title = 'Ethical, legal and environmental impact',
    display_order = 9
where slug = 'legislation-impact';

insert into public.topics (slug, title, is_enabled, display_order)
values
  ('digital-data', 'Digital data', false, 1),
  ('software', 'Software', false, 2),
  ('database-applications', 'Database applications', false, 3),
  ('spreadsheet-applications', 'Spreadsheet applications', false, 4),
  ('computer-hardware', 'Computer hardware', false, 5),
  ('network-technologies', 'Network technologies', true, 6),
  ('cyberspace-network-security-and-data-transfer', 'Cyberspace, network security and data transfer', false, 7),
  ('cloud-technology', 'Cloud technology', false, 8),
  ('ethical-legal-and-environmental-impact', 'Ethical, legal and environmental impact', false, 9),
  ('changes-in-employment-opportunities-skills-requirements-and-work-practices', 'Changes in employment opportunities, skills requirements and work practices', false, 10),
  ('health-and-safety', 'Health and safety', false, 11),
  ('digital-applications', 'Digital applications', false, 12)
on conflict (slug) do update
set title = excluded.title,
    is_enabled = excluded.is_enabled,
    display_order = excluded.display_order;
