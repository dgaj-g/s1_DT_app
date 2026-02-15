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
  const { role, loading } = useAuth();

  if (loading) {
    return <div className="center-screen">Loading your workspace...</div>;
  }

  if (!role) {
    return <Navigate to="/login" replace />;
  }

  if (role !== allow) {
    return <Navigate to={role === "admin" ? "/admin" : "/student"} replace />;
  }

  return <>{children}</>;
}
