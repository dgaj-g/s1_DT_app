import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { QuestionRenderer } from "../components/QuestionRenderer";
import {
  canStartSession,
  completeSessionV2,
  createSession,
  getStudentSessions,
  gradeSessionQuestionV2,
  isV2RuntimeUnavailableError,
  pickSessionQuestions,
  saveSessionSubmission,
  startSessionV2
} from "../lib/api";
import { localDateISO } from "../lib/date";
import { cleanQuestionStemForDisplay } from "../lib/questionDisplay";
import { getErrorMessage } from "../lib/request";
import { computeStreak, evaluateAnswer, getMatchCorrections } from "../lib/scoring";
import type {
  Difficulty,
  Question,
  RuntimeChoice,
  RuntimeQuestionFeedback,
  RuntimeResponseSchema,
  RuntimeSessionQuestion,
  SessionQuestionAnswer
} from "../lib/types";

type SessionMode = "legacy" | "v2";

function toRuntimeQuestionFromLegacy(question: Question, position: number): RuntimeSessionQuestion {
  const options = (question.options_json || {}) as Record<string, unknown>;
  const choices = Array.isArray(options.choices) ? (options.choices as string[]) : [];
  const pairs = Array.isArray(options.pairs) ? (options.pairs as Array<{ left: string; right: string }>) : [];
  const items = Array.isArray(options.items) ? (options.items as string[]) : [];

  let responseSchema: RuntimeResponseSchema = { kind: "unsupported" };

  switch (question.format) {
    case "mcq":
      responseSchema = {
        kind: "single_choice",
        choices: choices.map((choice) => ({ id: choice, label: choice }))
      };
      break;
    case "fill_gap":
      responseSchema = {
        kind: "fill_gap",
        gaps: [{ id: "gap1", label: "Gap 1" }]
      };
      break;
    case "short_text":
    case "structured_response":
      responseSchema = {
        kind: "short_text",
        placeholder: "Type your answer",
        max_length: 180
      };
      break;
    case "match_table": {
      const runtimeChoices: RuntimeChoice[] = choices.length
        ? choices.map((choice) => ({ id: choice, label: choice }))
        : pairs.map((pair) => ({ id: pair.right, label: pair.right }));

      responseSchema = {
        kind: "match_table",
        rows: pairs.map((pair) => ({ id: pair.left, label: pair.left })),
        choices: runtimeChoices
      };
      break;
    }
    case "drag_drop":
      responseSchema = {
        kind: "ordering",
        items: items.map((item) => ({ id: item, label: item }))
      };
      break;
    case "diagram_label": {
      const diagramKey = typeof options.diagram_key === "string" ? options.diagram_key : undefined;
      const marker =
        typeof options.marker === "string"
          ? options.marker
          : typeof options.callout === "string"
            ? options.callout
            : undefined;
      responseSchema = {
        kind: "diagram_label",
        input_mode: choices.length ? "single_choice" : "text",
        diagram_key: diagramKey,
        marker,
        choices: choices.length ? choices.map((choice) => ({ id: choice, label: choice })) : [],
        placeholder: "Type your label"
      };
      break;
    }
    case "multi_select":
      responseSchema = {
        kind: "multi_select",
        choices: choices.map((choice) => ({ id: choice, label: choice })),
        min_select: 1,
        max_select: choices.length
      };
      break;
    case "true_false":
      responseSchema = {
        kind: "true_false",
        statement: cleanQuestionStemForDisplay(question.stem),
        true_label: "True",
        false_label: "False"
      };
      break;
    default:
      responseSchema = { kind: "unsupported" };
  }

  return {
    session_item_id: question.id,
    question_id: question.id,
    topic_id: question.topic_id,
    difficulty: question.difficulty,
    adaptive_tier: "core",
    format: question.format === "structured_response" ? "short_text" : (question.format as RuntimeSessionQuestion["format"]),
    max_marks: 1,
    family_code: null,
    stem: cleanQuestionStemForDisplay(question.stem),
    prompt_blocks: [],
    assets: [],
    response_schema: responseSchema,
    autograde_rules: {},
    explanation: question.explanation,
    tags: Array.isArray(question.tags_json) ? question.tags_json : [],
    objective_ids: [],
    position,
    grading_status: "pending",
    student_answer: {},
    is_correct: null,
    marks_awarded: 0,
    marks_available: 1,
    feedback: null
  };
}

function getResumeIndex(questions: RuntimeSessionQuestion[]) {
  const pendingIndex = questions.findIndex((question) => question.grading_status !== "graded");
  if (pendingIndex >= 0) {
    return pendingIndex;
  }
  return questions.length > 0 ? questions.length - 1 : 0;
}

function buildRuntimeMatchCorrections(
  question: RuntimeSessionQuestion,
  feedback?: RuntimeQuestionFeedback | null,
  answer?: Record<string, unknown>
) {
  const schema = question.response_schema;
  if (schema.kind !== "match_table") {
    return [];
  }

  const corrections = Array.isArray(feedback?.corrections) ? feedback?.corrections : [];
  const selectedPairs = ((answer || {}).pairs || {}) as Record<string, string>;

  return corrections
    .filter((item): item is Record<string, unknown> => !!item && typeof item === "object")
    .map((item) => {
      const rowId = typeof item.row_id === "string" ? item.row_id : "";
      const expectedChoiceId = typeof item.expected_choice_id === "string" ? item.expected_choice_id : "";
      const selectedChoiceId = typeof item.selected_choice_id === "string" ? item.selected_choice_id : "";
      const row = schema.rows.find((entry) => entry.id === rowId);
      const expectedChoice = schema.choices.find((entry) => entry.id === expectedChoiceId);
      const selectedChoice = schema.choices.find((entry) => entry.id === selectedChoiceId);

      return {
        left: row?.label || rowId,
        selected: selectedChoice?.label || selectedPairs[rowId] || selectedChoiceId,
        expected: expectedChoice?.label || expectedChoiceId
      };
    });
}

export function StudentSessionPage() {
  const { difficulty } = useParams<{ difficulty: Difficulty }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const topicId = searchParams.get("topic") || "";
  const studentId = searchParams.get("student") || "";
  const academicYearId = searchParams.get("year") || "";
  const timezone = searchParams.get("tz") || "Europe/London";

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionMode, setSessionMode] = useState<SessionMode | null>(null);
  const [questions, setQuestions] = useState<RuntimeSessionQuestion[]>([]);
  const [legacyQuestions, setLegacyQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState<Record<string, unknown>>({});
  const [responses, setResponses] = useState<SessionQuestionAnswer[]>([]);
  const [evaluated, setEvaluated] = useState(false);
  const [lastCorrect, setLastCorrect] = useState(false);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [loading, setLoading] = useState(true);
  const [checkingAnswer, setCheckingAnswer] = useState(false);
  const [lockedMessage, setLockedMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  const activeQuestion = questions[currentIndex];
  const activeLegacyQuestion = sessionMode === "legacy" ? legacyQuestions[currentIndex] : null;
  const isLast = currentIndex === questions.length - 1;

  const progressLabel = useMemo(
    () => `Question ${Math.min(currentIndex + 1, questions.length)} of ${questions.length || 0}`,
    [currentIndex, questions.length]
  );

  const matchCorrections = useMemo(() => {
    if (!evaluated || !activeQuestion || lastCorrect) {
      return [];
    }

    if (sessionMode === "legacy" && activeLegacyQuestion?.format === "match_table") {
      return getMatchCorrections(activeLegacyQuestion, answer);
    }

    if (sessionMode === "v2") {
      return buildRuntimeMatchCorrections(activeQuestion, activeQuestion.feedback, answer);
    }

    return [];
  }, [activeLegacyQuestion, activeQuestion, answer, evaluated, lastCorrect, sessionMode]);

  useEffect(() => {
    const current = questions[currentIndex];
    if (!current) {
      return;
    }

    setAnswer(current.student_answer || {});
    setEvaluated(current.grading_status === "graded");
    setLastCorrect(Boolean(current.is_correct));
    setStartTime(Date.now());
  }, [currentIndex, questions]);

  useEffect(() => {
    let cancelled = false;

    async function bootLegacy() {
      if (!difficulty || !topicId || !studentId || !academicYearId) {
        throw new Error("Session parameters are incomplete. Return to student home.");
      }

      const today = localDateISO(timezone);
      const allowed = await canStartSession({
        studentId,
        academicYearId,
        difficulty,
        localDate: today
      });

      if (!allowed) {
        if (!cancelled) {
          setLockedMessage(
            "You have completed 3 sessions in this difficulty today. This level unlocks again tomorrow."
          );
        }
        return;
      }

      const picked = await pickSessionQuestions({
        studentId,
        topicId,
        difficulty,
        count: 10
      });

      if (picked.length === 0) {
        throw new Error("No questions are available for this topic and difficulty yet.");
      }

      const session = await createSession({
        studentId,
        academicYearId,
        topicId,
        difficulty
      });

      if (!cancelled) {
        setSessionMode("legacy");
        setSessionId(session.id);
        setLegacyQuestions(picked);
        setQuestions(picked.map((question, index) => toRuntimeQuestionFromLegacy(question, index + 1)));
        setCurrentIndex(0);
        setResponses([]);
      }
    }

    async function boot() {
      if (!difficulty || !topicId || !studentId || !academicYearId) {
        if (!cancelled) {
          setError("Session parameters are incomplete. Return to student home.");
          setLoading(false);
        }
        return;
      }

      try {
        if (!cancelled) {
          setLoading(true);
          setError(null);
          setLockedMessage(null);
        }

        try {
          const runtimeSession = await startSessionV2({
            studentId,
            academicYearId,
            topicId,
            difficulty,
            localDate: localDateISO(timezone),
            count: 10,
            recencyBuffer: 30
          });

          if (!cancelled) {
            setSessionMode("v2");
            setSessionId(runtimeSession.session_id);
            setLegacyQuestions([]);
            setQuestions(runtimeSession.questions);
            setCurrentIndex(getResumeIndex(runtimeSession.questions));
            setResponses([]);
          }
          return;
        } catch (caught) {
          if (!isV2RuntimeUnavailableError(caught)) {
            throw caught;
          }
        }

        await bootLegacy();
      } catch (caught) {
        if (!cancelled && !lockedMessage) {
          setError(getErrorMessage(caught, "Unable to start this session."));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void boot();

    return () => {
      cancelled = true;
    };
  }, [academicYearId, difficulty, reloadKey, studentId, timezone, topicId]);

  async function checkAnswer() {
    if (!activeQuestion || evaluated) {
      return;
    }

    if (sessionMode === "v2" && sessionId) {
      try {
        setCheckingAnswer(true);
        const grading = await gradeSessionQuestionV2({
          sessionId,
          studentId,
          sessionQuestionId: activeQuestion.session_item_id,
          studentAnswer: answer,
          responseTimeMs: Date.now() - startTime,
          hintUsed: false
        });

        setQuestions((prev) =>
          prev.map((question) =>
            question.session_item_id === activeQuestion.session_item_id
              ? {
                  ...question,
                  grading_status: "graded",
                  student_answer: answer,
                  is_correct: grading.grading.is_correct,
                  marks_awarded: grading.grading.marks_awarded,
                  marks_available: grading.grading.marks_available,
                  feedback: grading.grading.feedback,
                  explanation: grading.explanation || question.explanation
                }
              : question
          )
        );
        setLastCorrect(grading.grading.is_correct);
        setEvaluated(true);
        return;
      } catch (caught) {
        setError(getErrorMessage(caught, "Could not check this answer."));
      } finally {
        setCheckingAnswer(false);
      }

      return;
    }

    if (!activeLegacyQuestion) {
      return;
    }

    const isCorrect = evaluateAnswer(activeLegacyQuestion, answer);
    const responseTimeMs = Date.now() - startTime;

    setResponses((prev) => [
      ...prev,
      {
        questionId: activeLegacyQuestion.id,
        position: currentIndex + 1,
        answer,
        isCorrect,
        responseTimeMs,
        hintUsed: false
      }
    ]);

    setQuestions((prev) =>
      prev.map((question, index) =>
        index === currentIndex
          ? {
              ...question,
              grading_status: "graded",
              student_answer: answer,
              is_correct: isCorrect,
              marks_awarded: isCorrect ? question.marks_available : 0,
              feedback: null
            }
          : question
      )
    );
    setLastCorrect(isCorrect);
    setEvaluated(true);
  }

  async function nextOrFinish() {
    if (!activeQuestion || !evaluated) {
      return;
    }

    if (!isLast) {
      setCurrentIndex((value) => value + 1);
      return;
    }

    if (!sessionId) {
      setError("Session record missing. Cannot save progress.");
      return;
    }

    try {
      setSaving(true);

      if (sessionMode === "v2") {
        await completeSessionV2({
          sessionId,
          studentId,
          academicYearId,
          localDate: localDateISO(timezone)
        });
        navigate(`/student/summary/${sessionId}?student=${studentId}&year=${academicYearId}`);
        return;
      }

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
      setError(getErrorMessage(caught, "Could not save session."));
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
    return (
      <div className="panel stack gap-md">
        <div className="error-box">{error}</div>
        <div className="inline-actions">
          <button className="primary-btn" onClick={() => setReloadKey((value) => value + 1)}>
            Retry Session Start
          </button>
          <button className="ghost-btn" onClick={() => navigate("/student")}>
            Back to Student Home
          </button>
        </div>
      </div>
    );
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
        <p className="question-stem">{cleanQuestionStemForDisplay(activeQuestion.stem)}</p>

        <QuestionRenderer
          question={activeQuestion}
          answer={answer}
          onChange={setAnswer}
          isLocked={evaluated}
          showFeedback={evaluated}
          feedback={activeQuestion.feedback}
        />

        {!evaluated ? (
          <div className="question-actions">
            <button className="primary-btn" onClick={() => void checkAnswer()} disabled={checkingAnswer}>
              {checkingAnswer ? "Checking..." : "Check Answer"}
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
                      <strong>{item.left}</strong>: your match was <em>{item.selected || "not answered"}</em>; correct match is <em>{item.expected}</em>.
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
