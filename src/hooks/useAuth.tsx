import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { Session, User } from "@supabase/supabase-js";
import { recordStudentLogin } from "../lib/api";
import { supabase } from "../lib/supabase";
import { getErrorMessage, withTimeout } from "../lib/request";
import type { Profile, Role } from "../lib/types";

interface AuthContextValue {
  user: User | null;
  session: Session | null;
  profile: Profile | null;
  role: Role | null;
  loading: boolean;
  authError: string | null;
  loginWithIdentifier: (identifier: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  retryAuth: () => Promise<void>;
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
  const { data, error } = await withTimeout(
    supabase
      .from("profiles")
      .select("id, role, display_name, is_active, can_edit_questions")
      .eq("id", userId)
      .single(),
    "Loading your account profile"
  );

  if (error) {
    throw error;
  }

  return data as Profile;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [booting, setBooting] = useState(true);
  const [profileLoading, setProfileLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const profileRequestRef = useRef(0);
  const recordedStudentAccessRef = useRef<Set<string>>(new Set());

  const refreshProfile = useCallback(async () => {
    if (!user) {
      profileRequestRef.current += 1;
      setProfile(null);
      setProfileLoading(false);
      setAuthError(null);
      return;
    }

    const requestId = profileRequestRef.current + 1;
    profileRequestRef.current = requestId;
    setProfileLoading(true);
    setAuthError(null);

    try {
      const next = await getProfile(user.id);

      if (profileRequestRef.current !== requestId) {
        return;
      }

      if (!next) {
        throw new Error("We could not load your account access. Please try again.");
      }

      setProfile(next);
    } catch (error) {
      if (profileRequestRef.current !== requestId) {
        return;
      }

      setProfile(null);
      setAuthError(getErrorMessage(error, "We could not load your account access. Please try again."));
    } finally {
      if (profileRequestRef.current === requestId) {
        setProfileLoading(false);
      }
    }
  }, [user]);

  const retryAuth = useCallback(async () => {
    setBooting(true);
    setAuthError(null);
    profileRequestRef.current += 1;
    setProfile(null);
    setProfileLoading(false);

    try {
      const {
        data: { session: activeSession }
      } = await withTimeout(supabase.auth.getSession(), "Checking your saved sign-in");

      setSession(activeSession);
      setUser(activeSession?.user ?? null);
    } catch (error) {
      setSession(null);
      setUser(null);
      setProfile(null);
      setAuthError(getErrorMessage(error, "Could not restore your sign-in session."));
    } finally {
      setBooting(false);
    }
  }, []);

  useEffect(() => {
    let mounted = true;

    void retryAuth();

    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      if (!mounted) {
        return;
      }

      profileRequestRef.current += 1;
      setSession(nextSession);
      setUser(nextSession?.user ?? null);
      setAuthError(null);
      setProfile(null);

      if (nextSession?.user) {
        setProfileLoading(true);
      } else {
        setProfileLoading(false);
      }
    });

    return () => {
      mounted = false;
      profileRequestRef.current += 1;
      listener.subscription.unsubscribe();
    };
  }, [retryAuth]);

  useEffect(() => {
    if (booting) {
      return;
    }

    if (!user) {
      setProfile(null);
      setProfileLoading(false);
      return;
    }

    void refreshProfile();
  }, [booting, refreshProfile, user]);


  useEffect(() => {
    if (booting || !user) {
      return;
    }

    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Europe/London";
    const accessKey = `${user.id}:${new Date().toISOString().slice(0, 10)}`;

    if (recordedStudentAccessRef.current.has(accessKey)) {
      return;
    }

    recordedStudentAccessRef.current.add(accessKey);
    void recordStudentLogin(timezone).catch((caught) => {
      console.warn("Student login was not recorded.", caught);
    });
  }, [booting, user]);

  const loginWithIdentifier = useCallback(async (identifier: string, password: string) => {
    const email = toEmailIdentifier(identifier);
    setAuthError(null);

    const { error } = await withTimeout(
      supabase.auth.signInWithPassword({
        email,
        password
      }),
      "Signing you in"
    );

    if (error) {
      throw error;
    }

  }, []);

  const logout = useCallback(async () => {
    const { error } = await withTimeout(supabase.auth.signOut(), "Signing you out");
    if (error) {
      throw error;
    }

    setProfile(null);
    setAuthError(null);
  }, []);

  const loading = booting || profileLoading;

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      session,
      profile,
      role: profile?.role ?? null,
      loading,
      authError,
      loginWithIdentifier,
      logout,
      refreshProfile,
      retryAuth
    }),
    [authError, loading, loginWithIdentifier, logout, profile, refreshProfile, retryAuth, session, user]
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
