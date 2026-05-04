-- Safety assertions for strict visual-context repair.
-- This migration intentionally changes no content. It fails deployment if the
-- live database still has the unsafe broad visual repair state.

do $$
declare
  broad_link_count integer;
  strict_link_count integer;
  students_average_mark_image_count integer;
  vlookup_image_count integer;
  bad_sound_metadata_image_count integer;
begin
  select count(*)
  into broad_link_count
  from public.question_asset_links qal
  where coalesce(qal.metadata_json ->> 'stage5_visual_context_repair', 'false') = 'true';

  if broad_link_count <> 0 then
    raise exception 'Expected 0 unsafe broad visual-context repair links, found %', broad_link_count;
  end if;

  select count(*)
  into strict_link_count
  from public.question_asset_links qal
  where coalesce(qal.metadata_json ->> 'stage5_visual_context_strict_repair', 'false') = 'true';

  if strict_link_count < 100 then
    raise exception 'Expected at least 100 strict visual-context links, found %', strict_link_count;
  end if;

  select count(*)
  into students_average_mark_image_count
  from public.questions q
  join public.question_asset_links qal on qal.question_id = q.id
  join public.question_assets qa on qa.id = qal.asset_id
  where q.external_id = 'spreadsheet-applications.past_paper.topics_03_04.q026'
    and qa.storage_path = 'spreadsheet-applications/image26.png';

  if students_average_mark_image_count <> 1 then
    raise exception 'Students Average Mark question should be linked once to spreadsheet-applications/image26.png, found %', students_average_mark_image_count;
  end if;

  select count(*)
  into vlookup_image_count
  from public.questions q
  join public.question_asset_links qal on qal.question_id = q.id
  join public.question_assets qa on qa.id = qal.asset_id
  where q.external_id = 'spreadsheet-applications.past_paper.topics_03_04.q034'
    and qa.storage_path = 'spreadsheet-applications/image31.png';

  if vlookup_image_count <> 1 then
    raise exception 'VLOOKUP question should be linked once to spreadsheet-applications/image31.png, found %', vlookup_image_count;
  end if;

  select count(*)
  into bad_sound_metadata_image_count
  from public.questions q
  join public.question_asset_links qal on qal.question_id = q.id
  join public.question_assets qa on qa.id = qal.asset_id
  where q.external_id = 'digital-data.past_paper.topics_01_02.q021'
    and qa.storage_path = 'digital-data/image4.png';

  if bad_sound_metadata_image_count <> 0 then
    raise exception 'Sound recording fill-gap question must not be linked to digital-data/image4.png, found % links', bad_sound_metadata_image_count;
  end if;
end $$;
