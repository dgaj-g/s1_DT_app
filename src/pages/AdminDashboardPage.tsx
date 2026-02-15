import { useEffect, useMemo, useRef, useState } from "react";
import {
  callEdgeFunction,
  getAdminAccounts,
  getAdminSummary,
  getAllAcademicYears,
  getQuestionsForAdmin,
  getTopics,
  setQuestionQaStatus,
  setActiveAcademicYear,
  updateQuestionContent,
  toggleAdminProfileActive,
  toggleQuestionActive,
  toggleTopicEnabled
} from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import type { AcademicYear, Difficulty, QuestionFormat, Topic } from "../lib/types";

interface EdgeCsvResponse {
  filename: string;
  csv: string;
}

interface EdgePasswordResponse {
  year: string;
  generated_at: string;
  rows: Array<{ username: string; password: string }>;
}

interface AdminQuestion {
  id: string;
  topic_id: string;
  difficulty: string;
  format: string;
  stem: string;
  options_json: Record<string, unknown> | null;
  correct_answer_json: Record<string, unknown> | null;
  explanation: string;
  source_type: string;
  source_ref: string;
  is_active: boolean;
  qa_status: string;
  created_at: string;
  tags_json: string[] | null;
}

const DIFFICULTY_ORDER: Record<string, number> = {
  easy: 0,
  medium: 1,
  expert: 2
};

const EDITABLE_DIFFICULTIES: Difficulty[] = ["easy", "medium", "expert"];
const EDITABLE_FORMATS: QuestionFormat[] = [
  "mcq",
  "drag_drop",
  "match_table",
  "fill_gap",
  "short_text",
  "structured_response",
  "diagram_label"
];
const EDITABLE_SOURCES: Array<"adapted_exam" | "new_original"> = ["adapted_exam", "new_original"];

interface QuestionEditDraft {
  stem: string;
  difficulty: Difficulty;
  format: QuestionFormat;
  sourceType: "adapted_exam" | "new_original";
  sourceRef: string;
  explanation: string;
  tagsText: string;
  optionsText: string;
  correctText: string;
}

function downloadText(filename: string, text: string, contentType = "text/plain") {
  const blob = new Blob([text], { type: contentType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function asObject(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return {};
  }
  return value as Record<string, unknown>;
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map((item) => String(item));
}

function asPairs(value: unknown): Array<{ left: string; right: string }> {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .filter((item) => item && typeof item === "object")
    .map((item) => {
      const row = item as Record<string, unknown>;
      return {
        left: String(row.left || ""),
        right: String(row.right || "")
      };
    })
    .filter((pair) => pair.left && pair.right);
}

function asStringMap(value: unknown): Record<string, string> {
  const obj = asObject(value);
  const out: Record<string, string> = {};
  for (const [key, item] of Object.entries(obj)) {
    out[key] = String(item);
  }
  return out;
}

function nextQaStatus(current: string): "draft" | "reviewed" | "published" {
  if (current === "draft") {
    return "reviewed";
  }
  if (current === "reviewed") {
    return "published";
  }
  return "draft";
}

function nextQaActionLabel(current: string): string {
  if (current === "draft") {
    return "Send to Reviewed";
  }
  if (current === "reviewed") {
    return "Send to Published";
  }
  return "Reset to Draft";
}

function formatToken(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .trim();
}

function clampText(text: string, max = 110): string {
  if (text.length <= max) {
    return text;
  }
  return `${text.slice(0, max - 1)}…`;
}

function getQuestionOptionsPreview(question: AdminQuestion): string {
  const options = asObject(question.options_json);
  const choices = asStringArray(options.choices);
  const pairs = asPairs(options.pairs);
  const items = asStringArray(options.items);

  if (question.format === "mcq" || question.format === "diagram_label") {
    return clampText(choices.join(" | ") || "Multiple-choice options");
  }

  if (question.format === "match_table") {
    return clampText(pairs.map((pair) => pair.left).join(" | ") || "Match-table prompts");
  }

  if (question.format === "drag_drop") {
    return clampText(items.join(" -> ") || "Ordered sequence");
  }

  if (question.format === "fill_gap") {
    return "Short text response";
  }

  return "Structured response";
}

function getQuestionCorrectPreview(question: AdminQuestion): string {
  const correct = asObject(question.correct_answer_json);

  if (question.format === "mcq" || question.format === "diagram_label") {
    return String(correct.choice || "No answer set");
  }

  if (question.format === "fill_gap") {
    const accepted = asStringArray(correct.accepted);
    return clampText(accepted.join(" / ") || "Accepted terms required");
  }

  if (question.format === "drag_drop") {
    const order = asStringArray(correct.order);
    return clampText(order.join(" -> ") || "Correct sequence");
  }

  if (question.format === "match_table") {
    const pairs = asStringMap(correct.pairs);
    const preview = Object.entries(pairs)
      .map(([left, right]) => `${left}: ${right}`)
      .join(" | ");
    return clampText(preview || "Marked by term pairings");
  }

  return clampText(JSON.stringify(correct));
}

function formatJsonForDisplay(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function isQaReadyForStudents(qaStatus: string): boolean {
  return qaStatus === "reviewed" || qaStatus === "published";
}

function asDifficulty(value: string): Difficulty {
  if (value === "easy" || value === "medium" || value === "expert") {
    return value;
  }
  return "easy";
}

function asQuestionFormat(value: string): QuestionFormat {
  if (
    value === "mcq" ||
    value === "drag_drop" ||
    value === "match_table" ||
    value === "fill_gap" ||
    value === "short_text" ||
    value === "structured_response" ||
    value === "diagram_label"
  ) {
    return value;
  }
  return "mcq";
}

function asSourceType(value: string): "adapted_exam" | "new_original" {
  if (value === "adapted_exam" || value === "new_original") {
    return value;
  }
  return "new_original";
}

function buildEditDraft(question: AdminQuestion): QuestionEditDraft {
  return {
    stem: question.stem,
    difficulty: asDifficulty(question.difficulty),
    format: asQuestionFormat(question.format),
    sourceType: asSourceType(question.source_type),
    sourceRef: question.source_ref,
    explanation: question.explanation,
    tagsText: (question.tags_json || []).join(", "),
    optionsText: formatJsonForDisplay(question.options_json || {}),
    correctText: formatJsonForDisplay(question.correct_answer_json || {})
  };
}

export function AdminDashboardPage() {
  const { profile } = useAuth();
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [activeYearId, setActiveYearId] = useState<string>("");
  const [summary, setSummary] = useState<{ students: number; completedSessions: number; activeQuestions: number } | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [networkTopicId, setNetworkTopicId] = useState<string>("");
  const [questions, setQuestions] = useState<AdminQuestion[]>([]);
  const [admins, setAdmins] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const [reviewDifficulty, setReviewDifficulty] = useState<string>("all");
  const [reviewFormat, setReviewFormat] = useState<string>("all");
  const [reviewQaStatus, setReviewQaStatus] = useState<string>("all");
  const [reviewSearch, setReviewSearch] = useState<string>("");
  const [includeInactiveVersions, setIncludeInactiveVersions] = useState(false);
  const [selectedQuestionId, setSelectedQuestionId] = useState<string>("");
  const [editingQuestionId, setEditingQuestionId] = useState<string>("");
  const [editDraft, setEditDraft] = useState<QuestionEditDraft | null>(null);
  const selectedQuestionPanelRef = useRef<HTMLElement | null>(null);
  const questionStemInputRef = useRef<HTMLTextAreaElement | null>(null);

  const canEditQuestionContent = Boolean(profile?.can_edit_questions);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [yearRows, topicRows, adminRows] = await Promise.all([getAllAcademicYears(), getTopics(), getAdminAccounts()]);

        const networkTopic = topicRows.find((topic) => topic.slug === "network-technologies");
        const selectedTopicId = networkTopic?.id || "";
        const active = yearRows.find((item) => item.is_active) || yearRows[0] || null;

        setYears(yearRows);
        setTopics(topicRows);
        setAdmins(adminRows);
        setNetworkTopicId(selectedTopicId);

        if (active) {
          setActiveYearId(active.id);
          const [summaryData, questionRows] = await Promise.all([
            getAdminSummary({ academicYearId: active.id }),
            getQuestionsForAdmin(selectedTopicId || undefined)
          ]);

          setSummary(summaryData);
          setQuestions((questionRows || []) as AdminQuestion[]);
        }
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Could not load admin dashboard.");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  async function refreshSummary(yearId: string) {
    const [summaryData, topicRows, adminRows] = await Promise.all([
      getAdminSummary({ academicYearId: yearId }),
      getTopics(),
      getAdminAccounts()
    ]);

    const networkTopic = topicRows.find((topic) => topic.slug === "network-technologies");
    const selectedTopicId = networkTopic?.id || "";
    const questionRows = await getQuestionsForAdmin(selectedTopicId || undefined);

    setSummary(summaryData);
    setTopics(topicRows);
    setQuestions((questionRows || []) as AdminQuestion[]);
    setAdmins(adminRows);
    setNetworkTopicId(selectedTopicId);
  }

  async function handleSetYear() {
    if (!activeYearId) {
      return;
    }

    setBusy("year");
    setError(null);
    try {
      await setActiveAcademicYear(activeYearId);
      await refreshSummary(activeYearId);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not set active year.");
    } finally {
      setBusy(null);
    }
  }

  async function handleRotatePasswords() {
    const yearCode = years.find((item) => item.id === activeYearId)?.code || "unknown-year";
    setBusy("rotate");
    setError(null);

    try {
      const data = await callEdgeFunction<EdgePasswordResponse>("admin_bulk_rotate_student_passwords", {
        academic_year_code: yearCode
      });

      const csvLines = ["username,password", ...data.rows.map((row) => `${row.username},${row.password}`)];
      downloadText(`student-passwords-${yearCode}.csv`, `${csvLines.join("\n")}\n`, "text/csv");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not rotate passwords.");
    } finally {
      setBusy(null);
    }
  }

  async function handleExportCsv() {
    if (!activeYearId) {
      setError("Select an active academic year first.");
      return;
    }

    setBusy("export");
    setError(null);

    try {
      const data = await callEdgeFunction<EdgeCsvResponse>("admin_export_stats_csv", {
        academic_year_id: activeYearId,
        difficulty: null,
        username_from: "s1dt001",
        username_to: "s1dt100"
      });

      downloadText(data.filename, data.csv, "text/csv");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not export CSV.");
    } finally {
      setBusy(null);
    }
  }

  async function handleExportDetailedCsv() {
    if (!activeYearId) {
      setError("Select an active academic year first.");
      return;
    }

    setBusy("export-detailed");
    setError(null);

    try {
      const data = await callEdgeFunction<EdgeCsvResponse>("admin_export_detailed_question_report_csv", {
        academic_year_id: activeYearId,
        difficulty: null,
        username_from: "s1dt001",
        username_to: "s1dt100"
      });

      downloadText(data.filename, data.csv, "text/csv");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not export detailed report CSV.");
    } finally {
      setBusy(null);
    }
  }

  async function handleRepairPool() {
    setBusy("pool");
    setError(null);

    try {
      await callEdgeFunction("admin_seed_or_repair_student_pool", {
        start: 1,
        end: 100,
        prefix: "s1dt"
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not repair student pool.");
    } finally {
      setBusy(null);
    }
  }

  const availableFormats = useMemo(() => {
    const values = new Set<string>();
    for (const question of questions) {
      values.add(question.format);
    }
    return ["all", ...Array.from(values).sort()];
  }, [questions]);

  const reviewQuestions = useMemo(() => {
    const search = reviewSearch.trim().toLowerCase();

    return questions
      .filter((question) => (includeInactiveVersions ? true : Boolean(question.is_active)))
      .filter((question) => (reviewDifficulty === "all" ? true : question.difficulty === reviewDifficulty))
      .filter((question) => (reviewFormat === "all" ? true : question.format === reviewFormat))
      .filter((question) => (reviewQaStatus === "all" ? true : question.qa_status === reviewQaStatus))
      .filter((question) => {
        if (!search) {
          return true;
        }

        const haystack = [question.stem, question.explanation, question.source_ref, ...(question.tags_json || [])]
          .join(" ")
          .toLowerCase();
        return haystack.includes(search);
      })
      .sort((a, b) => {
        const diff = (DIFFICULTY_ORDER[a.difficulty] ?? 99) - (DIFFICULTY_ORDER[b.difficulty] ?? 99);
        if (diff !== 0) {
          return diff;
        }

        const timeA = new Date(a.created_at || "").getTime();
        const timeB = new Date(b.created_at || "").getTime();
        return timeA - timeB;
      });
  }, [includeInactiveVersions, questions, reviewDifficulty, reviewFormat, reviewQaStatus, reviewSearch]);

  const reviewCounts = useMemo(() => {
    const counts = { easy: 0, medium: 0, expert: 0 };
    for (const question of reviewQuestions) {
      if (question.difficulty in counts) {
        counts[question.difficulty as keyof typeof counts] += 1;
      }
    }
    return counts;
  }, [reviewQuestions]);

  useEffect(() => {
    if (reviewQuestions.length === 0) {
      if (selectedQuestionId) {
        setSelectedQuestionId("");
      }
      return;
    }

    if (!reviewQuestions.some((question) => question.id === selectedQuestionId)) {
      setSelectedQuestionId(reviewQuestions[0].id);
    }
  }, [reviewQuestions, selectedQuestionId]);

  const selectedQuestion = useMemo(
    () => reviewQuestions.find((question) => question.id === selectedQuestionId) || null,
    [reviewQuestions, selectedQuestionId]
  );

  const selectedQuestionPosition = useMemo(
    () => reviewQuestions.findIndex((question) => question.id === selectedQuestionId) + 1,
    [reviewQuestions, selectedQuestionId]
  );

  useEffect(() => {
    if (!selectedQuestion) {
      setEditingQuestionId("");
      setEditDraft(null);
      return;
    }

    if (editingQuestionId !== selectedQuestion.id) {
      setEditingQuestionId("");
      setEditDraft(null);
    }
  }, [editingQuestionId, selectedQuestion]);

  function openEditorForQuestion(question: AdminQuestion) {
    if (!canEditQuestionContent) {
      return;
    }

    setSelectedQuestionId(question.id);
    setEditingQuestionId(question.id);
    setEditDraft(buildEditDraft(question));
  }

  function startEditingSelectedQuestion() {
    if (!selectedQuestion || !canEditQuestionContent) {
      return;
    }

    openEditorForQuestion(selectedQuestion);
  }

  function cancelEditingSelectedQuestion() {
    setEditingQuestionId("");
    setEditDraft(null);
  }

  async function saveEditedQuestion() {
    if (!selectedQuestion || !editDraft || editingQuestionId !== selectedQuestion.id) {
      return;
    }

    setBusy(`q-edit-${selectedQuestion.id}`);
    setError(null);
    try {
      const parsedOptions = JSON.parse(editDraft.optionsText) as Record<string, unknown>;
      const parsedCorrect = JSON.parse(editDraft.correctText) as Record<string, unknown>;
      const tags = editDraft.tagsText
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean);

      await updateQuestionContent({
        id: selectedQuestion.id,
        difficulty: editDraft.difficulty,
        format: editDraft.format,
        stem: editDraft.stem.trim(),
        optionsJson: parsedOptions,
        correctAnswerJson: parsedCorrect,
        explanation: editDraft.explanation.trim(),
        sourceType: editDraft.sourceType,
        sourceRef: editDraft.sourceRef.trim(),
        tags
      });

      setEditingQuestionId("");
      setEditDraft(null);
      await refreshSummary(activeYearId);
      setSelectedQuestionId(selectedQuestion.id);
    } catch (caught) {
      if (caught instanceof Error) {
        setError(caught.message);
      } else {
        setError("Could not save question content.");
      }
    } finally {
      setBusy(null);
    }
  }

  useEffect(() => {
    if (!editingQuestionId || !editDraft) {
      return;
    }

    selectedQuestionPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    const timer = window.setTimeout(() => {
      questionStemInputRef.current?.focus();
      questionStemInputRef.current?.setSelectionRange(0, questionStemInputRef.current.value.length);
    }, 150);

    return () => {
      window.clearTimeout(timer);
    };
  }, [editDraft, editingQuestionId]);

  if (loading) {
    return <div className="center-screen">Loading admin dashboard...</div>;
  }

  return (
    <div className="stack gap-lg">
      <section className="panel hero-panel">
        <h2>Department Admin</h2>
        <p>Manage academic years, credentials, reporting, and question availability for student sessions.</p>
        {error ? <div className="error-box">{error}</div> : null}
      </section>

      <section className="panel stack gap-sm">
        <h3>Academic Year Control</h3>
        <div className="inline-actions">
          <select value={activeYearId} onChange={(event) => setActiveYearId(event.target.value)}>
            {years.map((year) => (
              <option key={year.id} value={year.id}>
                {year.code} {year.is_active ? "(active)" : ""}
              </option>
            ))}
          </select>
          <button className="primary-btn" onClick={() => void handleSetYear()} disabled={busy === "year"}>
            {busy === "year" ? "Saving..." : "Set Active Year"}
          </button>
        </div>
      </section>

      <section className="stats-grid">
        <article className="panel">
          <h3>Active Student Accounts</h3>
          <p className="metric">{summary?.students ?? 0}</p>
        </article>
        <article className="panel">
          <h3>Completed Sessions</h3>
          <p className="metric">{summary?.completedSessions ?? 0}</p>
        </article>
        <article className="panel">
          <h3>Questions In Student Sessions</h3>
          <p className="metric">{summary?.activeQuestions ?? 0}</p>
        </article>
      </section>

      <section className="panel stack gap-sm">
        <h3>Admin Operations</h3>
        <div className="inline-actions wrap">
          <button className="primary-btn" onClick={() => void handleRotatePasswords()} disabled={busy === "rotate"}>
            {busy === "rotate" ? "Rotating..." : "Bulk Rotate 100 Student Passwords"}
          </button>
          <button className="ghost-btn" onClick={() => void handleExportCsv()} disabled={busy === "export"}>
            {busy === "export" ? "Exporting..." : "Export Progress CSV"}
          </button>
          <button
            className="ghost-btn"
            onClick={() => void handleExportDetailedCsv()}
            disabled={busy === "export-detailed"}
          >
            {busy === "export-detailed" ? "Exporting..." : "Detailed Question Report CSV"}
          </button>
          <button className="ghost-btn" onClick={() => void handleRepairPool()} disabled={busy === "pool"}>
            {busy === "pool" ? "Repairing..." : "Seed/Repair Student Pool"}
          </button>
        </div>
      </section>

      <section className="panel stack gap-sm">
        <h3>Admin Accounts</h3>
        <p>Multiple teacher accounts are supported. Toggle access on existing admin profiles.</p>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Question Editor</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {admins.map((admin) => (
              <tr key={String(admin.id)}>
                <td>{String(admin.display_name || admin.id)}</td>
                <td>{admin.is_active ? "Active" : "Disabled"}</td>
                <td>{admin.can_edit_questions ? "Yes" : "No"}</td>
                <td>
                  <button
                    className="small-btn"
                    onClick={async () => {
                      try {
                        await toggleAdminProfileActive(String(admin.id), !Boolean(admin.is_active));
                        await refreshSummary(activeYearId);
                      } catch {
                        setError("Could not update admin status.");
                      }
                    }}
                  >
                    {admin.is_active ? "Disable" : "Enable"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel stack gap-sm">
        <h3>Topic Publishing</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Topic</th>
              <th>Enabled</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {topics.map((topic) => (
              <tr key={topic.id}>
                <td>{topic.title}</td>
                <td>{topic.is_enabled ? "Yes" : "No"}</td>
                <td>
                  <button
                    className="small-btn"
                    onClick={async () => {
                      try {
                        await toggleTopicEnabled(topic.id, !topic.is_enabled);
                        await refreshSummary(activeYearId);
                      } catch {
                        setError("Could not update topic.");
                      }
                    }}
                  >
                    {topic.is_enabled ? "Disable" : "Enable"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel stack gap-sm">
        <h3>Teacher Question Review</h3>
        <p>
          Review the live question bank content clearly before publishing. Use filters to inspect each difficulty,
          format, and QA stage.
        </p>

        <div className="teacher-review-toolbar">
          <select value={reviewDifficulty} onChange={(event) => setReviewDifficulty(event.target.value)}>
            <option value="all">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="expert">Expert</option>
          </select>

          <select value={reviewFormat} onChange={(event) => setReviewFormat(event.target.value)}>
            {availableFormats.map((format) => (
              <option value={format} key={format}>
                {format === "all" ? "All Formats" : format}
              </option>
            ))}
          </select>

          <select value={reviewQaStatus} onChange={(event) => setReviewQaStatus(event.target.value)}>
            <option value="all">All QA Stages</option>
            <option value="draft">Draft</option>
            <option value="reviewed">Reviewed</option>
            <option value="published">Published</option>
          </select>

          <label className="review-checkbox">
            <input
              type="checkbox"
              checked={includeInactiveVersions}
              onChange={(event) => setIncludeInactiveVersions(event.target.checked)}
            />
            Include inactive versions
          </label>

          <input
            type="search"
            placeholder="Search stem, explanation, source, tags"
            value={reviewSearch}
            onChange={(event) => setReviewSearch(event.target.value)}
          />
        </div>

        <p className="teacher-review-summary">
          Showing <strong>{reviewQuestions.length}</strong> question(s)
          {networkTopicId ? " in Network Technologies" : ""}.
          Easy: <strong>{reviewCounts.easy}</strong>, Medium: <strong>{reviewCounts.medium}</strong>, Expert: <strong>{reviewCounts.expert}</strong>.
        </p>
        <p className="teacher-review-summary">
          Student sessions only include questions marked <strong>Reviewed</strong> or <strong>Published</strong> and set
          to <strong>Use in Student Sessions</strong>.
        </p>

        <div className="teacher-review-table-wrap">
          <table className="table teacher-review-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Difficulty</th>
                <th>Format</th>
                <th>Question Stem</th>
                <th>Options / Prompt Preview</th>
                <th>Correct Answer Preview</th>
                <th>QA Stage</th>
                <th>In Student Sessions</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reviewQuestions.map((question, index) => {
                const nextQa = nextQaStatus(String(question.qa_status || "draft"));
                const selected = selectedQuestionId === question.id;
                const qaReady = isQaReadyForStudents(question.qa_status || "draft");
                const inStudentSessions = Boolean(question.is_active) && qaReady;
                return (
                  <tr
                    key={question.id}
                    className={`teacher-review-row ${selected ? "is-selected" : ""}`}
                    onClick={() => setSelectedQuestionId(question.id)}
                  >
                    <td className="mono-cell">{index + 1}</td>
                    <td>
                      <span className={`review-pill difficulty-${question.difficulty}`}>
                        {question.difficulty.toUpperCase()}
                      </span>
                    </td>
                    <td>{formatToken(question.format)}</td>
                    <td className="teacher-review-stem-cell">{question.stem}</td>
                    <td>{getQuestionOptionsPreview(question)}</td>
                    <td>{getQuestionCorrectPreview(question)}</td>
                    <td>
                      <span className="review-pill">QA: {formatToken(question.qa_status || "draft")}</span>
                    </td>
                    <td>
                      <span className={`review-pill ${inStudentSessions ? "is-live" : "is-off"}`}>
                        {inStudentSessions ? "In Use" : qaReady ? "Not In Use" : "Blocked by QA"}
                      </span>
                    </td>
                    <td>
                      <div className="inline-actions wrap">
                        <button
                          className="small-btn"
                          disabled={
                            busy === `q-pub-${question.id}` ||
                            busy === `q-qa-${question.id}` ||
                            (!question.is_active && !qaReady)
                          }
                          title={!question.is_active && !qaReady ? "Move QA to Reviewed or Published first." : undefined}
                          onClick={async (event) => {
                            event.stopPropagation();
                            setBusy(`q-pub-${question.id}`);
                            try {
                              await toggleQuestionActive(question.id, !Boolean(question.is_active));
                              await refreshSummary(activeYearId);
                            } catch {
                              setError("Could not update student-session availability.");
                            } finally {
                              setBusy(null);
                            }
                          }}
                        >
                          {question.is_active ? "Remove from Student Sessions" : "Use in Student Sessions"}
                        </button>

                        <button
                          className="small-btn"
                          disabled={busy === `q-pub-${question.id}` || busy === `q-qa-${question.id}`}
                          onClick={async (event) => {
                            event.stopPropagation();
                            setBusy(`q-qa-${question.id}`);
                            try {
                              await setQuestionQaStatus(question.id, nextQa);
                              await refreshSummary(activeYearId);
                            } catch {
                              setError("Could not update question QA status.");
                            } finally {
                              setBusy(null);
                            }
                          }}
                        >
                          {nextQaActionLabel(question.qa_status || "draft")}
                        </button>
                        {canEditQuestionContent ? (
                          <button
                            className="small-btn"
                            onClick={(event) => {
                              event.stopPropagation();
                              openEditorForQuestion(question);
                            }}
                          >
                            Edit Content
                          </button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                );
              })}

              {reviewQuestions.length === 0 ? (
                <tr>
                  <td colSpan={9}>
                    <div className="error-box">No questions match the current filters.</div>
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>

        {selectedQuestion ? (
          (() => {
            const options = asObject(selectedQuestion.options_json);
            const correct = asObject(selectedQuestion.correct_answer_json);
            const choices = asStringArray(options.choices);
            const pairs = asPairs(options.pairs);
            const dragItems = asStringArray(options.items);
            const accepted = asStringArray(correct.accepted);
            const correctOrder = asStringArray(correct.order);
            const correctPairs = asStringMap(correct.pairs);
            const marker = String(options.marker || options.callout || "");
            const diagramKey = String(options.diagram_key || "");
            const tags = asStringArray(selectedQuestion.tags_json);
            const editingDraft = editingQuestionId === selectedQuestion.id ? editDraft : null;
            const selectedQaReady = isQaReadyForStudents(selectedQuestion.qa_status || "draft");
            const selectedInStudentSessions = Boolean(selectedQuestion.is_active) && selectedQaReady;

            return (
              <article className="question-detail-panel" ref={selectedQuestionPanelRef}>
                <div className="question-review-head">
                  <div>
                    <p className="question-review-count">
                      Selected Question {selectedQuestionPosition} of {reviewQuestions.length}
                    </p>
                    <div className="question-review-badges">
                      <span className={`review-pill difficulty-${selectedQuestion.difficulty}`}>
                        {selectedQuestion.difficulty.toUpperCase()}
                      </span>
                      <span className="review-pill">{formatToken(selectedQuestion.format)}</span>
                      <span className="review-pill">QA: {formatToken(selectedQuestion.qa_status || "draft")}</span>
                      <span className={`review-pill ${selectedInStudentSessions ? "is-live" : "is-off"}`}>
                        {selectedInStudentSessions
                          ? "In Use for Students"
                          : selectedQaReady
                            ? "Not In Student Sessions"
                            : "Blocked by QA"}
                      </span>
                    </div>
                  </div>
                  <div className="inline-actions wrap">
                    {canEditQuestionContent && !editingDraft ? (
                      <button className="primary-btn" onClick={() => startEditingSelectedQuestion()}>
                        Edit Question Content
                      </button>
                    ) : null}
                    {canEditQuestionContent && editingDraft ? (
                      <>
                        <button
                          className="primary-btn"
                          disabled={busy === `q-edit-${selectedQuestion.id}`}
                          onClick={() => void saveEditedQuestion()}
                        >
                          {busy === `q-edit-${selectedQuestion.id}` ? "Saving..." : "Save Content Update"}
                        </button>
                        <button className="ghost-btn" onClick={() => cancelEditingSelectedQuestion()}>
                          Cancel
                        </button>
                      </>
                    ) : null}
                  </div>
                </div>
                {!canEditQuestionContent ? (
                  <p className="question-review-meta">
                    Content editing is restricted to the designated question editor account.
                  </p>
                ) : null}

                {editingDraft ? (
                  <div className="question-edit-form">
                    <label>
                      Question Stem
                      <textarea
                        ref={questionStemInputRef}
                        value={editingDraft.stem}
                        rows={3}
                        onChange={(event) =>
                          setEditDraft((draft) => (draft ? { ...draft, stem: event.target.value } : draft))
                        }
                      />
                    </label>

                    <div className="question-edit-grid">
                      <label>
                        Difficulty
                        <select
                          value={editingDraft.difficulty}
                          onChange={(event) =>
                            setEditDraft((draft) =>
                              draft ? { ...draft, difficulty: asDifficulty(event.target.value) } : draft
                            )
                          }
                        >
                          {EDITABLE_DIFFICULTIES.map((difficulty) => (
                            <option key={difficulty} value={difficulty}>
                              {formatToken(difficulty)}
                            </option>
                          ))}
                        </select>
                      </label>

                      <label>
                        Format
                        <select
                          value={editingDraft.format}
                          onChange={(event) =>
                            setEditDraft((draft) =>
                              draft ? { ...draft, format: asQuestionFormat(event.target.value) } : draft
                            )
                          }
                        >
                          {EDITABLE_FORMATS.map((format) => (
                            <option key={format} value={format}>
                              {formatToken(format)}
                            </option>
                          ))}
                        </select>
                      </label>

                      <label>
                        Source Type
                        <select
                          value={editingDraft.sourceType}
                          onChange={(event) =>
                            setEditDraft((draft) =>
                              draft ? { ...draft, sourceType: asSourceType(event.target.value) } : draft
                            )
                          }
                        >
                          {EDITABLE_SOURCES.map((sourceType) => (
                            <option key={sourceType} value={sourceType}>
                              {formatToken(sourceType)}
                            </option>
                          ))}
                        </select>
                      </label>

                      <label>
                        Source Reference
                        <input
                          value={editingDraft.sourceRef}
                          onChange={(event) =>
                            setEditDraft((draft) => (draft ? { ...draft, sourceRef: event.target.value } : draft))
                          }
                        />
                      </label>
                    </div>

                    <label>
                      Teaching Explanation
                      <textarea
                        value={editingDraft.explanation}
                        rows={3}
                        onChange={(event) =>
                          setEditDraft((draft) => (draft ? { ...draft, explanation: event.target.value } : draft))
                        }
                      />
                    </label>

                    <label>
                      Tags (comma-separated)
                      <input
                        value={editingDraft.tagsText}
                        onChange={(event) =>
                          setEditDraft((draft) => (draft ? { ...draft, tagsText: event.target.value } : draft))
                        }
                      />
                    </label>

                    <label>
                      Options JSON
                      <textarea
                        className="code-input"
                        value={editingDraft.optionsText}
                        rows={8}
                        onChange={(event) =>
                          setEditDraft((draft) => (draft ? { ...draft, optionsText: event.target.value } : draft))
                        }
                      />
                    </label>

                    <label>
                      Correct Answer JSON
                      <textarea
                        className="code-input"
                        value={editingDraft.correctText}
                        rows={8}
                        onChange={(event) =>
                          setEditDraft((draft) => (draft ? { ...draft, correctText: event.target.value } : draft))
                        }
                      />
                    </label>
                  </div>
                ) : (
                  <>
                    <p className="question-review-stem">{selectedQuestion.stem}</p>

                    <div className="question-detail-grid">
                      <div className="question-review-box">
                        <h4>Question Setup</h4>

                        {(selectedQuestion.format === "mcq" || selectedQuestion.format === "diagram_label") &&
                        choices.length > 0 ? (
                          <ol className="question-review-list-items">
                            {choices.map((choice, choiceIndex) => (
                              <li key={`${selectedQuestion.id}-choice-${choiceIndex}`}>{choice}</li>
                            ))}
                          </ol>
                        ) : null}

                        {selectedQuestion.format === "fill_gap" ? (
                          <p>Student types a short text answer in a free-response box.</p>
                        ) : null}

                        {selectedQuestion.format === "drag_drop" ? (
                          <>
                            <p>Items shown to student for ordering:</p>
                            <ol className="question-review-list-items">
                              {dragItems.map((item, itemIndex) => (
                                <li key={`${selectedQuestion.id}-drag-${itemIndex}`}>{item}</li>
                              ))}
                            </ol>
                          </>
                        ) : null}

                        {selectedQuestion.format === "match_table" ? (
                          <>
                            <p>Left column prompts:</p>
                            <ul className="question-review-list-items">
                              {pairs.map((pair) => (
                                <li key={`${selectedQuestion.id}-${pair.left}`}>{pair.left}</li>
                              ))}
                            </ul>
                            {choices.length > 0 ? <p>Choice bank: {choices.join(" | ")}</p> : null}
                          </>
                        ) : null}

                        {diagramKey ? (
                          <p>
                            Diagram family: <strong>{diagramKey}</strong>
                            {marker ? `, marker ${marker}` : ""}
                          </p>
                        ) : null}
                      </div>

                      <div className="question-review-box">
                        <h4>Marking / Correct Answer</h4>

                        {(selectedQuestion.format === "mcq" || selectedQuestion.format === "diagram_label") &&
                        correct.choice ? (
                          <p>
                            <strong>{String(correct.choice)}</strong>
                          </p>
                        ) : null}

                        {selectedQuestion.format === "fill_gap" ? (
                          <>
                            <p>Accepted answers:</p>
                            <ul className="question-review-list-items">
                              {accepted.map((item, itemIndex) => (
                                <li key={`${selectedQuestion.id}-accepted-${itemIndex}`}>{item}</li>
                              ))}
                            </ul>
                          </>
                        ) : null}

                        {selectedQuestion.format === "drag_drop" ? (
                          <>
                            <p>Required order:</p>
                            <ol className="question-review-list-items">
                              {correctOrder.map((item, itemIndex) => (
                                <li key={`${selectedQuestion.id}-correct-order-${itemIndex}`}>{item}</li>
                              ))}
                            </ol>
                          </>
                        ) : null}

                        {selectedQuestion.format === "match_table" ? (
                          <ul className="question-review-list-items">
                            {Object.entries(correctPairs).map(([left, right]) => (
                              <li key={`${selectedQuestion.id}-pair-${left}`}>
                                <strong>{left}</strong>
                                {" -> "}
                                {right}
                              </li>
                            ))}
                          </ul>
                        ) : null}
                      </div>
                    </div>

                    <p className="question-review-meta">
                      <strong>Teaching explanation:</strong> {selectedQuestion.explanation}
                    </p>
                    <p className="question-review-meta">
                      <strong>Source:</strong> {selectedQuestion.source_type} | {selectedQuestion.source_ref}
                    </p>
                    {tags.length > 0 ? (
                      <p className="question-review-meta">
                        <strong>Tags:</strong> {tags.join(", ")}
                      </p>
                    ) : null}

                    <details className="question-json-details">
                      <summary>Show raw question JSON</summary>
                      <pre>{formatJsonForDisplay(selectedQuestion.options_json)}</pre>
                      <pre>{formatJsonForDisplay(selectedQuestion.correct_answer_json)}</pre>
                    </details>
                  </>
                )}
              </article>
            );
          })()
        ) : null}
      </section>
    </div>
  );
}
