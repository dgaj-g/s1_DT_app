import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { role, profile, logout } = useAuth();
  const location = useLocation();

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>S1 Digital Technology Revision</h1>
          <p>CCEA Unit 1 Adaptive Practice</p>
        </div>
        <div className="header-actions">
          {role === "student" ? (
            <Link to="/student" className="ghost-btn">
              Student Home
            </Link>
          ) : null}
          {role === "admin" ? (
            <Link to="/admin" className="ghost-btn">
              Admin Dashboard
            </Link>
          ) : null}
          <button
            className="ghost-btn"
            onClick={() => {
              void logout();
            }}
          >
            Sign Out
          </button>
        </div>
      </header>

      <main className="app-main">{children}</main>

      <footer className="app-footer">
        <span>
          Logged in as <strong>{profile?.display_name || "User"}</strong>
        </span>
        <span>{location.pathname}</span>
      </footer>
    </div>
  );
}
