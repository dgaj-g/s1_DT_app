-- Stage 5 import keys.
--
-- These stable external IDs let the reviewed Unit 1 question payload be
-- applied repeatedly without duplicating questions, sources, or assets.
-- Existing student credentials and historical session rows are untouched.

alter table public.questions
  add column if not exists external_id text;

alter table public.content_sources
  add column if not exists external_id text;

alter table public.question_assets
  add column if not exists external_id text;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'questions_external_id_key'
      and conrelid = 'public.questions'::regclass
  ) then
    alter table public.questions
      add constraint questions_external_id_key unique (external_id);
  end if;
end
$$;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'content_sources_external_id_key'
      and conrelid = 'public.content_sources'::regclass
  ) then
    alter table public.content_sources
      add constraint content_sources_external_id_key unique (external_id);
  end if;
end
$$;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'question_assets_external_id_key'
      and conrelid = 'public.question_assets'::regclass
  ) then
    alter table public.question_assets
      add constraint question_assets_external_id_key unique (external_id);
  end if;
end
$$;
