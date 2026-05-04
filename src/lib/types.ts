export type Role = "student" | "admin";
export type Difficulty = "easy" | "medium" | "expert";
export type QuestionFormat =
  | "mcq"
  | "drag_drop"
  | "match_table"
  | "fill_gap"
  | "short_text"
  | "structured_response"
  | "diagram_label"
  | "multi_select"
  | "true_false";

export type RuntimeQuestionFormat =
  | "mcq"
  | "true_false"
  | "match_table"
  | "fill_gap"
  | "short_text"
  | "multi_select"
  | "drag_drop"
  | "diagram_label";

export interface RuntimeChoice {
  id: string;
  label: string;
}

export interface RuntimePromptBlock {
  kind: string;
  text?: string;
  title?: string;
  body?: string;
  block_key?: string;
  [key: string]: unknown;
}

export interface RuntimeAsset {
  asset_id?: string;
  role?: string;
  kind?: string;
  bucket?: string;
  path?: string;
  url?: string;
  public_url?: string;
  alt_text?: string;
  caption?: string | null;
  display_order?: number;
  block_key?: string | null;
}

export interface RuntimeSingleChoiceSchema {
  kind: "single_choice";
  choices: RuntimeChoice[];
}

export interface RuntimeTrueFalseSchema {
  kind: "true_false";
  statement?: string;
  true_label?: string;
  false_label?: string;
}

export interface RuntimeMatchTableSchema {
  kind: "match_table";
  rows: Array<{ id: string; label: string }>;
  choices: RuntimeChoice[];
}

export interface RuntimeFillGapSchema {
  kind: "fill_gap";
  gaps: Array<{ id: string; label: string }>;
}

export interface RuntimeShortTextSchema {
  kind: "short_text";
  placeholder?: string;
  max_length?: number;
}

export interface RuntimeMultiSelectSchema {
  kind: "multi_select";
  choices: RuntimeChoice[];
  min_select?: number;
  max_select?: number;
}

export interface RuntimeOrderingSchema {
  kind: "ordering";
  items: RuntimeChoice[];
}

export interface RuntimeDiagramLabelSchema {
  kind: "diagram_label";
  input_mode?: "single_choice" | "text";
  diagram_key?: string;
  marker?: string;
  choices?: RuntimeChoice[];
  placeholder?: string;
}

export interface RuntimeUnsupportedSchema {
  kind: "unsupported";
}

export type RuntimeResponseSchema =
  | RuntimeSingleChoiceSchema
  | RuntimeTrueFalseSchema
  | RuntimeMatchTableSchema
  | RuntimeFillGapSchema
  | RuntimeShortTextSchema
  | RuntimeMultiSelectSchema
  | RuntimeOrderingSchema
  | RuntimeDiagramLabelSchema
  | RuntimeUnsupportedSchema;

export interface RuntimeQuestionFeedback {
  summary?: string;
  corrections?: unknown[];
  accepted_answer_preview?: unknown[];
}

export interface RuntimeQuestionResult {
  result: "correct" | "partial" | "incorrect";
  is_correct: boolean;
  marks_awarded: number;
  marks_available: number;
  feedback: RuntimeQuestionFeedback;
}

export interface RuntimeQuestion {
  session_item_id: string;
  question_id: string;
  topic_id: string;
  difficulty: Difficulty;
  adaptive_tier: "support" | "core" | "challenge";
  format: RuntimeQuestionFormat;
  max_marks: number;
  family_code: string | null;
  stem: string;
  prompt_blocks: RuntimePromptBlock[];
  assets: RuntimeAsset[];
  response_schema: RuntimeResponseSchema;
  autograde_rules: Record<string, unknown>;
  explanation: string;
  tags: string[];
  objective_ids: string[];
}

export interface RuntimeSessionQuestion extends RuntimeQuestion {
  position: number;
  grading_status: "pending" | "graded";
  student_answer: Record<string, unknown>;
  is_correct: boolean | null;
  marks_awarded: number;
  marks_available: number;
  feedback: RuntimeQuestionFeedback | null;
}

export interface RuntimeSessionState {
  session_id: string;
  topic_id: string;
  difficulty: Difficulty;
  academic_year_id: string;
  started_at: string;
  completed_at: string | null;
  questions: RuntimeSessionQuestion[];
  session_status?: "started" | "resumed";
}

export interface RuntimeSessionSummary {
  session_id: string;
  score: number;
  points_earned: number;
  points_available: number;
  accuracy_pct: number;
  streak_after: number;
  completed_at: string;
}

export interface Profile {
  id: string;
  role: Role;
  display_name: string | null;
  is_active: boolean;
  can_edit_questions?: boolean;
}

export interface Topic {
  id: string;
  slug: string;
  title: string;
  is_enabled: boolean;
  display_order: number;
}

export interface AcademicYear {
  id: string;
  code: string;
  is_active: boolean;
  timezone: string;
}

export interface Question {
  id: string;
  topic_id: string;
  difficulty: Difficulty;
  format: QuestionFormat;
  stem: string;
  options_json: Record<string, unknown> | null;
  correct_answer_json: Record<string, unknown>;
  markscheme_points_json: string[];
  explanation: string;
  source_type: "adapted_exam" | "new_original";
  source_ref: string;
  tags_json: string[];
  is_active: boolean;
}

export interface SessionRecord {
  id: string;
  student_id: string;
  academic_year_id: string;
  topic_id: string;
  topics?: {
    id: string;
    slug: string;
    title: string;
  } | null;
  difficulty: Difficulty;
  started_at: string;
  completed_at: string | null;
  score: number | null;
  accuracy_pct: number | null;
  points_earned: number | null;
  streak_after: number | null;
}

export interface SessionQuestionAnswer {
  questionId: string;
  position: number;
  answer: Record<string, unknown>;
  isCorrect: boolean;
  responseTimeMs: number;
  hintUsed: boolean;
}

export interface DailyCap {
  id: string;
  student_id: string;
  academic_year_id: string;
  difficulty: Difficulty;
  local_date: string;
  sessions_completed: number;
}
