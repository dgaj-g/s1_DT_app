import { supabase } from "./supabase";
import type {
  AcademicYear,
  DailyCap,
  Difficulty,
  Question,
  SessionQuestionAnswer,
  SessionRecord,
  Topic
} from "./types";

export async function getActiveAcademicYear(): Promise<AcademicYear | null> {
  const { data, error } = await supabase
    .from("academic_years")
    .select("id, code, is_active, timezone")
    .eq("is_active", true)
    .single();

  if (error) {
    return null;
  }

  return data as AcademicYear;
}

export async function getAllAcademicYears(): Promise<AcademicYear[]> {
  const { data, error } = await supabase
    .from("academic_years")
    .select("id, code, is_active, timezone")
    .order("code", { ascending: false });

  if (error) {
    throw error;
  }

  return (data || []) as AcademicYear[];
}

export async function setActiveAcademicYear(id: string) {
  const { error } = await supabase.rpc("set_active_academic_year", {
    p_year_id: id
  });

  if (error) {
    throw error;
  }
}

export async function getTopics(): Promise<Topic[]> {
  const { data, error } = await supabase
    .from("topics")
    .select("id, slug, title, is_enabled, display_order")
    .order("display_order", { ascending: true });

  if (error) {
    throw error;
  }

  return (data || []) as Topic[];
}

export async function getStudentAccountId(authUserId: string): Promise<string> {
  const { data, error } = await supabase
    .from("student_accounts")
    .select("id")
    .eq("auth_user_id", authUserId)
    .single();

  if (error || !data) {
    throw error || new Error("Student account not found");
  }

  return data.id;
}

export async function canStartSession(args: {
  studentId: string;
  academicYearId: string;
  difficulty: Difficulty;
  localDate: string;
}): Promise<boolean> {
  const { data, error } = await supabase.rpc("can_start_session", {
    p_student_id: args.studentId,
    p_academic_year_id: args.academicYearId,
    p_difficulty: args.difficulty,
    p_local_date: args.localDate,
    p_max_sessions: 3
  });

  if (error) {
    throw error;
  }

  return !!data;
}

export async function getTodayCaps(args: {
  studentId: string;
  academicYearId: string;
  localDate: string;
}): Promise<DailyCap[]> {
  const { data, error } = await supabase
    .from("daily_caps")
    .select("id, student_id, academic_year_id, difficulty, local_date, sessions_completed")
    .eq("student_id", args.studentId)
    .eq("academic_year_id", args.academicYearId)
    .eq("local_date", args.localDate);

  if (error) {
    throw error;
  }

  return (data || []) as DailyCap[];
}

export async function createSession(args: {
  studentId: string;
  academicYearId: string;
  topicId: string;
  difficulty: Difficulty;
}): Promise<SessionRecord> {
  const { data, error } = await supabase
    .from("sessions")
    .insert({
      student_id: args.studentId,
      academic_year_id: args.academicYearId,
      topic_id: args.topicId,
      difficulty: args.difficulty,
      started_at: new Date().toISOString()
    })
    .select("*")
    .single();

  if (error) {
    throw error;
  }

  return data as SessionRecord;
}

export async function pickSessionQuestions(args: {
  studentId: string;
  topicId: string;
  difficulty: Difficulty;
  count: number;
}): Promise<Question[]> {
  const { data, error } = await supabase.rpc("pick_session_questions", {
    p_student_id: args.studentId,
    p_topic_id: args.topicId,
    p_difficulty: args.difficulty,
    p_count: args.count,
    p_recency_buffer: 30
  });

  if (error) {
    throw error;
  }

  return (data || []) as Question[];
}

export async function saveSessionSubmission(args: {
  sessionId: string;
  studentId: string;
  academicYearId: string;
  localDate: string;
  answers: SessionQuestionAnswer[];
  accuracyPct: number;
  score: number;
  pointsEarned: number;
  streakAfter: number;
}) {
  const { error } = await supabase.rpc("save_session_submission", {
    p_session_id: args.sessionId,
    p_student_id: args.studentId,
    p_academic_year_id: args.academicYearId,
    p_local_date: args.localDate,
    p_answers: args.answers,
    p_accuracy_pct: args.accuracyPct,
    p_score: args.score,
    p_points_earned: args.pointsEarned,
    p_streak_after: args.streakAfter
  });

  if (error) {
    throw error;
  }
}

export async function getSession(sessionId: string): Promise<SessionRecord | null> {
  const { data, error } = await supabase.from("sessions").select("*").eq("id", sessionId).single();
  if (error) {
    return null;
  }
  return data as SessionRecord;
}

export async function getSessionQuestions(sessionId: string) {
  const { data, error } = await supabase
    .from("session_questions")
    .select(
      "id, position, student_answer_json, is_correct, response_time_ms, hint_used, questions:question_id (id, stem, format, explanation, tags_json, difficulty)"
    )
    .eq("session_id", sessionId)
    .order("position", { ascending: true });

  if (error) {
    throw error;
  }

  return data || [];
}

export async function getStudentSessions(args: { studentId: string; academicYearId: string }) {
  const { data, error } = await supabase
    .from("sessions")
    .select("*")
    .eq("student_id", args.studentId)
    .eq("academic_year_id", args.academicYearId)
    .not("completed_at", "is", null)
    .order("completed_at", { ascending: true });

  if (error) {
    throw error;
  }

  return (data || []) as SessionRecord[];
}

export async function getStudentAnsweredTags(args: { studentId: string; academicYearId: string }) {
  const { data, error } = await supabase
    .from("session_questions")
    .select(
      "is_correct, questions:question_id (tags_json), sessions:session_id!inner(student_id, academic_year_id, completed_at)"
    )
    .eq("sessions.student_id", args.studentId)
    .eq("sessions.academic_year_id", args.academicYearId)
    .not("sessions.completed_at", "is", null);

  if (error) {
    throw error;
  }

  return data || [];
}

export async function getAdminSummary(args: { academicYearId: string }) {
  const [{ count: students }, { count: sessions }, { data: caps }, { count: questions }] = await Promise.all([
    supabase
      .from("student_accounts")
      .select("id", { head: true, count: "exact" })
      .eq("is_active", true),
    supabase
      .from("sessions")
      .select("id", { head: true, count: "exact" })
      .eq("academic_year_id", args.academicYearId)
      .not("completed_at", "is", null),
    supabase
      .from("daily_caps")
      .select("difficulty, sessions_completed")
      .eq("academic_year_id", args.academicYearId),
    supabase.from("questions").select("id", { head: true, count: "exact" }).eq("is_active", true)
  ]);

  return {
    students: students ?? 0,
    completedSessions: sessions ?? 0,
    dailyCaps: caps ?? [],
    activeQuestions: questions ?? 0
  };
}

export async function getAdminAccounts() {
  const { data, error } = await supabase
    .from("profiles")
    .select("id, display_name, role, is_active, can_edit_questions, created_at")
    .eq("role", "admin")
    .order("created_at", { ascending: true });

  if (error) {
    throw error;
  }

  return data || [];
}

export async function updateQuestionContent(args: {
  id: string;
  difficulty: Difficulty;
  format: Question["format"];
  stem: string;
  optionsJson: Record<string, unknown> | null;
  correctAnswerJson: Record<string, unknown>;
  explanation: string;
  sourceType: Question["source_type"];
  sourceRef: string;
  tags: string[];
}) {
  const { error } = await supabase
    .from("questions")
    .update({
      difficulty: args.difficulty,
      format: args.format,
      stem: args.stem,
      options_json: args.optionsJson,
      correct_answer_json: args.correctAnswerJson,
      explanation: args.explanation,
      source_type: args.sourceType,
      source_ref: args.sourceRef,
      tags_json: args.tags,
      qa_status: "draft",
      reviewed_at: null
    })
    .eq("id", args.id);

  if (error) {
    throw error;
  }
}

export async function toggleAdminProfileActive(profileId: string, isActive: boolean) {
  const { error } = await supabase
    .from("profiles")
    .update({ is_active: isActive })
    .eq("id", profileId)
    .eq("role", "admin");

  if (error) {
    throw error;
  }
}

export async function getQuestionsForAdmin(topicId?: string, options?: { onlyActive?: boolean }) {
  let query = supabase
    .from("questions")
    .select(
      "id, topic_id, difficulty, format, stem, options_json, correct_answer_json, explanation, source_type, source_ref, is_active, qa_status, created_at, tags_json"
    )
    .order("difficulty", { ascending: true })
    .order("created_at", { ascending: true });

  if (topicId) {
    query = query.eq("topic_id", topicId);
  }
  if (options?.onlyActive) {
    query = query.eq("is_active", true);
  }

  const { data, error } = await query;

  if (error) {
    throw error;
  }

  return data || [];
}

export async function toggleQuestionActive(id: string, isActive: boolean) {
  const { error } = await supabase.from("questions").update({ is_active: isActive }).eq("id", id);
  if (error) {
    throw error;
  }
}

export async function setQuestionQaStatus(id: string, status: "draft" | "reviewed" | "published") {
  const updates: Record<string, unknown> = {
    qa_status: status,
    reviewed_at: status === "draft" ? null : new Date().toISOString()
  };

  if (status === "draft") {
    updates.is_active = false;
  }

  const { error } = await supabase
    .from("questions")
    .update(updates)
    .eq("id", id);

  if (error) {
    throw error;
  }
}

export async function toggleTopicEnabled(id: string, enabled: boolean) {
  const { error } = await supabase.from("topics").update({ is_enabled: enabled }).eq("id", id);
  if (error) {
    throw error;
  }
}

export async function callEdgeFunction<T = unknown>(name: string, body: Record<string, unknown>) {
  // Edge Functions with `verify_jwt = true` require a valid Authorization Bearer token.
  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error("You must be signed in to run this admin action.");
  }

  const { data, error } = await supabase.functions.invoke(name, {
    body,
    headers: {
      Authorization: `Bearer ${session.access_token}`
    }
  });

  if (error) {
    throw error;
  }

  return data as T;
}
