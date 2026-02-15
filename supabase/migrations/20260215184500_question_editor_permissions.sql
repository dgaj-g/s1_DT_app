-- Add owner-only question-content editing controls.

alter table public.profiles
add column if not exists can_edit_questions boolean not null default false;

create or replace function public.can_edit_questions(p_user_id uuid default auth.uid())
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
      and can_edit_questions = true
  );
$$;

grant execute on function public.can_edit_questions(uuid) to authenticated;

-- Bootstrap: if no editor has been assigned yet, assign the earliest active admin.
do $$
begin
  if not exists (
    select 1
    from public.profiles
    where role = 'admin'::public.app_role
      and can_edit_questions = true
  ) then
    update public.profiles
    set can_edit_questions = true
    where id = (
      select id
      from public.profiles
      where role = 'admin'::public.app_role
        and is_active = true
      order by created_at asc
      limit 1
    );
  end if;
end;
$$;

create or replace function public.enforce_profile_editor_assignment()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  if new.can_edit_questions is distinct from old.can_edit_questions
     and auth.uid() is not null
     and not public.can_edit_questions(auth.uid()) then
    raise exception 'Only the designated question editor can change question-editor access.';
  end if;

  return new;
end;
$$;

drop trigger if exists trg_enforce_profile_editor_assignment on public.profiles;

create trigger trg_enforce_profile_editor_assignment
before update on public.profiles
for each row
execute function public.enforce_profile_editor_assignment();

create or replace function public.enforce_question_update_permissions()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  if public.is_admin(auth.uid()) and not public.can_edit_questions(auth.uid()) then
    if new.topic_id is distinct from old.topic_id
       or new.difficulty is distinct from old.difficulty
       or new.format is distinct from old.format
       or new.stem is distinct from old.stem
       or new.options_json is distinct from old.options_json
       or new.correct_answer_json is distinct from old.correct_answer_json
       or new.markscheme_points_json is distinct from old.markscheme_points_json
       or new.explanation is distinct from old.explanation
       or new.source_type is distinct from old.source_type
       or new.source_ref is distinct from old.source_ref
       or new.tags_json is distinct from old.tags_json then
      raise exception 'Only the designated question editor can modify question content.';
    end if;
  end if;

  return new;
end;
$$;

drop trigger if exists trg_enforce_question_update_permissions on public.questions;

create trigger trg_enforce_question_update_permissions
before update on public.questions
for each row
execute function public.enforce_question_update_permissions();
