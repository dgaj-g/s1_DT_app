import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { QuestionRenderer } from "../components/QuestionRenderer";
import {
  canStartSession,
  createSession,
  getStudentSessions,
  pickSessionQuestions,
  saveSessionSubmission
} from "../lib/api";
import { localDateISO } from "../lib/date";
import { computeStreak, evaluateAnswer, getMatchCorrections } from "../lib/scoring";
import type { Difficulty, Question, SessionQuestionAnswer } from "../lib/types";

export function StudentSessionPage() {
  const { difficulty } = useParams<{ difficulty: Difficulty }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const topicId = searchParams.get("topic") || "";
  const studentId = searchParams.get("student") || "";
  const academicYearId = searchParams.get("year") || "";
  const timezone = searchParams.get("tz") || "Europe/London";

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState<Record<string, unknown>>({});
  const [responses, setResponses] = useState<SessionQuestionAnswer[]>([]);
  const [evaluated, setEvaluated] = useState(false);
  const [lastCorrect, setLastCorrect] = useState<boolean>(false);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [loading, setLoading] = useState(true);
  const [lockedMessage, setLockedMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const activeQuestion = questions[currentIndex];
  const isLast = currentIndex === questions.length - 1;

  const progressLabel = useMemo(
    () => `Question ${Math.min(currentIndex + 1, questions.length)} of ${questions.length || 0}`,
    [currentIndex, questions.length]
  );
  const matchCorrections = useMemo(() => {
    if (!evaluated || !activeQuestion || lastCorrect || activeQuestion.format !== "match_table") {
      return [];
    }
    return getMatchCorrections(activeQuestion, answer);
  }, [activeQuestion, answer, evaluated, lastCorrect]);

  useEffect(() => {
    async function boot() {
      if (!difficulty || !topicId || !studentId || !academicYearId) {
        setError("Session parameters are incomplete. Return to student home.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const today = localDateISO(timezone);
        const allowed = await canStartSession({
          studentId,
          academicYearId,
          difficulty,
          localDate: today
        });

        if (!allowed) {
          setLockedMessage(
            "You have completed 3 sessions in this difficulty today. This level unlocks again tomorrow."
          );
          setLoading(false);
          return;
        }

        const [session, picked] = await Promise.all([
          createSession({
            studentId,
            academicYearId,
            topicId,
            difficulty
          }),
          pickSessionQuestions({
            studentId,
            topicId,
            difficulty,
            count: 10
          })
        ]);

        setSessionId(session.id);
        setQuestions(picked);
        setStartTime(Date.now());
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unable to start this session.");
      } finally {
        setLoading(false);
      }
    }

    void boot();
  }, [academicYearId, difficulty, studentId, timezone, topicId]);

  function checkAnswer() {
    if (!activeQuestion) {
      return;
    }
    if (evaluated) {
      return;
    }

    const isCorrect = evaluateAnswer(activeQuestion, answer);
    const responseTimeMs = Date.now() - startTime;

    setResponses((prev) => [
      ...prev,
      {
        questionId: activeQuestion.id,
        position: currentIndex + 1,
        answer,
        isCorrect,
        responseTimeMs,
        hintUsed: false
      }
    ]);

    setLastCorrect(isCorrect);
    setEvaluated(true);
  }

  async function nextOrFinish() {
    if (!activeQuestion) {
      return;
    }

    if (!evaluated) {
      return;
    }

    if (!isLast) {
      setCurrentIndex((value) => value + 1);
      setAnswer({});
      setEvaluated(false);
      setStartTime(Date.now());
      return;
    }

    if (!sessionId) {
      setError("Session record missing. Cannot save progress.");
      return;
    }

    try {
      setSaving(true);
      const completeResponses = responses;
      const correctCount = completeResponses.filter((entry) => entry.isCorrect).length;
      const score = correctCount;
      const accuracyPct = questions.length ? Math.round((correctCount / questions.length) * 100) : 0;
      const points = correctCount;

      const previous = await getStudentSessions({ studentId, academicYearId });
      const priorStreak = computeStreak(previous);
      const streakAfter = accuracyPct >= 60 ? priorStreak + 1 : 0;

      await saveSessionSubmission({
        sessionId,
        studentId,
        academicYearId,
        localDate: localDateISO(timezone),
        answers: completeResponses,
        accuracyPct,
        score,
        pointsEarned: points,
        streakAfter
      });

      navigate(`/student/summary/${sessionId}?student=${studentId}&year=${academicYearId}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not save session.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div className="center-screen">Preparing your session...</div>;
  }

  if (lockedMessage) {
    return (
      <div className="panel stack gap-md">
        <h2>Difficulty locked for today</h2>
        <p>{lockedMessage}</p>
        <button className="primary-btn" onClick={() => navigate("/student")}>Back to Student Home</button>
      </div>
    );
  }

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  if (!activeQuestion) {
    return <div className="error-box">No questions available for this difficulty yet.</div>;
  }

  return (
    <section className="stack gap-md">
      <div className="panel">
        <div className="session-header">
          <h2>{difficulty?.toUpperCase()} Session</h2>
          <span className="progress-pill">{progressLabel}</span>
        </div>
        <p className="question-stem">{activeQuestion.stem}</p>

        <QuestionRenderer
          question={activeQuestion}
          answer={answer}
          onChange={setAnswer}
          isLocked={evaluated}
          showFeedback={evaluated}
        />

        {!evaluated ? (
          <div className="question-actions">
            <button className="primary-btn" onClick={checkAnswer}>
              Check Answer
            </button>
          </div>
        ) : (
          <div className="feedback-box">
            <p className={lastCorrect ? "good" : "bad"}>{lastCorrect ? "Correct" : "Not quite right"}</p>
            <p>{activeQuestion.explanation}</p>
            {!lastCorrect && matchCorrections.length > 0 ? (
              <div className="correction-box">
                <p>Check these corrections:</p>
                <ul className="correction-list">
                  {matchCorrections.map((item) => (
                    <li key={item.left}>
                      <strong>{item.left}</strong>: your match was{" "}
                      <em>{item.selected || "not answered"}</em>; correct match is{" "}
                      <em>{item.expected}</em>.
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
            <button className="primary-btn" onClick={() => void nextOrFinish()} disabled={saving}>
              {saving ? "Saving..." : isLast ? "Finish Session" : "Next Question"}
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
