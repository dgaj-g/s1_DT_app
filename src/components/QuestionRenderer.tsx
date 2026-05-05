import { NetworkDiagram } from "./NetworkDiagram";
import { cleanQuestionStemForDisplay, isPublicHelperText } from "../lib/questionDisplay";
import { supabase } from "../lib/supabase";
import type {
  Question,
  RuntimeAsset,
  RuntimeChoice,
  RuntimeQuestionFeedback,
  RuntimeSessionQuestion
} from "../lib/types";

function isRuntimeQuestion(question: Question | RuntimeSessionQuestion): question is RuntimeSessionQuestion {
  return "response_schema" in question;
}

function getRuntimeMatchCorrections(feedback?: RuntimeQuestionFeedback | null): Record<string, string> {
  const corrections = Array.isArray(feedback?.corrections) ? feedback.corrections : [];
  return corrections.reduce<Record<string, string>>((acc, item) => {
    if (!item || typeof item !== "object") {
      return acc;
    }
    const rowId = typeof (item as Record<string, unknown>).row_id === "string"
      ? ((item as Record<string, unknown>).row_id as string)
      : "";
    const expectedChoiceId = typeof (item as Record<string, unknown>).expected_choice_id === "string"
      ? ((item as Record<string, unknown>).expected_choice_id as string)
      : "";

    if (rowId && expectedChoiceId) {
      acc[rowId] = expectedChoiceId;
    }
    return acc;
  }, {});
}

const visualPromptKinds = new Set(["figure", "diagram", "table_image", "screenshot", "chart", "photo", "image"]);

function normalizeBlockText(value: unknown) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function repeatsStemContext(text: string, stemText: string) {
  if (!text || !stemText) {
    return false;
  }
  return text === stemText || stemText.includes(text) || text.includes(stemText);
}

function getAssetUrl(asset: RuntimeAsset) {
  const directUrl = typeof asset.url === "string" ? asset.url : typeof asset.public_url === "string" ? asset.public_url : "";
  if (directUrl) {
    return directUrl;
  }

  if (!asset.bucket || !asset.path) {
    return "";
  }

  const { data } = supabase.storage.from(asset.bucket).getPublicUrl(asset.path);
  return data.publicUrl;
}

function renderRuntimeAsset(asset: RuntimeAsset, fallbackKey: string) {
  const url = getAssetUrl(asset);
  const caption = asset.caption || "";
  const altText = asset.alt_text || caption || "Question visual aid";

  return (
    <figure className="question-asset-card" key={asset.asset_id || asset.path || fallbackKey}>
      {url ? <img src={url} alt={altText} loading="lazy" /> : null}
      {caption ? <figcaption>{caption}</figcaption> : null}
      {!url && asset.path ? <p className="question-helper">Visual aid path: {asset.path}</p> : null}
    </figure>
  );
}

function renderRuntimePrompt(question: RuntimeSessionQuestion) {
  const promptBlocks = question.prompt_blocks || [];
  const assets = (question.assets || []).filter((asset) => (asset.role || "prompt") === "prompt");
  const usedAssetKeys = new Set<string>();
  const stemText = normalizeBlockText(cleanQuestionStemForDisplay(question.stem));

  const blocks = promptBlocks.flatMap((block, index) => {
    const kind = normalizeBlockText(block.kind).toLowerCase();
    const blockKey = typeof block.block_key === "string" ? block.block_key : "";

    if (visualPromptKinds.has(kind)) {
      const matchingAssets = assets.filter((asset) => asset.block_key === blockKey);
      if (matchingAssets.length > 0) {
        return matchingAssets.map((asset, assetIndex) => {
          usedAssetKeys.add(asset.asset_id || asset.path || `${blockKey}-${assetIndex}`);
          return renderRuntimeAsset(asset, `${index}-${assetIndex}`);
        });
      }

      const caption = normalizeBlockText(block.caption || block.title || block.text);
      return caption ? [<p className="question-helper" key={`visual-caption-${index}`}>{caption}</p>] : [];
    }

    if (kind === "text") {
      const text = normalizeBlockText(block.text || block.body);
      if (!text || isPublicHelperText(text) || repeatsStemContext(text, stemText)) {
        return [];
      }
      return [<p className="question-helper" key={`text-${index}`}>{text}</p>];
    }

    if (kind === "list_block" && Array.isArray(block.items)) {
      return [
        <div className="question-prompt-list" key={`list-${index}`}>
          {block.label ? <p>{String(block.label)}</p> : null}
          <ul>
            {block.items.map((item, itemIndex) => (
              <li key={`${index}-${itemIndex}`}>{String(item)}</li>
            ))}
          </ul>
        </div>
      ];
    }

    const text = normalizeBlockText(block.text || block.body || block.title || block.caption);
    return text && !repeatsStemContext(text, stemText)
      ? [<p className="question-helper" key={`block-${index}`}>{text}</p>]
      : [];
  });

  const unmatchedAssets = assets.filter((asset, index) => {
    const key = asset.asset_id || asset.path || `${asset.block_key || "asset"}-${index}`;
    return !usedAssetKeys.has(key);
  });

  if (blocks.length === 0 && unmatchedAssets.length === 0) {
    return null;
  }

  return (
    <div className="runtime-prompt stack gap-sm">
      {blocks}
      {unmatchedAssets.map((asset, index) => renderRuntimeAsset(asset, `unmatched-${index}`))}
    </div>
  );
}

function renderRuntimeQuestion(
  question: RuntimeSessionQuestion,
  answer: Record<string, unknown>,
  onChange: (next: Record<string, unknown>) => void,
  isLocked: boolean,
  showFeedback: boolean,
  feedback?: RuntimeQuestionFeedback | null
) {
  const schema = question.response_schema;

  if (schema.kind === "single_choice") {
    return (
      <div className="stack gap-sm">
        {schema.choices.map((choice) => (
          <label key={choice.id} className="choice-row">
            <input
              type="radio"
              name={`q-${question.session_item_id || question.question_id}`}
              checked={answer.choice === choice.id}
              disabled={isLocked}
              onChange={() => onChange({ choice: choice.id })}
            />
            <span>{choice.label}</span>
          </label>
        ))}
      </div>
    );
  }

  if (schema.kind === "true_false") {
    const statement = schema.statement && schema.statement !== question.stem ? schema.statement : null;
    return (
      <div className="stack gap-sm">
        {statement ? <p className="question-helper">{statement}</p> : null}
        <label className="choice-row">
          <input
            type="radio"
            name={`q-${question.session_item_id || question.question_id}`}
            checked={answer.value === true}
            disabled={isLocked}
            onChange={() => onChange({ value: true })}
          />
          <span>{schema.true_label || "True"}</span>
        </label>
        <label className="choice-row">
          <input
            type="radio"
            name={`q-${question.session_item_id || question.question_id}`}
            checked={answer.value === false}
            disabled={isLocked}
            onChange={() => onChange({ value: false })}
          />
          <span>{schema.false_label || "False"}</span>
        </label>
      </div>
    );
  }

  if (schema.kind === "short_text") {
    return (
      <textarea
        className="answer-box"
        value={String(answer.text || "")}
        readOnly={isLocked}
        maxLength={schema.max_length}
        onChange={(event) => onChange({ text: event.target.value })}
        placeholder={schema.placeholder || "Type your answer"}
      />
    );
  }

  if (schema.kind === "fill_gap") {
    const gaps = schema.gaps || [];
    const gapAnswers = (answer.gaps || {}) as Record<string, string>;

    if (gaps.length <= 1) {
      const gapId = gaps[0]?.id || "gap1";
      return (
        <textarea
          className="answer-box"
          value={String(gapAnswers[gapId] || answer.text || "")}
          readOnly={isLocked}
          onChange={(event) =>
            onChange({
              text: event.target.value,
              gaps: {
                [gapId]: event.target.value
              }
            })
          }
          placeholder="Type your answer"
        />
      );
    }

    return (
      <div className="stack gap-sm">
        {gaps.map((gap) => (
          <label key={gap.id} className="stack gap-xs">
            <span>{gap.label}</span>
            <input
              className="answer-input"
              type="text"
              value={gapAnswers[gap.id] || ""}
              readOnly={isLocked}
              onChange={(event) =>
                onChange({
                  gaps: {
                    ...gapAnswers,
                    [gap.id]: event.target.value
                  }
                })
              }
              placeholder="Type your answer"
            />
          </label>
        ))}
      </div>
    );
  }

  if (schema.kind === "multi_select") {
    const selected = Array.isArray(answer.choice_ids) ? (answer.choice_ids as string[]) : [];
    const minSelect = schema.min_select ?? 0;
    const maxSelect = schema.max_select ?? schema.choices.length;

    function toggleChoice(choiceId: string) {
      const next = selected.includes(choiceId)
        ? selected.filter((item) => item !== choiceId)
        : [...selected, choiceId];

      if (next.length > maxSelect) {
        return;
      }

      onChange({ choice_ids: next });
    }

    return (
      <div className="stack gap-sm">
        {minSelect > 0 || maxSelect > 0 ? (
          <p className="question-helper">
            Select {minSelect > 0 ? `at least ${minSelect}` : "the correct"}
            {maxSelect < schema.choices.length ? ` and no more than ${maxSelect}` : " option(s)"}.
          </p>
        ) : null}
        {schema.choices.map((choice) => (
          <label key={choice.id} className="choice-row">
            <input
              type="checkbox"
              checked={selected.includes(choice.id)}
              disabled={isLocked}
              onChange={() => toggleChoice(choice.id)}
            />
            <span>{choice.label}</span>
          </label>
        ))}
      </div>
    );
  }

  if (schema.kind === "ordering") {
    const items = Array.isArray(schema.items) ? schema.items : [];
    const fromAnswer = Array.isArray(answer.order_ids) ? (answer.order_ids as string[]) : [];
    const currentIds = fromAnswer.length ? fromAnswer : items.map((item) => item.id);
    const currentItems = currentIds
      .map((id) => items.find((item) => item.id === id))
      .filter(Boolean) as RuntimeChoice[];

    function move(index: number, direction: -1 | 1) {
      const nextIndex = index + direction;
      if (nextIndex < 0 || nextIndex >= currentItems.length) {
        return;
      }

      const next = [...currentItems];
      [next[index], next[nextIndex]] = [next[nextIndex], next[index]];
      onChange({ order_ids: next.map((item) => item.id) });
    }

    return (
      <div className="stack gap-xs">
        {currentItems.map((item, index) => (
          <div className="drag-row" key={item.id}>
            <span>
              {index + 1}. {item.label}
            </span>
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

  if (schema.kind === "match_table") {
    const selectedPairs = (answer.pairs || {}) as Record<string, string>;
    const corrections = showFeedback ? getRuntimeMatchCorrections(feedback) : {};

    return (
      <table className="match-table">
        <thead>
          <tr>
            <th>Term</th>
            <th>Match</th>
          </tr>
        </thead>
        <tbody>
          {schema.rows.map((row) => {
            const selected = selectedPairs[row.id] || "";
            let stateClass = "match-select";
            if (showFeedback && selected) {
              stateClass = corrections[row.id]
                ? "match-select is-wrong"
                : "match-select is-correct";
            }

            return (
              <tr key={row.id}>
                <td>{row.label}</td>
                <td>
                  <select
                    className={stateClass}
                    disabled={isLocked}
                    value={selected}
                    onChange={(event) => {
                      onChange({
                        pairs: {
                          ...selectedPairs,
                          [row.id]: event.target.value
                        }
                      });
                    }}
                  >
                    <option value="">Select...</option>
                    {schema.choices.map((choice) => (
                      <option value={choice.id} key={choice.id}>
                        {choice.label}
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

  if (schema.kind === "diagram_label") {
    const typedMode = schema.input_mode === "text";
    const marker = schema.marker || "";

    return (
      <div className="stack gap-sm">
        {schema.diagram_key ? (
          <div className="diagram-wrap">
            <NetworkDiagram diagramKey={schema.diagram_key} />
            {marker ? <p className="diagram-callout">Use marker {marker} in the diagram.</p> : null}
          </div>
        ) : null}

        {typedMode ? (
          <textarea
            className="answer-box"
            value={String(answer.text || "")}
            readOnly={isLocked}
            onChange={(event) => onChange({ text: event.target.value })}
            placeholder={schema.placeholder || "Type your label"}
          />
        ) : (
          <div className="stack gap-sm">
            {(schema.choices || []).map((choice) => (
              <label key={choice.id} className="choice-row">
                <input
                  type="radio"
                  name={`q-${question.session_item_id || question.question_id}`}
                  checked={answer.choice === choice.id}
                  disabled={isLocked}
                  onChange={() => onChange({ choice: choice.id })}
                />
                <span>{choice.label}</span>
              </label>
            ))}
          </div>
        )}
      </div>
    );
  }

  return <div className="error-box">Unsupported runtime question format in this build.</div>;
}

function renderLegacyQuestion(
  question: Question,
  answer: Record<string, unknown>,
  onChange: (next: Record<string, unknown>) => void,
  isLocked: boolean,
  showFeedback: boolean
) {
  const options = (question.options_json || {}) as Record<string, unknown>;

  const dragOrder = (() => {
    if (question.format !== "drag_drop") {
      return [];
    }

    const fromAnswer = Array.isArray(answer.order) ? (answer.order as string[]) : [];
    if (fromAnswer.length) {
      return fromAnswer;
    }

    return Array.isArray(options.items) ? (options.items as string[]) : [];
  })();

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
    function move(index: number, direction: -1 | 1) {
      const nextIndex = index + direction;
      if (nextIndex < 0 || nextIndex >= dragOrder.length) {
        return;
      }

      const next = [...dragOrder];
      [next[index], next[nextIndex]] = [next[nextIndex], next[index]];
      onChange({ order: next });
    }

    return (
      <div className="stack gap-xs">
        {dragOrder.map((item, index) => (
          <div className="drag-row" key={item + index}>
            <span>
              {index + 1}. {item}
            </span>
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

export function QuestionRenderer({
  question,
  answer,
  onChange,
  isLocked = false,
  showFeedback = false,
  feedback = null
}: {
  question: Question | RuntimeSessionQuestion;
  answer: Record<string, unknown>;
  onChange: (next: Record<string, unknown>) => void;
  isLocked?: boolean;
  showFeedback?: boolean;
  feedback?: RuntimeQuestionFeedback | null;
}) {
  if (isRuntimeQuestion(question)) {
    return (
      <>
        {renderRuntimePrompt(question)}
        {renderRuntimeQuestion(question, answer, onChange, isLocked, showFeedback, feedback)}
      </>
    );
  }

  return renderLegacyQuestion(question, answer, onChange, isLocked, showFeedback);
}
