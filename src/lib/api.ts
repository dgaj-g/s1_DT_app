import { supabase } from "./supabase";
import { withTimeout } from "./request";
import type {
  AcademicYear,
  DailyCap,
  Difficulty,
  Question,
  RuntimeQuestionFeedback,
  RuntimeSessionQuestion,
  RuntimeSessionState,
  RuntimeSessionSummary,
  SessionQuestionAnswer,
  SessionRecord,
  Topic
} from "./types";

function getUnknownErrorText(error: unknown): string {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  if (typeof error === "string" && error.trim()) {
    return error;
  }

  try {
    return JSON.stringify(error);
  } catch {
    return "";
  }
}

export function isV2RuntimeUnavailableError(error: unknown): boolean {
  const message = getUnknownErrorText(error).toLowerCase();
  return (
    (message.includes("could not find the function") &&
      (message.includes("start_session_v2") ||
        message.includes("grade_session_question_v2") ||
        message.includes("complete_session_v2") ||
        message.includes("get_session_state_v2"))) ||
    message.includes("session_question_status") ||
    message.includes("question_snapshot_json") ||
    message.includes("grading_feedback_json")
  );
}

function toRuntimeSessionQuestion(record: Record<string, unknown>): RuntimeSessionQuestion {
  const feedback =
    record.feedback && typeof record.feedback === "object"
      ? (record.feedback as RuntimeQuestionFeedback)
      : null;

  return {
    session_item_id: String(record.session_item_id || ""),
    question_id: String(record.question_id || ""),
    topic_id: String(record.topic_id || ""),
    difficulty: (record.difficulty || "easy") as Difficulty,
    adaptive_tier:
      record.adaptive_tier === "support" || record.adaptive_tier === "challenge"
        ? record.adaptive_tier
        : "core",
    format: (record.format || "short_text") as RuntimeSessionQuestion["format"],
    max_marks: Number(record.max_marks || 1),
    family_code: typeof record.family_code === "string" ? record.family_code : null,
    stem: String(record.stem || ""),
    prompt_blocks: Array.isArray(record.prompt_blocks) ? (record.prompt_blocks as RuntimeSessionQuestion["prompt_blocks"]) : [],
    assets: Array.isArray(record.assets) ? (record.assets as RuntimeSessionQuestion["assets"]) : [],
    response_schema:
      record.response_schema && typeof record.response_schema === "object"
        ? (record.response_schema as RuntimeSessionQuestion["response_schema"])
        : { kind: "unsupported" },
    autograde_rules:
      record.autograde_rules && typeof record.autograde_rules === "object"
        ? (record.autograde_rules as Record<string, unknown>)
        : {},
    explanation: String(record.explanation || ""),
    tags: Array.isArray(record.tags) ? (record.tags as string[]) : [],
    objective_ids: Array.isArray(record.objective_ids) ? (record.objective_ids as string[]) : [],
    position: Number(record.position || 0),
    grading_status: record.grading_status === "graded" ? "graded" : "pending",
    student_answer:
      record.student_answer && typeof record.student_answer === "object"
        ? (record.student_answer as Record<string, unknown>)
        : {},
    is_correct: typeof record.is_correct === "boolean" ? record.is_correct : null,
    marks_awarded: Number(record.marks_awarded || 0),
    marks_available: Number(record.marks_available || Number(record.max_marks || 1)),
    feedback
  };
}

export async function getActiveAcademicYear(): Promise<AcademicYear | null> {
  const { data, error } = await withTimeout(
    supabase
      .from("academic_years")
      .select("id, code, is_active, timezone")
      .eq("is_active", true)
      .single(),
    "Loading the active academic year"
  );

  if (error) {
    return null;
  }

  return data as AcademicYear;
}

export async function getAllAcademicYears(): Promise<AcademicYear[]> {
  const { data, error } = await withTimeout(
    supabase
      .from("academic_years")
      .select("id, code, is_active, timezone")
      .order("code", { ascending: false }),
    "Loading academic years"
  );

  if (error) {
    throw error;
  }

  return (data || []) as AcademicYear[];
}

export async function setActiveAcademicYear(id: string) {
  const { error } = await withTimeout(
    supabase.rpc("set_active_academic_year", {
      p_year_id: id
    }),
    "Saving the active academic year"
  );

  if (error) {
    throw error;
  }
}

export async function getTopics(): Promise<Topic[]> {
  const { data, error } = await withTimeout(
    supabase
      .from("topics")
      .select("id, slug, title, is_enabled, display_order")
      .order("display_order", { ascending: true }),
    "Loading topics"
  );

  if (error) {
    throw error;
  }

  return (data || []) as Topic[];
}

export async function getStudentAccountId(authUserId: string): Promise<string> {
  const { data, error } = await withTimeout(
    supabase
      .from("student_accounts")
      .select("id")
      .eq("auth_user_id", authUserId)
      .single(),
    "Loading your student account"
  );

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
  const { data, error } = await withTimeout(
    supabase.rpc("can_start_session", {
      p_student_id: args.studentId,
      p_academic_year_id: args.academicYearId,
      p_difficulty: args.difficulty,
      p_local_date: args.localDate,
      p_max_sessions: 3
    }),
    "Checking whether this session can start"
  );

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
  const { data, error } = await withTimeout(
    supabase
      .from("daily_caps")
      .select("id, student_id, academic_year_id, difficulty, local_date, sessions_completed")
      .eq("student_id", args.studentId)
      .eq("academic_year_id", args.academicYearId)
      .eq("local_date", args.localDate),
    "Loading today's session limits"
  );

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
  const { data, error } = await withTimeout(
    supabase
      .from("sessions")
      .insert({
        student_id: args.studentId,
        academic_year_id: args.academicYearId,
        topic_id: args.topicId,
        difficulty: args.difficulty,
        started_at: new Date().toISOString()
      })
      .select("*")
      .single(),
    "Creating your revision session"
  );

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
  const { data, error } = await withTimeout(
    supabase.rpc("pick_session_questions", {
      p_student_id: args.studentId,
      p_topic_id: args.topicId,
      p_difficulty: args.difficulty,
      p_count: args.count,
      p_recency_buffer: 30
    }),
    "Loading questions for this session"
  );

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
  const { error } = await withTimeout(
    supabase.rpc("save_session_submission", {
      p_session_id: args.sessionId,
      p_student_id: args.studentId,
      p_academic_year_id: args.academicYearId,
      p_local_date: args.localDate,
      p_answers: args.answers,
      p_accuracy_pct: args.accuracyPct,
      p_score: args.score,
      p_points_earned: args.pointsEarned,
      p_streak_after: args.streakAfter
    }),
    "Saving your session results"
  );

  if (error) {
    throw error;
  }
}

export async function getSessionStateV2(args: {
  sessionId: string;
  studentId: string;
}): Promise<RuntimeSessionState> {
  const { data, error } = await withTimeout(
    supabase.rpc("get_session_state_v2", {
      p_session_id: args.sessionId,
      p_student_id: args.studentId
    }),
    "Loading your in-progress session"
  );

  if (error) {
    throw error;
  }

  const payload = (data || {}) as Record<string, unknown>;
  return {
    session_id: String(payload.session_id || ""),
    topic_id: String(payload.topic_id || ""),
    difficulty: (payload.difficulty || "easy") as Difficulty,
    academic_year_id: String(payload.academic_year_id || ""),
    started_at: String(payload.started_at || ""),
    completed_at: payload.completed_at ? String(payload.completed_at) : null,
    session_status:
      payload.session_status === "started" || payload.session_status === "resumed"
        ? payload.session_status
        : undefined,
    questions: Array.isArray(payload.questions)
      ? payload.questions.map((item) => toRuntimeSessionQuestion(item as Record<string, unknown>))
      : []
  };
}

export async function startSessionV2(args: {
  studentId: string;
  academicYearId: string;
  topicId: string;
  difficulty: Difficulty;
  localDate: string;
  count?: number;
  recencyBuffer?: number;
}): Promise<RuntimeSessionState> {
  const { data, error } = await withTimeout(
    supabase.rpc("start_session_v2", {
      p_student_id: args.studentId,
      p_academic_year_id: args.academicYearId,
      p_topic_id: args.topicId,
      p_difficulty: args.difficulty,
      p_local_date: args.localDate,
      p_count: args.count ?? 10,
      p_recency_buffer: args.recencyBuffer ?? 30
    }),
    "Preparing your upgraded revision session"
  );

  if (error) {
    throw error;
  }

  const payload = (data || {}) as Record<string, unknown>;
  return {
    session_id: String(payload.session_id || ""),
    topic_id: String(payload.topic_id || ""),
    difficulty: (payload.difficulty || "easy") as Difficulty,
    academic_year_id: String(payload.academic_year_id || ""),
    started_at: String(payload.started_at || ""),
    completed_at: payload.completed_at ? String(payload.completed_at) : null,
    session_status:
      payload.session_status === "started" || payload.session_status === "resumed"
        ? payload.session_status
        : undefined,
    questions: Array.isArray(payload.questions)
      ? payload.questions.map((item) => toRuntimeSessionQuestion(item as Record<string, unknown>))
      : []
  };
}

export async function gradeSessionQuestionV2(args: {
  sessionId: string;
  studentId: string;
  sessionQuestionId: string;
  studentAnswer: Record<string, unknown>;
  responseTimeMs: number;
  hintUsed?: boolean;
}) {
  const { data, error } = await withTimeout(
    supabase.rpc("grade_session_question_v2", {
      p_session_id: args.sessionId,
      p_student_id: args.studentId,
      p_session_question_id: args.sessionQuestionId,
      p_student_answer: args.studentAnswer,
      p_response_time_ms: args.responseTimeMs,
      p_hint_used: args.hintUsed ?? false
    }),
    "Checking your answer"
  );

  if (error) {
    throw error;
  }

  return (data || {}) as {
    session_question_id: string;
    grading: {
      result: "correct" | "partial" | "incorrect";
      is_correct: boolean;
      marks_awarded: number;
      marks_available: number;
      feedback: RuntimeQuestionFeedback;
    };
    explanation: string;
  };
}

export async function completeSessionV2(args: {
  sessionId: string;
  studentId: string;
  academicYearId: string;
  localDate: string;
}): Promise<RuntimeSessionSummary> {
  const { data, error } = await withTimeout(
    supabase.rpc("complete_session_v2", {
      p_session_id: args.sessionId,
      p_student_id: args.studentId,
      p_academic_year_id: args.academicYearId,
      p_local_date: args.localDate
    }),
    "Finishing your session"
  );

  if (error) {
    throw error;
  }

  return (data || {}) as RuntimeSessionSummary;
}

export async function getSession(sessionId: string): Promise<SessionRecord | null> {
  const { data, error } = await withTimeout(
    supabase.from("sessions").select("*").eq("id", sessionId).single(),
    "Loading the session summary"
  );
  if (error) {
    return null;
  }
  return data as SessionRecord;
}

export async function getSessionQuestions(sessionId: string) {
  const { data, error } = await withTimeout(
    supabase
      .from("session_questions")
      .select(
        "id, position, student_answer_json, is_correct, response_time_ms, hint_used, questions:question_id (id, stem, format, explanation, tags_json, difficulty)"
      )
      .eq("session_id", sessionId)
      .order("position", { ascending: true }),
    "Loading your question review"
  );

  if (error) {
    throw error;
  }

  return data || [];
}

export async function getStudentSessions(args: { studentId: string; academicYearId: string }) {
  const { data, error } = await withTimeout(
    supabase
      .from("sessions")
      .select("*, topics:topic_id (id, slug, title)")
      .eq("student_id", args.studentId)
      .eq("academic_year_id", args.academicYearId)
      .not("completed_at", "is", null)
      .order("completed_at", { ascending: true }),
    "Loading your previous sessions"
  );

  if (error) {
    throw error;
  }

  return (data || []) as SessionRecord[];
}

export async function getStudentAnsweredTags(args: { studentId: string; academicYearId: string }) {
  const { data, error } = await withTimeout(
    supabase
      .from("session_questions")
      .select(
        "is_correct, questions:question_id (tags_json), sessions:session_id!inner(student_id, academic_year_id, completed_at)"
      )
      .eq("sessions.student_id", args.studentId)
      .eq("sessions.academic_year_id", args.academicYearId)
      .not("sessions.completed_at", "is", null),
    "Loading your revision topic data"
  );

  if (error) {
    throw error;
  }

  return data || [];
}

export async function getAdminSummary(args: { academicYearId: string }) {
  const [{ count: students }, { count: sessions }, { data: caps }, { count: questions }] = await withTimeout(
    Promise.all([
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
    ]),
    "Loading the admin summary"
  );

  return {
    students: students ?? 0,
    completedSessions: sessions ?? 0,
    dailyCaps: caps ?? [],
    activeQuestions: questions ?? 0
  };
}

export interface AdminActivitySession {
  id: string;
  username: string;
  topicTitle: string;
  topicSlug: string;
  difficulty: Difficulty;
  status: "completed" | "in_progress";
  score: number | null;
  accuracyPct: number | null;
  pointsEarned: number | null;
  streakAfter: number | null;
  startedAt: string;
  completedAt: string | null;
}

export interface AdminStudentActivity {
  studentId: string;
  username: string;
  isActive: boolean;
  sessionStarts: number;
  completedSessions: number;
  unfinishedSessions: number;
  averageAccuracy: number | null;
  bestTopic: string | null;
  needsWorkTopic: string | null;
  lastActivityAt: string | null;
  lastCompletedAt: string | null;
  latestStreak: number | null;
  status: "no_activity" | "needs_support" | "building" | "steady" | "strong";
}

export interface AdminTopicActivity {
  topicId: string;
  topicTitle: string;
  topicSlug: string;
  sessionStarts: number;
  completedSessions: number;
  activeStudents: number;
  averageAccuracy: number | null;
  lastRevisedAt: string | null;
  status: "no_activity" | "needs_attention" | "watch" | "steady" | "strong";
}

export interface AdminDifficultyActivity {
  difficulty: Difficulty;
  sessionStarts: number;
  completedSessions: number;
  averageAccuracy: number | null;
}

export interface AdminActivityAnalytics {
  generatedAt: string;
  totalStudents: number;
  activeStudentAccounts: number;
  studentsWithActivity: number;
  studentsWithoutActivity: number;
  sessionStarts: number;
  completedSessions: number;
  unfinishedSessions: number;
  questionsAnswered: number;
  averageAccuracy: number | null;
  lastActivityAt: string | null;
  recentSessions: AdminActivitySession[];
  students: AdminStudentActivity[];
  topics: AdminTopicActivity[];
  difficulties: AdminDifficultyActivity[];
  attention: {
    noActivity: AdminStudentActivity[];
    needsSupport: AdminStudentActivity[];
    inactiveSevenDays: AdminStudentActivity[];
  };
}

type RelatedRecord = Record<string, unknown> | Record<string, unknown>[] | null | undefined;

function getRelatedObject(value: RelatedRecord): Record<string, unknown> {
  if (Array.isArray(value)) {
    return (value[0] || {}) as Record<string, unknown>;
  }
  if (value && typeof value === "object") {
    return value as Record<string, unknown>;
  }
  return {};
}

function average(values: number[]): number | null {
  if (!values.length) {
    return null;
  }
  return Math.round((values.reduce((total, value) => total + value, 0) / values.length) * 10) / 10;
}

function newestIso(values: Array<string | null | undefined>): string | null {
  let newest = 0;
  let newestValue: string | null = null;

  for (const value of values) {
    if (!value) {
      continue;
    }
    const time = new Date(value).getTime();
    if (Number.isFinite(time) && time > newest) {
      newest = time;
      newestValue = value;
    }
  }

  return newestValue;
}

function getStudentStatus(completedSessions: number, averageAccuracy: number | null): AdminStudentActivity["status"] {
  if (completedSessions === 0) {
    return "no_activity";
  }
  if (averageAccuracy !== null && averageAccuracy < 60) {
    return "needs_support";
  }
  if (averageAccuracy !== null && averageAccuracy < 75) {
    return "building";
  }
  if (completedSessions >= 2 && averageAccuracy !== null && averageAccuracy >= 85) {
    return "strong";
  }
  return "steady";
}

function getTopicStatus(completedSessions: number, averageAccuracy: number | null): AdminTopicActivity["status"] {
  if (completedSessions === 0) {
    return "no_activity";
  }
  if (averageAccuracy !== null && averageAccuracy < 60) {
    return "needs_attention";
  }
  if (averageAccuracy !== null && averageAccuracy < 75) {
    return "watch";
  }
  if (averageAccuracy !== null && averageAccuracy >= 85) {
    return "strong";
  }
  return "steady";
}

export async function getAdminActivityAnalytics(args: { academicYearId: string }): Promise<AdminActivityAnalytics> {
  const { data: students, error: studentError } = await withTimeout(
    supabase
      .from("student_accounts")
      .select("id, username, is_active")
      .order("account_number", { ascending: true }),
    "Loading class activity students"
  );

  if (studentError) {
    throw studentError;
  }

  const sessions: Array<Record<string, unknown>> = [];
  const pageSize = 1000;
  let from = 0;

  while (true) {
    const { data, error } = await withTimeout(
      supabase
        .from("sessions")
        .select(
          "id, student_id, difficulty, score, accuracy_pct, points_earned, streak_after, started_at, completed_at, topics:topic_id(id, title, slug)"
        )
        .eq("academic_year_id", args.academicYearId)
        .order("started_at", { ascending: false })
        .order("id", { ascending: true })
        .range(from, from + pageSize - 1),
      "Loading class activity sessions"
    );

    if (error) {
      throw error;
    }

    const batch = (data || []) as Array<Record<string, unknown>>;
    sessions.push(...batch);

    if (batch.length < pageSize) {
      break;
    }

    from += pageSize;
  }

  const { count: questionCount, error: questionCountError } = await withTimeout(
    supabase
      .from("session_questions")
      .select("id, sessions:session_id!inner(academic_year_id)", { count: "exact", head: true })
      .eq("sessions.academic_year_id", args.academicYearId),
    "Counting answered questions"
  );

  const studentById = new Map<string, { id: string; username: string; is_active: boolean }>();
  for (const row of students || []) {
    studentById.set(String(row.id), {
      id: String(row.id),
      username: String(row.username),
      is_active: Boolean(row.is_active)
    });
  }

  const normalizedSessions: AdminActivitySession[] = sessions.map((row) => {
    const topic = getRelatedObject(row.topics as RelatedRecord);
    const student = studentById.get(String(row.student_id));
    const completedAt = row.completed_at ? String(row.completed_at) : null;

    return {
      id: String(row.id),
      username: student?.username || "unknown",
      topicTitle: String(topic.title || "Unknown topic"),
      topicSlug: String(topic.slug || ""),
      difficulty: (row.difficulty || "easy") as Difficulty,
      status: completedAt ? "completed" : "in_progress",
      score: row.score === null || row.score === undefined ? null : Number(row.score),
      accuracyPct: row.accuracy_pct === null || row.accuracy_pct === undefined ? null : Number(row.accuracy_pct),
      pointsEarned: row.points_earned === null || row.points_earned === undefined ? null : Number(row.points_earned),
      streakAfter: row.streak_after === null || row.streak_after === undefined ? null : Number(row.streak_after),
      startedAt: String(row.started_at),
      completedAt
    };
  });

  const completed = normalizedSessions.filter((session) => session.status === "completed");
  const completedAccuracy = completed
    .map((session) => session.accuracyPct)
    .filter((value): value is number => typeof value === "number" && Number.isFinite(value));

  const studentsActivity: AdminStudentActivity[] = Array.from(studentById.values()).map((student) => {
    const studentSessions = normalizedSessions.filter((session) => session.username === student.username);
    const studentCompleted = studentSessions.filter((session) => session.status === "completed");
    const studentAccuracy = studentCompleted
      .map((session) => session.accuracyPct)
      .filter((value): value is number => typeof value === "number" && Number.isFinite(value));

    const topicStats = new Map<string, { title: string; accuracies: number[]; completed: number }>();
    for (const session of studentCompleted) {
      if (session.accuracyPct === null) {
        continue;
      }
      const key = session.topicSlug || session.topicTitle;
      const stat = topicStats.get(key) || { title: session.topicTitle, accuracies: [], completed: 0 };
      stat.accuracies.push(session.accuracyPct);
      stat.completed += 1;
      topicStats.set(key, stat);
    }

    const rankedTopics = Array.from(topicStats.values())
      .map((item) => ({ ...item, averageAccuracy: average(item.accuracies) ?? 0 }))
      .filter((item) => item.completed > 0)
      .sort((a, b) => b.averageAccuracy - a.averageAccuracy);

    const averageAccuracy = average(studentAccuracy);
    const lastCompleted = newestIso(studentCompleted.map((session) => session.completedAt));
    const latestCompleted = [...studentCompleted].sort(
      (a, b) => new Date(b.completedAt || "").getTime() - new Date(a.completedAt || "").getTime()
    )[0];

    return {
      studentId: student.id,
      username: student.username,
      isActive: student.is_active,
      sessionStarts: studentSessions.length,
      completedSessions: studentCompleted.length,
      unfinishedSessions: studentSessions.length - studentCompleted.length,
      averageAccuracy,
      bestTopic: rankedTopics[0]?.title || null,
      needsWorkTopic: rankedTopics.length > 1 ? rankedTopics[rankedTopics.length - 1]?.title || null : null,
      lastActivityAt: newestIso(studentSessions.map((session) => session.completedAt || session.startedAt)),
      lastCompletedAt: lastCompleted,
      latestStreak: latestCompleted?.streakAfter ?? null,
      status: getStudentStatus(studentCompleted.length, averageAccuracy)
    };
  });

  const topicMap = new Map<string, AdminTopicActivity & { accuracies: number[]; usernames: Set<string> }>();
  for (const session of normalizedSessions) {
    const key = session.topicSlug || session.topicTitle;
    const existing =
      topicMap.get(key) ||
      ({
        topicId: key,
        topicTitle: session.topicTitle,
        topicSlug: session.topicSlug,
        sessionStarts: 0,
        completedSessions: 0,
        activeStudents: 0,
        averageAccuracy: null,
        lastRevisedAt: null,
        status: "no_activity",
        accuracies: [],
        usernames: new Set<string>()
      } as AdminTopicActivity & { accuracies: number[]; usernames: Set<string> });

    existing.sessionStarts += 1;
    existing.usernames.add(session.username);
    existing.lastRevisedAt = newestIso([existing.lastRevisedAt, session.completedAt || session.startedAt]);

    if (session.status === "completed") {
      existing.completedSessions += 1;
      if (session.accuracyPct !== null) {
        existing.accuracies.push(session.accuracyPct);
      }
    }

    topicMap.set(key, existing);
  }

  const topics = Array.from(topicMap.values())
    .map((topic) => {
      const topicAverage = average(topic.accuracies);
      return {
        topicId: topic.topicId,
        topicTitle: topic.topicTitle,
        topicSlug: topic.topicSlug,
        sessionStarts: topic.sessionStarts,
        completedSessions: topic.completedSessions,
        activeStudents: topic.usernames.size,
        averageAccuracy: topicAverage,
        lastRevisedAt: topic.lastRevisedAt,
        status: getTopicStatus(topic.completedSessions, topicAverage)
      };
    })
    .sort((a, b) => {
      const statusOrder: Record<AdminTopicActivity["status"], number> = {
        needs_attention: 0,
        watch: 1,
        no_activity: 2,
        steady: 3,
        strong: 4
      };
      const statusDiff = statusOrder[a.status] - statusOrder[b.status];
      if (statusDiff !== 0) {
        return statusDiff;
      }
      return a.topicTitle.localeCompare(b.topicTitle);
    });

  const difficulties: AdminDifficultyActivity[] = (["easy", "medium", "expert"] as Difficulty[]).map((difficulty) => {
    const difficultySessions = normalizedSessions.filter((session) => session.difficulty === difficulty);
    const difficultyCompleted = difficultySessions.filter((session) => session.status === "completed");
    const accuracies = difficultyCompleted
      .map((session) => session.accuracyPct)
      .filter((value): value is number => typeof value === "number" && Number.isFinite(value));

    return {
      difficulty,
      sessionStarts: difficultySessions.length,
      completedSessions: difficultyCompleted.length,
      averageAccuracy: average(accuracies)
    };
  });

  const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
  const studentsWithActivity = studentsActivity.filter((student) => student.sessionStarts > 0);

  return {
    generatedAt: new Date().toISOString(),
    totalStudents: studentById.size,
    activeStudentAccounts: Array.from(studentById.values()).filter((student) => student.is_active).length,
    studentsWithActivity: studentsWithActivity.length,
    studentsWithoutActivity: studentsActivity.filter((student) => student.sessionStarts === 0).length,
    sessionStarts: normalizedSessions.length,
    completedSessions: completed.length,
    unfinishedSessions: normalizedSessions.length - completed.length,
    questionsAnswered: questionCountError ? completed.length * 10 : questionCount ?? completed.length * 10,
    averageAccuracy: average(completedAccuracy),
    lastActivityAt: newestIso(normalizedSessions.map((session) => session.completedAt || session.startedAt)),
    recentSessions: normalizedSessions.slice(0, 20),
    students: studentsActivity.sort((a, b) => {
      const aTime = a.lastActivityAt ? new Date(a.lastActivityAt).getTime() : 0;
      const bTime = b.lastActivityAt ? new Date(b.lastActivityAt).getTime() : 0;
      return bTime - aTime || a.username.localeCompare(b.username);
    }),
    topics,
    difficulties,
    attention: {
      noActivity: studentsActivity.filter((student) => student.sessionStarts === 0).slice(0, 20),
      needsSupport: studentsActivity
        .filter((student) => student.status === "needs_support")
        .sort((a, b) => (a.averageAccuracy ?? 0) - (b.averageAccuracy ?? 0))
        .slice(0, 20),
      inactiveSevenDays: studentsActivity
        .filter((student) => {
          if (!student.lastActivityAt) {
            return false;
          }
          return new Date(student.lastActivityAt).getTime() < sevenDaysAgo;
        })
        .sort((a, b) => new Date(a.lastActivityAt || 0).getTime() - new Date(b.lastActivityAt || 0).getTime())
        .slice(0, 20)
    }
  };
}

export async function getAdminAccounts() {
  const { data, error } = await withTimeout(
    supabase
      .from("profiles")
      .select("id, display_name, role, is_active, can_edit_questions, created_at")
      .eq("role", "admin")
      .order("created_at", { ascending: true }),
    "Loading admin accounts"
  );

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
  const { error } = await withTimeout(
    supabase
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
      .eq("id", args.id),
    "Saving question content"
  );

  if (error) {
    throw error;
  }
}

export async function toggleAdminProfileActive(profileId: string, isActive: boolean) {
  const { error } = await withTimeout(
    supabase
      .from("profiles")
      .update({ is_active: isActive })
      .eq("id", profileId)
      .eq("role", "admin"),
    "Updating admin account access"
  );

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

  const { data, error } = await withTimeout(query, "Loading question review data");

  if (error) {
    throw error;
  }

  return data || [];
}

export async function toggleQuestionActive(id: string, isActive: boolean) {
  const { error } = await withTimeout(
    supabase.from("questions").update({ is_active: isActive }).eq("id", id),
    "Updating question availability"
  );
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

  const { error } = await withTimeout(
    supabase
      .from("questions")
      .update(updates)
      .eq("id", id),
    "Updating question QA status"
  );

  if (error) {
    throw error;
  }
}

export async function toggleTopicEnabled(id: string, enabled: boolean) {
  const { error } = await withTimeout(
    supabase.from("topics").update({ is_enabled: enabled }).eq("id", id),
    "Updating topic availability"
  );
  if (error) {
    throw error;
  }
}

export async function callEdgeFunction<T = unknown>(name: string, body: Record<string, unknown>) {
  // Edge Functions with `verify_jwt = true` require a valid Authorization Bearer token.
  const {
    data: { session }
  } = await withTimeout(supabase.auth.getSession(), "Checking your admin session");

  if (!session?.access_token) {
    throw new Error("You must be signed in to run this admin action.");
  }

  const { data, error } = await withTimeout(
    supabase.functions.invoke(name, {
      body,
      headers: {
        Authorization: `Bearer ${session.access_token}`
      }
    }),
    `Running admin action: ${name}`
  );

  if (error) {
    throw error;
  }

  return data as T;
}
