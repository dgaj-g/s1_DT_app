import { useMemo } from "react";
import { NetworkDiagram } from "./NetworkDiagram";
import type { Question } from "../lib/types";

export function QuestionRenderer({
  question,
  answer,
  onChange,
  isLocked = false,
  showFeedback = false
}: {
  question: Question;
  answer: Record<string, unknown>;
  onChange: (next: Record<string, unknown>) => void;
  isLocked?: boolean;
  showFeedback?: boolean;
}) {
  const options = (question.options_json || {}) as Record<string, unknown>;

  const dragOrder = useMemo<string[]>(() => {
    if (question.format !== "drag_drop") {
      return [];
    }

    const fromAnswer = Array.isArray(answer.order) ? (answer.order as string[]) : [];
    if (fromAnswer.length) {
      return fromAnswer;
    }

    return Array.isArray(options.items) ? (options.items as string[]) : [];
  }, [answer.order, options.items, question.format]);

  if (question.format === "mcq") {
    const choices = Array.isArray(options.choices) ? (options.choices as string[]) : [];

    return (
      <div className="stack gap-sm">
        {choices.map((choice) => (
          <label key={choice} className="choice-row">
            <input
              type="radio"
              name={`q-${question.id}`}
              checked={answer.choice === choice}
              disabled={isLocked}
              onChange={() => onChange({ choice })}
            />
            <span>{choice}</span>
          </label>
        ))}
      </div>
    );
  }

  if (
    question.format === "fill_gap" ||
    question.format === "short_text" ||
    question.format === "structured_response"
  ) {
    return (
      <textarea
        className="answer-box"
        value={String(answer.text || "")}
        readOnly={isLocked}
        onChange={(event) => onChange({ text: event.target.value })}
        placeholder="Type your answer"
      />
    );
  }

  if (question.format === "diagram_label") {
    const choices = Array.isArray(options.choices) ? (options.choices as string[]) : [];
    const diagramKey = typeof options.diagram_key === "string" ? options.diagram_key : "";
    const marker =
      typeof options.marker === "string"
        ? options.marker
        : typeof options.callout === "string"
          ? options.callout
          : "";

    if (choices.length) {
      return (
        <div className="stack gap-sm">
          {diagramKey ? (
            <div className="diagram-wrap">
              <NetworkDiagram diagramKey={diagramKey} />
              {marker ? <p className="diagram-callout">Use marker {marker} in the diagram.</p> : null}
            </div>
          ) : null}
          {choices.map((choice) => (
            <label key={choice} className="choice-row">
              <input
                type="radio"
                name={`q-${question.id}`}
                checked={answer.choice === choice}
                disabled={isLocked}
                onChange={() => onChange({ choice })}
              />
              <span>{choice}</span>
            </label>
          ))}
        </div>
      );
    }

    return (
      <textarea
        className="answer-box"
        value={String(answer.text || "")}
        readOnly={isLocked}
        onChange={(event) => onChange({ text: event.target.value })}
        placeholder="Type your label"
      />
    );
  }

  if (question.format === "drag_drop") {
    const current = dragOrder;

    function move(index: number, direction: -1 | 1) {
      const nextIndex = index + direction;
      if (nextIndex < 0 || nextIndex >= current.length) {
        return;
      }

      const next = [...current];
      [next[index], next[nextIndex]] = [next[nextIndex], next[index]];
      onChange({ order: next });
    }

    return (
      <div className="stack gap-xs">
        {current.map((item, index) => (
          <div className="drag-row" key={item + index}>
            <span>{index + 1}. {item}</span>
            <div>
              <button type="button" onClick={() => move(index, -1)} className="small-btn" disabled={isLocked}>
                Up
              </button>
              <button type="button" onClick={() => move(index, 1)} className="small-btn" disabled={isLocked}>
                Down
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (question.format === "match_table") {
    const pairs = Array.isArray(options.pairs) ? (options.pairs as Array<{ left: string; right: string }>) : [];
    const choices = Array.isArray(options.choices)
      ? (options.choices as string[])
      : pairs.map((entry) => entry.right);

    const userPairs = (answer.pairs || {}) as Record<string, string>;
    const expectedPairs = ((question.correct_answer_json || {}).pairs || {}) as Record<string, string>;

    return (
      <table className="match-table">
        <thead>
          <tr>
            <th>Term</th>
            <th>Match</th>
          </tr>
        </thead>
        <tbody>
          {pairs.map((pair) => {
            const selected = userPairs[pair.left] || "";
            let stateClass = "match-select";
            if (showFeedback && selected) {
              stateClass =
                selected === expectedPairs[pair.left]
                  ? "match-select is-correct"
                  : "match-select is-wrong";
            }

            return (
              <tr key={pair.left}>
                <td>{pair.left}</td>
                <td>
                  <select
                    className={stateClass}
                    disabled={isLocked}
                    value={selected}
                    onChange={(event) => {
                      onChange({
                        pairs: {
                          ...userPairs,
                          [pair.left]: event.target.value
                        }
                      });
                    }}
                  >
                    <option value="">Select...</option>
                    {choices.map((choice, index) => (
                      <option value={choice} key={`${choice}-${index}`}>
                        {choice}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    );
  }

  return <div className="error-box">Unsupported question format in this build.</div>;
}
