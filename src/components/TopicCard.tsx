import type { Difficulty, Topic } from "../lib/types";

export function TopicCard({
  topic,
  onStart,
  caps
}: {
  topic: Topic;
  onStart: (difficulty: Difficulty) => void;
  caps: Record<Difficulty, number>;
}) {
  const disabled = !topic.is_enabled;

  return (
    <article className={`topic-card ${disabled ? "locked" : ""}`}>
      <h3>{topic.title}</h3>
      {disabled ? <p className="lock-pill">Coming Soon</p> : null}

      {!disabled ? (
        <div className="difficulty-grid">
          {(["easy", "medium", "expert"] as Difficulty[]).map((difficulty) => {
            const remaining = Math.max(0, 3 - (caps[difficulty] || 0));
            const locked = remaining <= 0;
            return (
              <button
                key={difficulty}
                disabled={locked}
                className="difficulty-btn"
                onClick={() => onStart(difficulty)}
              >
                <span>{difficulty.toUpperCase()}</span>
                <small>{locked ? "Locked today" : `${remaining} sessions left`}</small>
              </button>
            );
          })}
        </div>
      ) : null}
    </article>
  );
}
