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
