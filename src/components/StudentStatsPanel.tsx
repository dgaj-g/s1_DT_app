import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { SessionRecord } from "../lib/types";

interface Props {
  sessions: SessionRecord[];
  tagBreakdown: Array<{ tag: string; total: number; correct: number }>;
  streak: number;
}

export function StudentStatsPanel({ sessions, tagBreakdown, streak }: Props) {
  const completed = sessions.filter((session) => session.completed_at);

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

  const trendData = completed.slice(-8).map((session, index) => ({
    name: `S${index + 1}`,
    accuracy: Number(session.accuracy_pct || 0)
  }));

  const radarData = tagBreakdown.map((item) => ({
    tag: item.tag,
    score: item.total ? Math.round((item.correct / item.total) * 100) : 0
  }));

  return (
    <section className="stats-grid">
      <article className="panel">
        <h3>Progress by Difficulty</h3>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={difficultyData}>
            <CartesianGrid strokeDasharray="4 4" />
            <XAxis dataKey="difficulty" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="accuracy" fill="#136f63" name="Accuracy %" />
            <Bar dataKey="attempts" fill="#f4a259" name="Sessions" />
          </BarChart>
        </ResponsiveContainer>
      </article>

      <article className="panel">
        <h3>Weak / Strong Topic Radar</h3>
        <ResponsiveContainer width="100%" height={260}>
          <RadarChart outerRadius={90} data={radarData.length ? radarData : [{ tag: "No data", score: 0 }]}>
            <PolarGrid />
            <PolarAngleAxis dataKey="tag" />
            <Tooltip />
            <Radar dataKey="score" stroke="#e63946" fill="#e63946" fillOpacity={0.45} />
          </RadarChart>
        </ResponsiveContainer>
      </article>

      <article className="panel">
        <h3>Recent Trend</h3>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={trendData.length ? trendData : [{ name: "S1", accuracy: 0 }]}>
            <CartesianGrid strokeDasharray="4 4" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Bar dataKey="accuracy" fill="#1d3557" />
          </BarChart>
        </ResponsiveContainer>
      </article>

      <article className="panel accent-panel">
        <h3>Streak Badge</h3>
        <p className="streak">{streak} sessions</p>
        <p>{streak >= 5 ? "Consistency Champion" : streak >= 3 ? "Momentum Builder" : "Getting Started"}</p>
      </article>
    </section>
  );
}
