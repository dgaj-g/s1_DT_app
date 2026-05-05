import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { getSession, getSessionQuestions } from "../lib/api";
import { cleanQuestionStemForDisplay } from "../lib/questionDisplay";
import { getErrorMessage } from "../lib/request";
import { getAdaptiveRecommendation } from "../lib/scoring";
import type { Difficulty, SessionRecord } from "../lib/types";

export function StudentSummaryPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [search] = useSearchParams();
  const navigate = useNavigate();

  const studentId = search.get("student") || "";
  const yearId = search.get("year") || "";

  const [session, setSession] = useState<SessionRecord | null>(null);
  const [rows, setRows] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!sessionId) {
        if (!cancelled) {
          setError("Session missing");
          setLoading(false);
        }
        return;
      }

      try {
        if (!cancelled) {
          setLoading(true);
          setError(null);
        }
        const [sessionRow, answerRows] = await Promise.all([getSession(sessionId), getSessionQuestions(sessionId)]);
        if (!cancelled) {
          setSession(sessionRow);
          setRows(answerRows as Array<Record<string, unknown>>);
        }
      } catch (caught) {
        if (!cancelled) {
          setError(getErrorMessage(caught, "Could not load summary."));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [reloadKey, sessionId]);

  const recommendation = useMemo(() => {
    if (!session) {
      return null;
    }
    return getAdaptiveRecommendation(session.difficulty as Difficulty, Number(session.accuracy_pct || 0));
  }, [session]);

  const recommendationLabel = useMemo(() => {
    if (!session || !recommendation) {
      return "";
    }

    if (recommendation.nextDifficulty === session.difficulty) {
      return `Practice This Level Again (${recommendation.nextDifficulty.toUpperCase()})`;
    }

    return `Try Recommended Level (${recommendation.nextDifficulty.toUpperCase()})`;
  }, [recommendation, session]);

  if (loading) {
    return <div className="center-screen">Loading session summary...</div>;
  }

  if (error || !session) {
    return (
      <div className="panel stack gap-md">
        <div className="error-box">{error || "Session not found."}</div>
        <div className="inline-actions">
          <button className="primary-btn" onClick={() => setReloadKey((value) => value + 1)}>
            Retry Summary Load
          </button>
          <button className="ghost-btn" onClick={() => navigate("/student")}>
            Back to Student Home
          </button>
        </div>
      </div>
    );
  }

  const total = rows.length;
  const correct = rows.filter((row) => Boolean(row.is_correct)).length;

  return (
    <section className="stack gap-md">
      <article className="panel hero-panel">
        <h2>Session complete</h2>
        <p>
          Score: <strong>{correct}</strong> / {total}
        </p>
        <p>
          Accuracy: <strong>{Math.round(Number(session.accuracy_pct || 0))}%</strong>
        </p>
        <p>
          Streak after session: <strong>{session.streak_after ?? 0}</strong>
        </p>
      </article>

      {recommendation ? (
        <article className="panel">
          <h3>{recommendation.headline}</h3>
          <p>{recommendation.detail}</p>
        </article>
      ) : null}

      <article className="panel">
        <h3>Question-by-question review</h3>
        <ul className="review-list">
          {rows.map((row, index) => {
            const question = row.questions as Record<string, unknown> | null;
            return (
              <li key={String(row.id || index)}>
                <strong>Q{index + 1}.</strong> {cleanQuestionStemForDisplay(question?.stem || "Question")}
                <span className={row.is_correct ? "good" : "bad"}>{row.is_correct ? "Correct" : "Review"}</span>
              </li>
            );
          })}
        </ul>
      </article>

      <div className="inline-actions">
        <button
          className="ghost-btn"
          onClick={() => navigate("/student")}
        >
          Back to Student Home
        </button>
        {recommendation ? (
          <button
            className="primary-btn"
            onClick={() =>
              navigate(
                `/student/session/${recommendation.nextDifficulty}?topic=${encodeURIComponent(session.topic_id)}&student=${encodeURIComponent(studentId)}&year=${encodeURIComponent(yearId)}&tz=Europe%2FLondon`
              )
            }
          >
            {recommendationLabel}
          </button>
        ) : null}
      </div>
    </section>
  );
}
