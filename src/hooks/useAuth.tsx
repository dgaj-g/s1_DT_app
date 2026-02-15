import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { Session, User } from "@supabase/supabase-js";
import { supabase } from "../lib/supabase";
import type { Profile, Role } from "../lib/types";

interface AuthContextValue {
  user: User | null;
  session: Session | null;
  profile: Profile | null;
  role: Role | null;
  loading: boolean;
  loginWithIdentifier: (identifier: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function toEmailIdentifier(raw: string): string {
  const trimmed = raw.trim().toLowerCase();
  if (trimmed.includes("@")) {
    return trimmed;
  }

  if (/^s1dt\d{3}$/.test(trimmed)) {
    return `${trimmed}@students.local`;
  }

  return `${trimmed}@school.local`;
}

async function getProfile(userId: string): Promise<Profile | null> {
  const { data, error } = await supabase
    .from("profiles")
    .select("id, role, display_name, is_active, can_edit_questions")
    .eq("id", userId)
    .single();

  if (error) {
    return null;
  }

  return data as Profile;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshProfile = useCallback(async () => {
    if (!user) {
      setProfile(null);
      return;
    }

    const next = await getProfile(user.id);
    setProfile(next);
  }, [user]);

  useEffect(() => {
    let mounted = true;

    async function boot() {
      const {
        data: { session: activeSession }
      } = await supabase.auth.getSession();

      if (!mounted) {
        return;
      }

      setSession(activeSession);
      setUser(activeSession?.user ?? null);

      if (activeSession?.user) {
        const next = await getProfile(activeSession.user.id);
        if (mounted) {
          setProfile(next);
        }
      }

      if (mounted) {
        setLoading(false);
      }
    }

    boot();

    const { data: listener } = supabase.auth.onAuthStateChange(async (_event, nextSession) => {
      setSession(nextSession);
      setUser(nextSession?.user ?? null);

      if (nextSession?.user) {
        const next = await getProfile(nextSession.user.id);
        setProfile(next);
      } else {
        setProfile(null);
      }

      setLoading(false);
    });

    return () => {
      mounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  const loginWithIdentifier = useCallback(async (identifier: string, password: string) => {
    const email = toEmailIdentifier(identifier);

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      throw error;
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      session,
      profile,
      role: profile?.role ?? null,
      loading,
      loginWithIdentifier,
      logout,
      refreshProfile
    }),
    [loading, loginWithIdentifier, logout, profile, refreshProfile, session, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}
