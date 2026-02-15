import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "";
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY") || "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Content-Type": "application/json"
};

function randomReadablePassword(length = 8) {
  const alphabet = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(length));
  let out = "";
  for (let i = 0; i < length; i += 1) {
    out += alphabet[bytes[i] % alphabet.length];
  }
  return out;
}

function csvEscape(value: string) {
  if (value.includes(",") || value.includes("\n") || value.includes("\"")) {
    return `"${value.replaceAll('"', '""')}"`;
  }
  return value;
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

    const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    const body = await request.json().catch(() => ({}));
    const yearCode = body.academic_year_code || "unknown";

    const { data: accounts, error: accountError } = await adminClient
      .from("student_accounts")
      .select("id, username, auth_user_id")
      .eq("is_active", true)
      .order("account_number", { ascending: true });

    if (accountError) {
      throw accountError;
    }

    const rows: Array<{ username: string; password: string }> = [];

    for (const account of accounts || []) {
      const password = randomReadablePassword(8);
      const { error: updateError } = await adminClient.auth.admin.updateUserById(account.auth_user_id, {
        password
      });

      if (!updateError) {
        rows.push({ username: account.username, password });
      }
    }

    await adminClient.from("admin_events").insert({
      admin_id: user.id,
      event_type: "bulk_rotate_student_passwords",
      payload_json: {
        academic_year_code: yearCode,
        count: rows.length
      }
    });

    const csv = ["username,password", ...rows.map((row) => `${csvEscape(row.username)},${csvEscape(row.password)}`)].join("\n");

    return new Response(
      JSON.stringify({
        year: yearCode,
        generated_at: new Date().toISOString(),
        rows,
        csv
      }),
      { headers: corsHeaders }
    );
  } catch (error) {
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }), {
      status: 500,
      headers: corsHeaders
    });
  }
});
