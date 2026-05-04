import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import type { Role } from "../lib/types";

export function ProtectedRoute({
  allow,
  children
}: {
  allow: Role;
  children: ReactNode;
}) {
  const { authError, loading, logout, refreshProfile, role, session, user } = useAuth();

  if (loading) {
    return <div className="center-screen">Loading your workspace...</div>;
  }

  if (session && user && !role) {
    return (
      <div className="center-screen">
        <div className="panel stack gap-md">
          <h2>We could not load your access</h2>
          <p>{authError || "Your sign-in session exists, but your account role could not be loaded."}</p>
          <div className="inline-actions">
            <button className="primary-btn" onClick={() => void refreshProfile()}>
              Retry Access Check
            </button>
            <button className="ghost-btn" onClick={() => void logout()}>
              Sign Out
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!role) {
    return <Navigate to="/login" replace />;
  }

  if (role !== allow) {
    return <Navigate to={role === "admin" ? "/admin" : "/student"} replace />;
  }

  return <>{children}</>;
}
