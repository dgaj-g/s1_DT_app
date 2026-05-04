import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./hooks/useAuth";
import "./styles/global.css";

const githubPagesRedirectKey = "s1dt.githubPagesRedirect";

try {
  const redirectedRoute = window.sessionStorage.getItem(githubPagesRedirectKey);
  if (redirectedRoute) {
    window.sessionStorage.removeItem(githubPagesRedirectKey);
    const basePath = import.meta.env.BASE_URL.replace(/\/$/, "");
    const route = redirectedRoute.startsWith("/") ? redirectedRoute : `/${redirectedRoute}`;
    window.history.replaceState(null, "", `${basePath}${route}`);
  }
} catch (error) {
  // Ignore storage errors; normal app routing still works.
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
