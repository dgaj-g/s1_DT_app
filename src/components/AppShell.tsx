import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { getErrorMessage } from "../lib/request";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { role, profile, logout } = useAuth();
  const location = useLocation();
  const [signOutBusy, setSignOutBusy] = useState(false);
  const [signOutError, setSignOutError] = useState<string | null>(null);

  async function handleLogout() {
    setSignOutBusy(true);
    setSignOutError(null);

    try {
      await logout();
    } catch (error) {
      setSignOutError(getErrorMessage(error, "We could not sign you out just now. Please try again."));
    } finally {
      setSignOutBusy(false);
    }
  }

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
            onClick={() => void handleLogout()}
            disabled={signOutBusy}
          >
            {signOutBusy ? "Signing Out..." : "Sign Out"}
          </button>
        </div>
      </header>

      {signOutError ? (
        <div className="app-main">
          <div className="error-box">{signOutError}</div>
        </div>
      ) : null}

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
