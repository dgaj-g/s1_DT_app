import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "";
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY") || "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Content-Type": "application/json"
};

function csvEscape(value: string | number | null) {
  const raw = value === null ? "" : String(value);
  if (raw.includes(",") || raw.includes("\n") || raw.includes('"')) {
    return `"${raw.replaceAll('"', '""')}"`;
  }
  return raw;
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

    const ids = (students || []).map((row) => row.id);
    if (!ids.length) {
      return new Response(
        JSON.stringify({
          filename: `progress-${academicYearId}.csv`,
          csv: "username,difficulty,score,accuracy_pct,points_earned,streak_after,completed_at\n"
        }),
        { headers: corsHeaders }
      );
    }

    const sessions: Array<Record<string, unknown>> = [];
    const pageSize = 1000;
    let from = 0;

    while (true) {
      let sessionQuery = adminClient
        .from("sessions")
        .select(
          "id, student_id, difficulty, score, accuracy_pct, points_earned, streak_after, completed_at, academic_years:academic_year_id(code), topics:topic_id(title)"
        )
        .eq("academic_year_id", academicYearId)
        .in("student_id", ids)
        .not("completed_at", "is", null)
        .order("completed_at", { ascending: true })
        .order("id", { ascending: true })
        .range(from, from + pageSize - 1);

      if (difficulty) {
        sessionQuery = sessionQuery.eq("difficulty", difficulty);
      }

      const { data, error: sessionError } = await sessionQuery;
      if (sessionError) {
        throw sessionError;
      }

      const batch = data || [];
      sessions.push(...batch);

      if (batch.length < pageSize) {
        break;
      }
      from += pageSize;
    }

    const usernameMap = new Map<string, string>();
    for (const row of students || []) {
      usernameMap.set(row.id, row.username);
    }

    const header = [
      "username",
      "difficulty",
      "score",
      "accuracy_pct",
      "points_earned",
      "streak_after",
      "topic",
      "academic_year",
      "completed_at"
    ];

    const lines = [header.join(",")];
    for (const row of sessions) {
      const yearCode = (row.academic_years as { code?: string })?.code || "";
      const topicTitle = (row.topics as { title?: string })?.title || "";

      lines.push(
        [
          usernameMap.get(row.student_id) || "unknown",
          row.difficulty,
          row.score,
          row.accuracy_pct,
          row.points_earned,
          row.streak_after,
          topicTitle,
          yearCode,
          row.completed_at
        ]
          .map((value) => csvEscape(value as string | number | null))
          .join(",")
      );
    }

    await adminClient.from("admin_events").insert({
      admin_id: user.id,
      event_type: "export_stats_csv",
      payload_json: {
        academic_year_id: academicYearId,
        difficulty: difficulty || "all",
        rows: sessions.length
      }
    });

    const csv = `${lines.join("\n")}\n`;
    const filename = `progress-${yearCodeSafe(academicYearId)}-${new Date().toISOString().slice(0, 10)}.csv`;

    return new Response(JSON.stringify({ filename, csv }), {
      headers: corsHeaders
    });
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
