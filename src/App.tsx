import { Navigate, Route, Routes } from "react-router-dom";
import { LoginPage } from "./pages/LoginPage";
import { StudentTopicPage } from "./pages/StudentTopicPage";
import { StudentSessionPage } from "./pages/StudentSessionPage";
import { StudentSummaryPage } from "./pages/StudentSummaryPage";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { AppShell } from "./components/AppShell";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./hooks/useAuth";

export default function App() {
  const { role } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/student"
        element={
          <ProtectedRoute allow="student">
            <AppShell>
              <StudentTopicPage />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/session/:difficulty"
        element={
          <ProtectedRoute allow="student">
            <AppShell>
              <StudentSessionPage />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/summary/:sessionId"
        element={
          <ProtectedRoute allow="student">
            <AppShell>
              <StudentSummaryPage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin"
        element={
          <ProtectedRoute allow="admin">
            <AppShell>
              <AdminDashboardPage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      <Route
        path="*"
        element={
          role === "student" ? (
            <Navigate to="/student" replace />
          ) : role === "admin" ? (
            <Navigate to="/admin" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
}
