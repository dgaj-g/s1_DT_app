import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const navigate = useNavigate();
  const { loginWithIdentifier, role, loading } = useAuth();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (role === "student") {
      navigate("/student", { replace: true });
    }
    if (role === "admin") {
      navigate("/admin", { replace: true });
    }
  }, [navigate, role]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);

    try {
      await loginWithIdentifier(identifier, password);
    } catch {
      setError("Sign-in failed. Check your username/email and password.");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return <div className="center-screen">Loading login...</div>;
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>Digital Technology Revision</h1>
        <p>Sign in as student (`s1dt001` to `s1dt100`) or teacher admin.</p>

        <form onSubmit={handleSubmit} className="stack gap-md">
          <label className="stack gap-xs">
            <span>Username or admin email</span>
            <input
              required
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              placeholder="e.g. s1dt001"
            />
          </label>

          <label className="stack gap-xs">
            <span>Password</span>
            <input
              required
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
            />
          </label>

          {error ? <div className="error-box">{error}</div> : null}

          <button type="submit" disabled={busy} className="primary-btn">
            {busy ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
