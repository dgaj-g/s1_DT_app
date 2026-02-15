import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "";
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY") || "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Content-Type": "application/json"
};

function csvEscape(value: string | number | boolean | null) {
  const raw = value === null ? "" : String(value);
  if (raw.includes(",") || raw.includes("\n") || raw.includes('"')) {
    return `"${raw.replaceAll('"', '""')}"`;
  }
  return raw;
}

function chunk<T>(values: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < values.length; i += size) {
    out.push(values.slice(i, i + size));
  }
  return out;
}

Deno.serve(async (request) => {
  if (request.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const authHeader = request.headers.get("Authorization");
    if (!authHeader) {
      return new Response(JSON.stringify({ error: "Missing auth header" }), { status: 401, headers: corsHeaders });
    }

    const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      global: { headers: { Authorization: authHeader } }
    });

    const {
      data: { user },
      error: userError
    } = await userClient.auth.getUser();

    if (userError || !user) {
      return new Response(JSON.stringify({ error: "Unauthenticated" }), { status: 401, headers: corsHeaders });
    }

    const { data: profile } = await userClient
      .from("profiles")
      .select("id, role, is_active")
      .eq("id", user.id)
      .single();

    if (!profile || profile.role !== "admin" || profile.is_active !== true) {
      return new Response(JSON.stringify({ error: "Admin role required" }), { status: 403, headers: corsHeaders });
    }

    const body = await request.json().catch(() => ({}));
    const academicYearId = body.academic_year_id as string;
    const difficulty = body.difficulty as string | null;
    const usernameFrom = (body.username_from as string) || "s1dt001";
    const usernameTo = (body.username_to as string) || "s1dt100";

    if (!academicYearId) {
      return new Response(JSON.stringify({ error: "academic_year_id is required" }), { status: 400, headers: corsHeaders });
    }

    const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

    const { data: students, error: studentError } = await adminClient
      .from("student_accounts")
      .select("id, username")
      .gte("username", usernameFrom)
      .lte("username", usernameTo)
      .order("username", { ascending: true });

    if (studentError) {
      throw studentError;
    }

    const studentIds = (students || []).map((row) => row.id);
    const usernameById = new Map<string, string>();
    for (const student of students || []) {
      usernameById.set(student.id, student.username);
    }

    const header = [
      "username",
      "session_id",
      "question_position",
      "question_id",
      "topic",
      "difficulty",
      "question_format",
      "question_stem",
      "correct_answer_json",
      "student_answer_json",
      "is_correct",
      "response_time_ms",
      "hint_used",
      "question_tags_json",
      "source_ref",
      "academic_year",
      "completed_at"
    ];

    if (!studentIds.length) {
      return new Response(
        JSON.stringify({
          filename: `detailed-question-report-${yearCodeSafe(academicYearId)}-${new Date().toISOString().slice(0, 10)}.csv`,
          csv: `${header.join(",")}\n`
        }),
        { headers: corsHeaders }
      );
    }

    const sessions: Array<Record<string, unknown>> = [];
    const pageSize = 1000;
    let from = 0;

    while (true) {
      let query = adminClient
        .from("sessions")
        .select(
          "id, student_id, difficulty, completed_at, academic_years:academic_year_id(code), topics:topic_id(title)"
        )
        .eq("academic_year_id", academicYearId)
        .in("student_id", studentIds)
        .not("completed_at", "is", null)
        .order("completed_at", { ascending: true })
        .order("id", { ascending: true })
        .range(from, from + pageSize - 1);

      if (difficulty) {
        query = query.eq("difficulty", difficulty);
      }

      const { data, error } = await query;
      if (error) {
        throw error;
      }

      const batch = data || [];
      sessions.push(...batch);

      if (batch.length < pageSize) {
        break;
      }
      from += pageSize;
    }

    if (!sessions.length) {
      return new Response(
        JSON.stringify({
          filename: `detailed-question-report-${yearCodeSafe(academicYearId)}-${new Date().toISOString().slice(0, 10)}.csv`,
          csv: `${header.join(",")}\n`
        }),
        { headers: corsHeaders }
      );
    }

    const sessionMeta = new Map<string, Record<string, unknown>>();
    for (const session of sessions) {
      sessionMeta.set(String(session.id), session);
    }

    const sessionIds = sessions.map((row) => String(row.id));
    const allQuestionRows: Array<Record<string, unknown>> = [];

    for (const sessionChunk of chunk(sessionIds, 200)) {
      let rowFrom = 0;
      while (true) {
        const { data, error } = await adminClient
          .from("session_questions")
          .select(
            "session_id, question_id, position, student_answer_json, is_correct, response_time_ms, hint_used, questions:question_id(id, stem, format, source_ref, tags_json, correct_answer_json)"
          )
          .in("session_id", sessionChunk)
          .order("session_id", { ascending: true })
          .order("position", { ascending: true })
          .range(rowFrom, rowFrom + pageSize - 1);

        if (error) {
          throw error;
        }

        const batch = data || [];
        allQuestionRows.push(...batch);

        if (batch.length < pageSize) {
          break;
        }
        rowFrom += pageSize;
      }
    }

    allQuestionRows.sort((a, b) => {
      const sessionA = sessionMeta.get(String(a.session_id));
      const sessionB = sessionMeta.get(String(b.session_id));
      const timeA = new Date(String(sessionA?.completed_at || "")).getTime();
      const timeB = new Date(String(sessionB?.completed_at || "")).getTime();
      if (timeA !== timeB) {
        return timeA - timeB;
      }

      const sA = String(a.session_id);
      const sB = String(b.session_id);
      if (sA !== sB) {
        return sA.localeCompare(sB);
      }

      const pA = Number(a.position || 0);
      const pB = Number(b.position || 0);
      return pA - pB;
    });

    const lines = [header.join(",")];
    for (const row of allQuestionRows) {
      const session = sessionMeta.get(String(row.session_id));
      if (!session) {
        continue;
      }

      const question = (row.questions as Record<string, unknown>) || {};
      const yearCode = ((session.academic_years as Record<string, unknown>)?.code as string) || "";
      const topicTitle = ((session.topics as Record<string, unknown>)?.title as string) || "";

      lines.push(
        [
          usernameById.get(String(session.student_id)) || "unknown",
          String(row.session_id || ""),
          Number(row.position || 0),
          String(row.question_id || ""),
          topicTitle,
          String(session.difficulty || ""),
          String(question.format || ""),
          String(question.stem || ""),
          JSON.stringify(question.correct_answer_json || {}),
          JSON.stringify(row.student_answer_json || {}),
          row.is_correct === null ? "" : Boolean(row.is_correct),
          row.response_time_ms === null ? "" : Number(row.response_time_ms || 0),
          row.hint_used === null ? "" : Boolean(row.hint_used),
          JSON.stringify(question.tags_json || []),
          String(question.source_ref || ""),
          yearCode,
          String(session.completed_at || "")
        ]
          .map((value) => csvEscape(value as string | number | boolean | null))
          .join(",")
      );
    }

    await adminClient.from("admin_events").insert({
      admin_id: user.id,
      event_type: "export_detailed_question_report_csv",
      payload_json: {
        academic_year_id: academicYearId,
        difficulty: difficulty || "all",
        rows: allQuestionRows.length
      }
    });

    const csv = `${lines.join("\n")}\n`;
    const filename = `detailed-question-report-${yearCodeSafe(academicYearId)}-${new Date().toISOString().slice(0, 10)}.csv`;

    return new Response(JSON.stringify({ filename, csv }), { headers: corsHeaders });
  } catch (error) {
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }), {
      status: 500,
      headers: corsHeaders
    });
  }
});

function yearCodeSafe(value: string) {
  return value.replace(/[^a-zA-Z0-9_-]/g, "_");
}
