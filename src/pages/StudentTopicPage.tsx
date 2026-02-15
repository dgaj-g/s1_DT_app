import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { StudentStatsPanel } from "../components/StudentStatsPanel";
import { TopicCard } from "../components/TopicCard";
import { useAuth } from "../hooks/useAuth";
import {
  getActiveAcademicYear,
  getStudentAccountId,
  getStudentAnsweredTags,
  getStudentSessions,
  getTodayCaps,
  getTopics
} from "../lib/api";
import { localDateISO } from "../lib/date";
import { DEFAULT_TIMEZONE } from "../lib/supabase";
import { computeStreak } from "../lib/scoring";
import type { Difficulty, SessionRecord, Topic } from "../lib/types";

export function StudentTopicPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [topicList, setTopicList] = useState<Topic[]>([]);
  const [studentId, setStudentId] = useState<string | null>(null);
  const [year, setYear] = useState<{ id: string; code: string; timezone: string } | null>(null);
  const [sessions, setSessions] = useState<SessionRecord[]>([]);
  const [tagStats, setTagStats] = useState<Array<{ tag: string; total: number; correct: number }>>([]);
  const [caps, setCaps] = useState<Record<Difficulty, number>>({ easy: 0, medium: 0, expert: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!user) {
        return;
      }

      try {
        setLoading(true);
        const [topics, activeYear] = await Promise.all([getTopics(), getActiveAcademicYear()]);
        if (!activeYear) {
          throw new Error("No active academic year configured.");
        }

        const sid = await getStudentAccountId(user.id);
        const date = localDateISO(activeYear.timezone || DEFAULT_TIMEZONE);

        const [todayCaps, allSessions, answeredTags] = await Promise.all([
          getTodayCaps({
            studentId: sid,
            academicYearId: activeYear.id,
            localDate: date
          }),
          getStudentSessions({ studentId: sid, academicYearId: activeYear.id }),
          getStudentAnsweredTags({ studentId: sid, academicYearId: activeYear.id })
        ]);

        const capMap: Record<Difficulty, number> = { easy: 0, medium: 0, expert: 0 };
        for (const row of todayCaps) {
          capMap[row.difficulty] = row.sessions_completed;
        }

        const tagMap = new Map<string, { total: number; correct: number }>();
        for (const row of answeredTags) {
          const q = row.questions as { tags_json?: string[] };
          const tags = q?.tags_json || ["general"];
          for (const tag of tags) {
            const prev = tagMap.get(tag) || { total: 0, correct: 0 };
            prev.total += 1;
            prev.correct += row.is_correct ? 1 : 0;
            tagMap.set(tag, prev);
          }
        }

        setTopicList(topics);
        setYear({ id: activeYear.id, code: activeYear.code, timezone: activeYear.timezone });
        setStudentId(sid);
        setSessions(allSessions);
        setCaps(capMap);
        setTagStats(
          Array.from(tagMap.entries()).map(([tag, value]) => ({
            tag,
            ...value
          }))
        );
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Could not load student dashboard.");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [user]);

  const streak = useMemo(() => computeStreak(sessions), [sessions]);

  function startTopic(topic: Topic, difficulty: Difficulty) {
    if (!studentId || !year) {
      return;
    }

    navigate(
      `/student/session/${difficulty}?topic=${encodeURIComponent(topic.id)}&student=${encodeURIComponent(studentId)}&year=${encodeURIComponent(year.id)}&tz=${encodeURIComponent(year.timezone || DEFAULT_TIMEZONE)}`
    );
  }

  if (loading) {
    return <div className="center-screen">Loading topics and stats...</div>;
  }

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  return (
    <div className="stack gap-lg">
      <section className="panel hero-panel">
        <h2>Welcome back</h2>
        <p>
          Active academic year: <strong>{year?.code}</strong>
        </p>
        <p>Pick your challenge level and complete short 10-question sessions.</p>
      </section>

      <section className="topic-grid">
        {topicList.map((topic) => (
          <TopicCard
            key={topic.id}
            topic={topic}
            caps={caps}
            onStart={(difficulty) => startTopic(topic, difficulty)}
          />
        ))}
      </section>

      <StudentStatsPanel sessions={sessions} tagBreakdown={tagStats} streak={streak} />
    </div>
  );
}
