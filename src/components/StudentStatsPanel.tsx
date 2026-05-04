import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { SessionRecord, Topic } from "../lib/types";

interface Props {
  sessions: SessionRecord[];
  tagBreakdown: Array<{ tag: string; total: number; correct: number }>;
  streak: number;
  topics: Topic[];
}

interface TopicRevisionStat {
  topicId: string;
  title: string;
  attempts: number;
  averageAccuracy: number | null;
  lastRevisedAt: string | null;
  lastDifficulty: string | null;
}

function formatDate(value: string | null) {
  if (!value) {
    return "Not revised yet";
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(new Date(value));
}

function getTopicTitle(session: SessionRecord, topicsById: Map<string, Topic>) {
  return session.topics?.title || topicsById.get(session.topic_id)?.title || "Topic";
}

function getTopicStats(sessions: SessionRecord[], topics: Topic[]): TopicRevisionStat[] {
  const completed = sessions.filter((session) => session.completed_at);
  const byTopic = new Map<string, SessionRecord[]>();

  for (const session of completed) {
    const list = byTopic.get(session.topic_id) || [];
    list.push(session);
    byTopic.set(session.topic_id, list);
  }

  return topics.map((topic) => {
    const attempts = byTopic.get(topic.id) || [];
    const scored = attempts.filter((session) => session.accuracy_pct !== null);
    const averageAccuracy = scored.length
      ? Math.round(scored.reduce((sum, session) => sum + Number(session.accuracy_pct || 0), 0) / scored.length)
      : null;
    const latest = attempts
      .slice()
      .sort((a, b) => new Date(b.completed_at || 0).getTime() - new Date(a.completed_at || 0).getTime())[0];

    return {
      topicId: topic.id,
      title: topic.title,
      attempts: attempts.length,
      averageAccuracy,
      lastRevisedAt: latest?.completed_at || null,
      lastDifficulty: latest?.difficulty || null
    };
  });
}

function getAction(stat: TopicRevisionStat) {
  if (stat.attempts === 0) {
    return "Start this topic";
  }
  if ((stat.averageAccuracy ?? 0) < 55) {
    return "Revisit easy/core questions";
  }
  if ((stat.averageAccuracy ?? 0) >= 80) {
    return "Try a harder session";
  }
  return "Keep practising";
}

export function StudentStatsPanel({ sessions, tagBreakdown, streak, topics }: Props) {
  const completed = sessions.filter((session) => session.completed_at);
  const topicsById = new Map(topics.map((topic) => [topic.id, topic]));
  const topicStats = getTopicStats(sessions, topics);
  const attemptedTopicStats = topicStats.filter((stat) => stat.attempts > 0 && stat.averageAccuracy !== null);

  const strongestTopic = attemptedTopicStats
    .slice()
    .sort((a, b) => (b.averageAccuracy ?? 0) - (a.averageAccuracy ?? 0) || b.attempts - a.attempts)[0];

  const needsWorkTopic = attemptedTopicStats
    .slice()
    .sort((a, b) => (a.averageAccuracy ?? 0) - (b.averageAccuracy ?? 0) || b.attempts - a.attempts)[0];

  const leastRecentTopic = topicStats
    .slice()
    .sort((a, b) => {
      if (!a.lastRevisedAt && !b.lastRevisedAt) {
        return a.title.localeCompare(b.title);
      }
      if (!a.lastRevisedAt) {
        return -1;
      }
      if (!b.lastRevisedAt) {
        return 1;
      }
      return new Date(a.lastRevisedAt).getTime() - new Date(b.lastRevisedAt).getTime();
    })[0];

  const difficultyData = ["easy", "medium", "expert"].map((difficulty) => {
    const matches = completed.filter((session) => session.difficulty === difficulty && session.accuracy_pct !== null);
    const avg = matches.length
      ? Math.round(matches.reduce((sum, row) => sum + Number(row.accuracy_pct || 0), 0) / matches.length)
      : 0;

    return {
      difficulty,
      accuracy: avg,
      attempts: matches.length
    };
  });

  const trendData = completed.slice(-8).map((session) => ({
    name: getTopicTitle(session, topicsById).replace(/^(.{14}).+$/, "$1..."),
    accuracy: Number(session.accuracy_pct || 0)
  }));

  const skillData = tagBreakdown
    .map((item) => ({
      label: item.tag.replace(/-/g, " "),
      score: item.total ? Math.round((item.correct / item.total) * 100) : 0,
      attempts: item.total
    }))
    .sort((a, b) => a.score - b.score)
    .slice(0, 4);

  return (
    <section className="stack gap-md" aria-label="Revision statistics">
      <div className="stats-grid">
        <article className="panel insight-card">
          <span className="eyebrow">Strongest topic</span>
          <h3>{strongestTopic?.title || "No topic data yet"}</h3>
          <p>
            {strongestTopic
              ? `${strongestTopic.averageAccuracy}% average across ${strongestTopic.attempts} session(s).`
              : "Complete a session to start building topic statistics."}
          </p>
        </article>

        <article className="panel insight-card warning-card">
          <span className="eyebrow">Needs attention</span>
          <h3>{needsWorkTopic?.title || "No weak topic yet"}</h3>
          <p>
            {needsWorkTopic
              ? `${needsWorkTopic.averageAccuracy}% average. Start with easy or medium to rebuild confidence.`
              : "A topic needing work will appear once there is enough data."}
          </p>
        </article>

        <article className="panel insight-card">
          <span className="eyebrow">Revise next</span>
          <h3>{leastRecentTopic?.title || "Choose any topic"}</h3>
          <p>
            {leastRecentTopic
              ? `Last revised: ${formatDate(leastRecentTopic.lastRevisedAt)}.`
              : "Pick a topic to begin your revision record."}
          </p>
        </article>

        <article className="panel accent-panel insight-card">
          <span className="eyebrow">Streak</span>
          <p className="streak">{streak} sessions</p>
          <p>{streak >= 5 ? "Consistency Champion" : streak >= 3 ? "Momentum Builder" : "Getting Started"}</p>
        </article>
      </div>

      <article className="panel">
        <h3>Topic Revision Snapshot</h3>
        <div className="responsive-table">
          <table className="table compact-table">
            <thead>
              <tr>
                <th>Topic</th>
                <th>Sessions</th>
                <th>Average</th>
                <th>Last Revised</th>
                <th>Advice</th>
              </tr>
            </thead>
            <tbody>
              {topicStats.map((stat) => (
                <tr key={stat.topicId}>
                  <td>{stat.title}</td>
                  <td>{stat.attempts}</td>
                  <td>{stat.averageAccuracy === null ? "-" : `${stat.averageAccuracy}%`}</td>
                  <td>{formatDate(stat.lastRevisedAt)}</td>
                  <td>{getAction(stat)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <section className="stats-grid">
        <article className="panel">
          <h3>Progress by Difficulty</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={difficultyData}>
              <CartesianGrid strokeDasharray="4 4" />
              <XAxis dataKey="difficulty" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="accuracy" fill="#136f63" name="Accuracy %" />
              <Bar dataKey="attempts" fill="#f4a259" name="Sessions" />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <h3>Recent Topic Trend</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={trendData.length ? trendData : [{ name: "No sessions", accuracy: 0 }]}>
              <CartesianGrid strokeDasharray="4 4" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="accuracy" fill="#1d3557" name="Accuracy %" />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <h3>Question Skills To Watch</h3>
          {skillData.length ? (
            <ul className="skill-list">
              {skillData.map((item) => (
                <li key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.score}%</strong>
                </li>
              ))}
            </ul>
          ) : (
            <p>Question skill data will appear after completed sessions.</p>
          )}
        </article>
      </section>
    </section>
  );
}
