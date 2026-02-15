export type Role = "student" | "admin";
export type Difficulty = "easy" | "medium" | "expert";
export type QuestionFormat =
  | "mcq"
  | "drag_drop"
  | "match_table"
  | "fill_gap"
  | "short_text"
  | "structured_response"
  | "diagram_label";

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
