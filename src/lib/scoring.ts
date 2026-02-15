import type { Difficulty, Question } from "./types";

function normaliseText(input: string): string {
  return input.trim().toLowerCase().replace(/\s+/g, " ");
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export interface MatchCorrection {
  left: string;
  selected: string;
  expected: string;
}

export function evaluateAnswer(question: Question, userAnswer: Record<string, unknown>): boolean {
  const correct = question.correct_answer_json;

  switch (question.format) {
    case "mcq": {
      return userAnswer.choice === correct.choice;
    }
    case "fill_gap": {
      const typed = String(userAnswer.text || "");
      const normalisedTyped = normaliseText(typed);
      if (!normalisedTyped) {
        return false;
      }

      const accepted = asArray(correct.accepted).map((item) => normaliseText(String(item)));
      return accepted.some(
        (term) => normalisedTyped === term || normalisedTyped.includes(term) || term.includes(normalisedTyped)
      );
    }
    case "short_text":
    case "structured_response": {
      const typed = String(userAnswer.text || "");
      const accepted = asArray(correct.accepted).map((item) => normaliseText(String(item)));
      return accepted.includes(normaliseText(typed));
    }
    case "diagram_label": {
      if (typeof correct.choice === "string" && typeof userAnswer.choice === "string") {
        return userAnswer.choice === correct.choice;
      }

      const typed = String(userAnswer.text || "");
      const accepted = asArray(correct.accepted).map((item) => normaliseText(String(item)));
      return accepted.includes(normaliseText(typed));
    }
    case "drag_drop": {
      const userOrder = asArray(userAnswer.order).map(String);
      const correctOrder = asArray(correct.order).map(String);
      return JSON.stringify(userOrder) === JSON.stringify(correctOrder);
    }
    case "match_table": {
      const userPairs = (userAnswer.pairs as Record<string, string>) || {};
      const correctPairs = (correct.pairs as Record<string, string>) || {};
      const keys = Object.keys(correctPairs);
      return keys.every((key) => userPairs[key] === correctPairs[key]);
    }
    default:
      return false;
  }
}

export function getMatchCorrections(
  question: Question,
  userAnswer: Record<string, unknown>
): MatchCorrection[] {
  if (question.format !== "match_table") {
    return [];
  }

  const userPairs = (userAnswer.pairs as Record<string, string>) || {};
  const correctPairs = (question.correct_answer_json.pairs as Record<string, string>) || {};

  return Object.keys(correctPairs)
    .filter((left) => userPairs[left] !== correctPairs[left])
    .map((left) => ({
      left,
      selected: userPairs[left] || "",
      expected: correctPairs[left]
    }));
}

export function getAdaptiveRecommendation(difficulty: Difficulty, accuracyPct: number): {
  headline: string;
  detail: string;
  nextDifficulty: Difficulty;
} {
  if (accuracyPct >= 80) {
    const next = difficulty === "easy" ? "medium" : difficulty === "medium" ? "expert" : "expert";
    return {
      headline: "Ready to stretch further",
      detail: "Your recent accuracy is strong. Try stepping up in challenge to keep improving.",
      nextDifficulty: next
    };
  }

  if (accuracyPct <= 45) {
    const next = difficulty === "expert" ? "medium" : "easy";
    return {
      headline: "Consolidate first",
      detail: "Focus on key terms and structure. A slightly easier level now can build confidence quickly.",
      nextDifficulty: next
    };
  }

  return {
    headline: "Stay steady",
    detail: "Keep practicing this level for consistency, then step up after another strong session.",
    nextDifficulty: difficulty
  };
}

export function computeStreak(sessions: Array<{ completed_at: string | null; accuracy_pct: number | null }>): number {
  const complete = sessions
    .filter((session) => session.completed_at && session.accuracy_pct !== null)
    .sort((a, b) => new Date(a.completed_at!).getTime() - new Date(b.completed_at!).getTime());

  let streak = 0;
  for (const session of complete) {
    if ((session.accuracy_pct || 0) >= 60) {
      streak += 1;
    } else {
      streak = 0;
    }
  }
  return streak;
}
