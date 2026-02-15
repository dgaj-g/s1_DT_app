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
    const start = Number(body.start || 1);
    const end = Number(body.end || 100);
    const prefix = String(body.prefix || "s1dt");

    if (start < 1 || end > 100 || start > end) {
      return new Response(JSON.stringify({ error: "Invalid range. Must be within 1..100." }), { status: 400, headers: corsHeaders });
    }

    const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

    const { data: existingAccounts } = await adminClient
      .from("student_accounts")
      .select("id, username, auth_user_id, account_number")
      .gte("account_number", start)
      .lte("account_number", end);

    const accountMap = new Map<number, { id: string; username: string; auth_user_id: string }>();
    for (const row of existingAccounts || []) {
      accountMap.set(row.account_number, {
        id: row.id,
        username: row.username,
        auth_user_id: row.auth_user_id
      });
    }

    const createdUsers: Array<{ username: string; email: string; password: string }> = [];
    const listed = await adminClient.auth.admin.listUsers({ page: 1, perPage: 1000 });
    const authByEmail = new Map<string, string>();
    for (const existing of listed.data.users) {
      if (existing.email) {
        authByEmail.set(existing.email.toLowerCase(), existing.id);
      }
    }

    for (let n = start; n <= end; n += 1) {
      const username = `${prefix}${String(n).padStart(3, "0")}`;
      const email = `${username}@students.local`;

      let authUserId = accountMap.get(n)?.auth_user_id;

      if (!authUserId) {
        authUserId = authByEmail.get(email.toLowerCase());
      }

      if (!authUserId) {
        const password = randomReadablePassword(8);
        const { data: created, error: createError } = await adminClient.auth.admin.createUser({
          email,
          password,
          email_confirm: true,
          user_metadata: {
            role: "student",
            display_name: username
          }
        });

        if (createError || !created.user) {
          throw createError || new Error(`Could not create user ${email}`);
        }

        authUserId = created.user.id;
        authByEmail.set(email.toLowerCase(), authUserId);
        createdUsers.push({ username, email, password });
      }

      const { error: upsertError } = await adminClient.from("student_accounts").upsert(
        {
          auth_user_id: authUserId,
          username,
          account_number: n,
          is_active: true
        },
        { onConflict: "username" }
      );

      if (upsertError) {
        throw upsertError;
      }
    }

    await adminClient.from("admin_events").insert({
      admin_id: user.id,
      event_type: "seed_or_repair_student_pool",
      payload_json: {
        start,
        end,
        prefix,
        created_users: createdUsers.length
      }
    });

    return new Response(
      JSON.stringify({
        repaired_range: `${start}-${end}`,
        created_users: createdUsers,
        message: "Student pool is seeded/repaired."
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
