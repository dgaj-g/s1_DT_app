-- Digital Data content correction after teacher review.
-- Retire the 24-bit true-colour count item: accurate arithmetic, but too niche
-- and not representative of likely Unit 1 exam questioning.
-- Reframe resolution around CCEA past-paper mark-scheme wording: number of
-- pixels / pixels per inch, with higher resolution usually improving quality
-- and increasing file size.

begin;

with retired_questions as (
  update public.questions q
  set
    is_active = false,
    qa_status = 'draft',
    teacher_notes = concat_ws(
      ' | ',
      nullif(q.teacher_notes, ''),
      'Scope correction 2026-05-14: retired from live student sessions because 24-bit true-colour count recall is too niche for the intended exam-revision bank.'
    )
  from public.topics t
  where q.topic_id = t.id
    and t.slug = 'digital-data'
    and q.external_id = 'digital-data.practice_bank.topic_01_digital_data.q028'
  returning q.id
)
delete from public.question_objectives qo
using retired_questions rq
where qo.question_id = rq.id;

update public.questions q
set
  stem = 'Which statement best describes the resolution of a bitmap image?',
  options_json = jsonb_build_object(
    'choices', jsonb_build_array(
      'The number of pixels in the image; higher resolution usually means better quality and a larger file size',
      'The total number of colours that can be displayed in the image',
      'The file format used to save the image, such as JPG or PNG',
      'The physical width of the image measured in centimetres'
    )
  ),
  correct_answer_json = jsonb_build_object(
    'choice', 'The number of pixels in the image; higher resolution usually means better quality and a larger file size'
  ),
  markscheme_points_json = jsonb_build_array(
    'Resolution means the number of pixels in an image or pixels per inch.',
    'Higher resolution usually gives better quality and increases file size/storage required.'
  ),
  explanation = 'Resolution means the number of pixels in an image, often described as pixels per inch. A higher-resolution image normally has better quality but needs more storage space.',
  source_type = 'adapted_exam'::public.question_source,
  source_ref = '2018 Q4(a)(ii), 2019 Q4(a)(ii), and 2023 Q2(b) mark-scheme wording on resolution - simplified MCQ',
  content_blocks_json = jsonb_build_array(
    jsonb_build_object('kind', 'text', 'text', 'Which statement best describes the resolution of a bitmap image?', 'block_key', null)
  ),
  response_schema_json = jsonb_build_object(
    'kind', 'single_choice',
    'choices', jsonb_build_array(
      jsonb_build_object('id', 'a', 'label', 'The number of pixels in the image; higher resolution usually means better quality and a larger file size'),
      jsonb_build_object('id', 'b', 'label', 'The total number of colours that can be displayed in the image'),
      jsonb_build_object('id', 'c', 'label', 'The file format used to save the image, such as JPG or PNG'),
      jsonb_build_object('id', 'd', 'label', 'The physical width of the image measured in centimetres')
    )
  ),
  autograde_rules_json = jsonb_build_object('kind', 'single_choice', 'correct_choice_id', 'a'),
  teacher_notes = concat_ws(
    ' | ',
    nullif(q.teacher_notes, ''),
    'Scope correction 2026-05-14: rewrote resolution prompt to match CCEA mark-scheme language on number of pixels, quality, and storage/file size.'
  )
from public.topics t
where q.topic_id = t.id
  and t.slug = 'digital-data'
  and q.external_id = 'digital-data.practice_bank.topic_01_digital_data.q029';

commit;
