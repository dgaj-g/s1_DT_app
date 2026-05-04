#!/usr/bin/env python3
"""Build a normalized Unit 1 import bundle from the curated source pack.

This script does not write directly into Supabase. It transforms the curated
markdown and figure sources into a structured JSON bundle suitable for the
Stage 3 staging tables:

- import_batches
- staged_questions
- staged_question_assets

The goal is to automate the first pass of enrichment so the content owner does
not need to hand-tag every question.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from unit1_objectives import OBJECTIVES_BY_CODE, infer_objective_codes


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = REPO_ROOT.parent / "GCSE Unit 1 Revision Project"
DEFAULT_OUTPUT = REPO_ROOT / "supabase" / "imports" / "unit1_stage4_import_bundle.json"

TOPIC_SLUG_BY_TITLE = {
    "Topic 1: Digital data": "digital-data",
    "Topic 2: Software": "software",
    "Topic 3: Database applications": "database-applications",
    "Topic 4: Spreadsheet applications": "spreadsheet-applications",
    "Topic 5: Computer hardware": "computer-hardware",
    "Topic 6: Network technologies": "network-technologies",
    "Topic 7: Cyberspace, network security and data transfer": "cyberspace-network-security-and-data-transfer",
    "Topic 8: Cloud technology": "cloud-technology",
    "Topic 9: Ethical, legal and environmental impact": "ethical-legal-and-environmental-impact",
    "Topic 10: Changes in employment opportunities, skills requirements and work practices": "changes-in-employment-opportunities-skills-requirements-and-work-practices",
    "Topic 11: Health and safety": "health-and-safety",
    "Topic 12: Digital applications": "digital-applications",
}

TOPIC_TITLE_BY_SHORT = {
    "Digital data": "Topic 1: Digital data",
    "Software": "Topic 2: Software",
    "Database applications": "Topic 3: Database applications",
    "Spreadsheet applications": "Topic 4: Spreadsheet applications",
    "Computer hardware": "Topic 5: Computer hardware",
    "Network technologies": "Topic 6: Network technologies",
    "Cyberspace, network security and data transfer": "Topic 7: Cyberspace, network security and data transfer",
    "Cloud technology": "Topic 8: Cloud technology",
    "Ethical, legal and environmental impact": "Topic 9: Ethical, legal and environmental impact",
    "Changes in employment opportunities, skills requirements and work practices": "Topic 10: Changes in employment opportunities, skills requirements and work practices",
    "Health and safety": "Topic 11: Health and safety",
    "Digital applications": "Topic 12: Digital applications",
}

TOPIC_CONCEPT_RULES = {
    "network-technologies": [
        ("topology-bus", ("bus", "backbone", "terminator")),
        ("topology-ring", ("ring", "node to node", "closed loop")),
        ("topology-star", ("star", "central device", "hub", "switch")),
        ("internet-web", ("world wide web", "www", "internet", "intranet")),
        ("iot", ("iot", "internet of things")),
        ("communication-media", ("bluetooth", "wi-fi", "5g", "fibre", "fiber", "optical")),
        ("network-devices", ("router", "switch", "nic", "file server")),
    ],
    "database-applications": [
        ("data-types", ("data type", "currency", "boolean", "date/time", "text")),
        ("validation", ("validation", "presence", "range", "format", "length")),
        ("keys", ("key field", "primary key")),
        ("query", ("query", "criteria", "sorted", "filter")),
        ("report", ("report", "grouped", "printed")),
        ("form", ("form", "capture", "input box")),
    ],
    "spreadsheet-applications": [
        ("cell-reference", ("cell reference", "absolute", "$")),
        ("formula", ("formula", "sum", "average", "max", "min")),
        ("lookup", ("vlookup", "lookup")),
        ("csv", ("csv", "comma separated")),
        ("formatting", ("conditional formatting", "merge", "wrap text")),
        ("chart", ("chart", "graph", "pie chart", "bar chart")),
    ],
    "software": [
        ("operating-system", ("operating system", "booting", "resources", "interface")),
        ("utility", ("utility", "backup", "restore", "antivirus")),
    ],
    "digital-data": [
        ("data-measurement", ("terabyte", "kilobyte", "bit rate", "bit depth", "sample rate")),
        ("graphics", ("bitmap", "vector", "pixel", "jpeg", "png", "bmp")),
        ("sound", ("bit rate", "sample rate", "sound file", "wav")),
        ("portability", ("portability", "pdf", "txt", "jpeg", "wav")),
    ],
}

STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "with", "what",
    "which", "is", "are", "does", "do", "state", "name", "give", "identify", "choose",
    "correct", "best", "following", "using", "from", "about", "this", "that", "these",
    "those", "used", "into", "below", "shown", "above", "type", "term", "list", "two",
    "one", "three", "four",
}

QUESTION_HEADING_RE = re.compile(r"^###\s+Q(\d+(?:\s*\([^)]+\))?(?:\([^)]+\))?)\s*\[([^\]]+)\]\s*[—\-]\s*(.+?)\s*$")
TOPIC_HEADING_RE = re.compile(r"^#{1,2}\s+Topic\s+(\d+):\s*(.+?)\s*$", re.MULTILINE)
FIGURE_MARKER_RE = re.compile(r"^\[FIGURE:\s*(.+?)\]\s*$")
SOURCE_LINE_RE = re.compile(r"^\*?\[Source:\s*(.*?)\]\*?\s*$")
STRUCTURAL_BLOCK_LABELS = {
    "terms", "term", "definitions", "definition", "statements", "statement",
    "examples", "example", "descriptions", "description", "functions", "function",
    "purposes", "purpose", "resources", "resource", "reasons", "reason",
    "pairs", "pair", "options", "option",
}
LETTERED_CHOICE_RE = re.compile(r"\b([A-Z])\.\s*(.+?)(?=(?:\s*;\s*[A-Z]\.\s)|$)")
ARROW_PAIR_RE = re.compile(r"^\s*(.+?)\s*(?:→|->|=>)\s*(.+?)\s*$")
CODED_CHOICE_RE = re.compile(r"^\s*(.+?)\s*\(([A-Z])\)\s*$")
ANY_N_FROM_RE = re.compile(
    r"^Any\s+(?:(\d+)|(two|three|four))\s+(?:from|of)\s*:\s*(.+?)\.?\s*$",
    flags=re.IGNORECASE,
)
ANY_N_SUFFIX_RE = re.compile(
    r"^(.*?)\s*\(any\s+((?:\d+)|(?:two|three|four))\)\.?\s*$",
    flags=re.IGNORECASE,
)
PARENTHETICAL_OR_RE = re.compile(r"^(.*?)\s*\(or\s+(.*?)\)\s*$", flags=re.IGNORECASE)
BLANK_RE = re.compile(r"_{2,}")
ORDERING_STEM_SIGNALS = (
    "place the following",
    "arrange the following",
    "put the following",
    "correct order",
)

ACCEPTED_ANSWER_OVERRIDES = {
    "database-applications.past_paper.topics_03_04.q003": [
        "Uniquely identifies a record",
        "Uniquely identifies a member",
        "Uniquely identifies an individual",
    ],
    "database-applications.practice_bank.topic_02_03_software_database.q058": [
        "Entity-Relationship (ER) diagram",
        "Entity-Relationship diagram",
        "ER diagram",
    ],
}


@dataclass
class ParsedQuestion:
    question_label: str
    marks_text: str
    qtype: str
    source_line: str
    body_segments: list[tuple[str, object]]
    options: list[tuple[str, str]]
    answer: str


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def stable_hash(text: str, length: int = 10) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def split_semicolon_items(text: str) -> list[str]:
    parts: list[str] = []
    buffer: list[str] = []
    depth = 0

    for char in text:
        if char == "(":
            depth += 1
        elif char == ")" and depth > 0:
            depth -= 1

        if char == ";" and depth == 0:
            piece = normalize_text("".join(buffer))
            if piece:
                parts.append(piece)
            buffer = []
            continue

        buffer.append(char)

    tail = normalize_text("".join(buffer))
    if tail:
        parts.append(tail)

    return parts


def parse_arrow_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for piece in split_semicolon_items(text):
        match = ARROW_PAIR_RE.match(piece)
        if not match:
            return []
        left = normalize_text(match.group(1))
        right = normalize_text(match.group(2))
        if not left or not right:
            return []
        pairs.append((left, right))
    return pairs


def expand_embedded_list_items(items: list[str]) -> list[str]:
    normalized_items = [normalize_text(item) for item in items if normalize_text(item)]
    if len(normalized_items) == 1 and ":" in normalized_items[0]:
        prefix, tail = normalized_items[0].split(":", 1)
        if normalize_text(prefix).lower() in {
            "terms",
            "measures",
            "health problems",
            "prevention methods",
            "examples",
            "descriptions",
            "definitions",
        }:
            expanded = split_semicolon_items(tail)
            if len(expanded) <= 1 and "," in tail:
                expanded = [normalize_text(part) for part in tail.split(",") if normalize_text(part)]
            if expanded:
                return expanded
    return normalized_items


def extract_match_choices(stem: str, blocks: list[dict], raw_answer: str, raw_options: list[tuple[str, str]]) -> list[dict]:
    if raw_options:
        return [
            {"id": key.lower(), "key": key.upper(), "label": normalize_text(label)}
            for key, label in raw_options
            if normalize_text(key) and normalize_text(label)
        ]

    for block in blocks:
        if block.get("type") != "list_block":
            continue
        items = expand_embedded_list_items(block.get("items", []))
        if not items:
            continue
        label = normalize_text(block.get("label", "")).lower()
        original_first = normalize_text(block.get("items", [""])[0]) if block.get("items") else ""
        if label in {"terms", "measures"} or original_first.lower().startswith(("terms:", "measures:")):
            return [
                {"id": slugify(choice) or f"choice-{idx}", "key": None, "label": choice}
                for idx, choice in enumerate(items, start=1)
            ]

    texts = [
        str(block.get("text", ""))
        for block in blocks
        if block.get("type") == "text" and block.get("text")
    ] + [stem]

    for text in texts:
        stripped = text.strip()
        if not stripped.lower().startswith("terms:"):
            continue
        tail = stripped.split(":", 1)[1].strip()
        lettered = LETTERED_CHOICE_RE.findall(tail)
        if lettered:
            return [
                {"id": key.lower(), "key": key.upper(), "label": normalize_text(label)}
                for key, label in lettered
            ]

        pieces = split_semicolon_items(tail)
        if len(pieces) <= 1 and "," in tail:
            pieces = [normalize_text(part) for part in tail.split(",") if normalize_text(part)]
        if not pieces:
            continue

        coded_choices: list[dict] = []
        for piece in pieces:
            coded = CODED_CHOICE_RE.match(piece)
            if not coded:
                coded_choices = []
                break
            coded_choices.append(
                {
                    "id": coded.group(2).lower(),
                    "key": coded.group(2).upper(),
                    "label": normalize_text(coded.group(1)),
                }
            )
        if coded_choices:
            return coded_choices

        return [
            {"id": slugify(label) or f"choice-{idx}", "key": None, "label": label}
            for idx, label in enumerate(pieces, start=1)
        ]

    either_match = re.search(
        r"either\s+(.+?)\s*\(([A-Z])\)\s+or\s+(.+?)\s*\(([A-Z])\)",
        stem,
        flags=re.IGNORECASE,
    )
    if either_match:
        left_label = normalize_text(either_match.group(1))
        left_code = either_match.group(2).upper()
        right_label = normalize_text(either_match.group(3))
        right_code = either_match.group(4).upper()
        return [
            {"id": left_code.lower(), "key": left_code, "label": left_label},
            {"id": right_code.lower(), "key": right_code, "label": right_label},
        ]

    coded_mentions = re.findall(r"([A-Za-z][A-Za-z0-9 /'-]+?)\s*\(([A-Z])\)", stem)
    if len(coded_mentions) >= 2:
        return [
            {"id": code.lower(), "key": code.upper(), "label": normalize_text(label)}
            for label, code in coded_mentions
        ]

    answer_pairs = parse_arrow_pairs(raw_answer)
    if answer_pairs:
        labels: list[str] = []
        seen: set[str] = set()
        for _, right in answer_pairs:
            label = normalize_text(right)
            if not label or label.lower() in seen:
                continue
            seen.add(label.lower())
            labels.append(label)
        if labels and all(len(label) <= 80 for label in labels):
            return [
                {"id": slugify(label) or f"choice-{idx}", "key": None, "label": label}
                for idx, label in enumerate(labels, start=1)
            ]

    return []


def extract_numbered_statement_rows(stem: str) -> list[str]:
    matches = re.findall(
        r"(?:^|\s)(\d+)\.\s+(.+?)(?=(?:\s+\d+\.\s)|$)",
        normalize_text(stem),
    )
    if len(matches) < 2:
        return []
    return [normalize_text(label) for _, label in matches]


def extract_match_rows(stem: str, blocks: list[dict], raw_answer: str) -> list[str]:
    candidate_rows: list[tuple[int, list[str]]] = []
    for block in blocks:
        if block.get("type") != "list_block" or not block.get("items"):
            continue
        label = normalize_text(block.get("label", "")).lower()
        original_first = normalize_text(block.get("items", [""])[0]) if block.get("items") else ""
        if label == "terms" or original_first.lower().startswith("terms:"):
            continue
        rows = expand_embedded_list_items(block.get("items", []))
        if not rows:
            continue
        score = 1 if len(rows) > 1 else 0
        if label in {"definitions", "definition", "descriptions", "description", "statements", "statement", "examples", "example"}:
            score += 2
        candidate_rows.append((score, rows))
    if candidate_rows:
        candidate_rows.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
        return candidate_rows[0][1]

    numbered_rows = extract_numbered_statement_rows(stem)
    if numbered_rows:
        return numbered_rows

    answer_pairs = parse_arrow_pairs(raw_answer)
    if answer_pairs:
        return [left for left, _ in answer_pairs]

    for block in blocks:
        if block.get("type") != "text":
            continue
        pairs = parse_arrow_pairs(str(block.get("text", "")))
        if pairs and all(right == "?" for _, right in pairs):
            return [left for left, _ in pairs]

    return []


def resolve_row_id(value: str, row_records: list[dict], row_id_by_label: dict[str, str]) -> str | None:
    normalized = normalize_text(value)
    if normalized.isdigit():
        idx = int(normalized) - 1
        if 0 <= idx < len(row_records):
            return row_records[idx]["id"]
    return row_id_by_label.get(normalized.lower())


def resolve_choice_id(value: str, choice_id_by_key: dict[str, str], choice_id_by_label: dict[str, str]) -> str | None:
    normalized = normalize_text(value)
    if not normalized:
        return None
    return choice_id_by_key.get(normalized.upper()) or choice_id_by_label.get(normalized.lower())


def normalize_match_table_fields(stem: str, blocks: list[dict], raw_answer: str, raw_options: list[tuple[str, str]]) -> tuple[dict, dict, list[str], dict]:
    choices = extract_match_choices(stem, blocks, raw_answer, raw_options)
    rows = extract_match_rows(stem, blocks, raw_answer)
    answer_pairs = parse_arrow_pairs(raw_answer)

    if not choices or not rows or not answer_pairs:
        return {}, {"raw": normalize_text(raw_answer)}, [normalize_text(raw_answer)], {"mode": "needs_enrichment", "raw_answer": normalize_text(raw_answer)}

    row_records = [{"id": f"row{idx}", "label": row} for idx, row in enumerate(rows, start=1)]
    row_id_by_label = {normalize_text(row["label"]).lower(): row["id"] for row in row_records}
    choice_id_by_key = {choice["key"]: choice["id"] for choice in choices if choice.get("key")}
    choice_id_by_label = {normalize_text(choice["label"]).lower(): choice["id"] for choice in choices}
    choice_label_by_id = {choice["id"]: choice["label"] for choice in choices}

    normalized_pairs: list[dict] = []
    markscheme_points: list[str] = []

    for left, right in answer_pairs:
        row_id = resolve_row_id(left, row_records, row_id_by_label)
        choice_id = resolve_choice_id(right, choice_id_by_key, choice_id_by_label)

        if row_id is None or choice_id is None:
            inverse_choice_id = resolve_choice_id(left, choice_id_by_key, choice_id_by_label)
            inverse_row_id = resolve_row_id(right, row_records, row_id_by_label)
            if inverse_row_id is not None and inverse_choice_id is not None:
                row_id = inverse_row_id
                choice_id = inverse_choice_id

        if row_id is None or choice_id is None:
            return {}, {"raw": normalize_text(raw_answer)}, [normalize_text(raw_answer)], {"mode": "needs_enrichment", "raw_answer": normalize_text(raw_answer)}

        normalized_pairs.append({"row_id": row_id, "choice_id": choice_id})
        row_label = next(row["label"] for row in row_records if row["id"] == row_id)
        markscheme_points.append(f"{row_label} -> {choice_label_by_id[choice_id]}")

    options_json = {"rows": row_records, "choices": choices}
    correct_answer_json = {"raw": normalize_text(raw_answer), "pairs": normalized_pairs}
    autograde_rules_json = {"mode": "structured_match", "pairs": normalized_pairs}
    return options_json, correct_answer_json, markscheme_points, autograde_rules_json


def parse_drag_drop_prompt_items(stem: str) -> list[str]:
    normalized = normalize_text(stem).rstrip(".")
    if ":" not in normalized:
        return []

    tail = normalized.rsplit(":", 1)[1]
    items = [normalize_text(part) for part in tail.split(",") if normalize_text(part)]
    if len(items) < 3:
        return []

    return items


def normalize_drag_drop_fields(stem: str, raw_answer: str) -> tuple[dict, dict, list[str], dict]:
    prompt_items = parse_drag_drop_prompt_items(stem)
    answer_items = split_semicolon_items(raw_answer)

    if len(prompt_items) < 3 or len(answer_items) != len(prompt_items):
        answer_text = normalize_text(raw_answer)
        return {}, {"raw": answer_text}, [answer_text], {"mode": "needs_enrichment", "raw_answer": answer_text}

    prompt_counts = Counter(item.lower() for item in prompt_items)
    answer_counts = Counter(item.lower() for item in answer_items)
    if prompt_counts != answer_counts:
        answer_text = normalize_text(raw_answer)
        return {}, {"raw": answer_text}, [answer_text], {"mode": "needs_enrichment", "raw_answer": answer_text}

    options_json = {"items": prompt_items}
    correct_answer_json = {"raw": normalize_text(raw_answer), "order": answer_items}
    autograde_rules_json = {"mode": "ordering", "order": answer_items}
    return options_json, correct_answer_json, answer_items, autograde_rules_json


def sentence_join(parts: list[str]) -> str:
    sentences: list[str] = []
    for part in parts:
        cleaned = normalize_text(part)
        if not cleaned:
            continue
        if cleaned[-1] not in ".!?":
            cleaned += "."
        sentences.append(cleaned)
    return " ".join(sentences)


def objective_explanation(objective_codes: list[str]) -> str:
    if not objective_codes:
        return ""
    descriptions = [
        objective.description
        for code in objective_codes[:2]
        if (objective := OBJECTIVES_BY_CODE.get(code)) is not None
    ]
    if not descriptions:
        return ""
    if len(descriptions) == 1:
        return descriptions[0]
    return f"{descriptions[0]} It also checks whether you can {descriptions[1][0].lower()}{descriptions[1][1:]}"


def resolve_mcq_answer_text(options_json: list[dict] | dict, correct_answer_json: dict) -> str:
    raw = normalize_text(correct_answer_json.get("raw", ""))
    if isinstance(options_json, list):
        for option in options_json:
            key = normalize_text(option.get("key", "")).upper()
            text = normalize_text(option.get("text", ""))
            if raw.upper() == key or raw.lower() == text.lower():
                return text or raw
    return raw


def answer_preview(question_format: str, options_json: list[dict] | dict, correct_answer_json: dict, markscheme_points: list[str]) -> str:
    if question_format == "mcq":
        answer_text = resolve_mcq_answer_text(options_json, correct_answer_json)
        return f"The correct option is {answer_text}" if answer_text else ""

    if question_format == "true_false":
        raw = normalize_text(correct_answer_json.get("raw", ""))
        return f"The statement is {raw.lower()}" if raw else ""

    if question_format == "match_table":
        points = [normalize_text(point) for point in markscheme_points if normalize_text(point)]
        if points:
            return "The correct matches are: " + "; ".join(points)
        return ""

    if question_format == "drag_drop":
        order = correct_answer_json.get("order", [])
        if isinstance(order, list) and order:
            return "The correct order is: " + " -> ".join(normalize_text(item) for item in order)
        return ""

    accepted_texts = correct_answer_json.get("accepted_texts")
    if isinstance(accepted_texts, list) and accepted_texts:
        return "An accepted answer is " + normalize_text(str(accepted_texts[0]))

    raw = normalize_text(correct_answer_json.get("raw", ""))
    if raw:
        return "An accepted answer is " + raw

    points = [normalize_text(point) for point in markscheme_points if normalize_text(point)]
    if points:
        return "An accepted answer is " + points[0]

    return ""


def build_teaching_explanation(question_format: str, options_json: list[dict] | dict, correct_answer_json: dict, markscheme_points: list[str], objective_codes: list[str]) -> str:
    preview = answer_preview(question_format, options_json, correct_answer_json, markscheme_points)
    objective_text = objective_explanation(objective_codes)
    if objective_text:
        objective_text = "This question checks whether you can " + objective_text[0].lower() + objective_text[1:]
    return sentence_join([preview, objective_text])


def parse_figure_caption_map(build_script_path: Path) -> dict[str, str]:
    module = ast.parse(build_script_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "FIGURE_TO_IMAGE":
                    return ast.literal_eval(node.value)
    raise RuntimeError("Could not locate FIGURE_TO_IMAGE in build_automark_docx.py")


def parse_topics_from_markdown(path: Path) -> Iterable[tuple[int, str, str, list[str]]]:
    text = path.read_text(encoding="utf-8")
    matches = list(TOPIC_HEADING_RE.finditer(text))
    for idx, match in enumerate(matches):
        topic_num = int(match.group(1))
        topic_title = f"Topic {topic_num}: {match.group(2).strip()}"
        body_start = match.end()
        body_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[body_start:body_end]

        chunks = [chunk.strip() for chunk in re.split(r"^---\s*$", body, flags=re.MULTILINE) if chunk.strip()]
        sources_line = ""
        question_chunks: list[str] = []
        for chunk in chunks:
            if chunk.startswith("Sources:"):
                sources_line = chunk.splitlines()[0].strip()
            elif chunk.startswith("### Q"):
                question_chunks.append(chunk)

        yield topic_num, topic_title, sources_line, question_chunks


def parse_question_chunk(chunk: str) -> ParsedQuestion | None:
    lines = chunk.splitlines()
    if not lines:
        return None

    head = lines[0]
    match = QUESTION_HEADING_RE.match(head)
    if not match:
        return None

    question_label = match.group(1).strip()
    marks_text = match.group(2).strip()
    qtype = match.group(3).strip()
    rest = lines[1:]

    answer = ""
    answer_index = None
    for idx, line in enumerate(rest):
        if line.lstrip().startswith("**Answer:**"):
            answer_index = idx
            answer = line.split("**Answer:**", 1)[1].strip()
            break

    body = rest[:answer_index] if answer_index is not None else rest
    while body and not body[-1].strip():
        body.pop()

    option_re = re.compile(r"^([A-D])\.\s+(.*)$")
    block_label_re = re.compile(r"^([A-Z][A-Za-z /]*?):\s*$")

    source_line = ""
    body_segments: list[tuple[str, object]] = []
    options: list[tuple[str, str]] = []
    paragraph_buffer: list[str] = []
    idx = 0

    def flush_paragraph() -> None:
        nonlocal paragraph_buffer
        if paragraph_buffer:
            text = "\n".join(paragraph_buffer).strip()
            if text:
                body_segments.append(("text", text))
            paragraph_buffer = []

    while idx < len(body):
        stripped = body[idx].strip()

        if not stripped:
            flush_paragraph()
            idx += 1
            continue

        source_match = SOURCE_LINE_RE.match(stripped)
        if source_match:
            flush_paragraph()
            source_line = source_match.group(1).strip()
            idx += 1
            continue

        figure_match = FIGURE_MARKER_RE.match(stripped)
        if figure_match:
            flush_paragraph()
            body_segments.append(("figure", figure_match.group(1).strip()))
            idx += 1
            continue

        block_match = block_label_re.match(stripped)
        if block_match:
            flush_paragraph()
            label = block_match.group(1).strip()
            idx += 1
            items: list[str] = []
            while idx < len(body):
                block_line = body[idx].strip()
                if not block_line:
                    idx += 1
                    continue
                if block_label_re.match(block_line) or option_re.match(block_line):
                    break
                numbered = re.match(r"^\d+\.\s+(.*)$", block_line)
                bulleted = re.match(r"^[-*]\s+(.*)$", block_line)
                if numbered:
                    items.append(numbered.group(1).strip())
                elif bulleted:
                    items.append(bulleted.group(1).strip())
                else:
                    if items:
                        items[-1] = f"{items[-1]} {block_line}"
                    else:
                        items.append(block_line)
                idx += 1
            body_segments.append(("block", {"label": label, "items": items}))
            continue

        if option_re.match(stripped):
            flush_paragraph()
            while idx < len(body):
                option_line = body[idx].strip()
                option_match = option_re.match(option_line)
                if not option_match:
                    if not option_line:
                        idx += 1
                        continue
                    break
                options.append((option_match.group(1), option_match.group(2).strip()))
                idx += 1
            continue

        paragraph_buffer.append(body[idx])
        idx += 1

    flush_paragraph()

    return ParsedQuestion(
        question_label=question_label,
        marks_text=marks_text,
        qtype=qtype,
        source_line=source_line,
        body_segments=body_segments,
        options=options,
        answer=answer,
    )


def infer_format(qtype: str, stem: str, blocks: list[dict], raw_answer: str, has_options: bool) -> str:
    q = qtype.lower()
    s = stem.lower()
    answer = normalize_text(raw_answer).lower()
    if parse_shared_gap_answer(stem, raw_answer):
        return "fill_gap"
    if "multiple choice" in q:
        return "mcq"
    if "true / false" in q or "true/false" in q:
        if parse_arrow_pairs(raw_answer):
            return "match_table"
        return "true_false"
    true_false_stem_signals = (
        "true or false",
        "state whether",
        "select whether",
        "decide whether",
        "tick true or false",
    )
    if any(signal in s for signal in true_false_stem_signals):
        if parse_arrow_pairs(raw_answer):
            return "match_table"
        return "true_false"
    if answer in {"true", "false"} and not has_options and not blocks:
        return "true_false"
    if "match" in q:
        return "match_table"
    if "fill in the blank" in q or "fill the gap" in s:
        return "fill_gap"
    if any(signal in s for signal in ORDERING_STEM_SIGNALS):
        return "drag_drop"
    if "short answer" in q or "short factual" in q or "define" in q:
        return "short_text"
    if any(block["label"].lower() in {"terms", "pairs", "definitions", "statements"} for block in blocks):
        return "match_table"
    return "structured_response"


def infer_difficulty(
    source_set: str,
    question_format: str,
    marks: int,
    has_figure: bool,
    source_locator: str = "",
    stem: str = "",
) -> str:
    source_locator_lower = source_locator.lower()
    stem_lower = normalize_text(stem).lower()
    recall_stem = stem_lower.startswith((
        "state one",
        "state another",
        "name one",
        "name two",
        "what do the letters",
        "what does the acronym",
    ))

    if source_set == "practice_bank":
        if marks >= 3:
            return "expert"
        if question_format == "mcq" and marks == 1 and not has_figure:
            return "easy"
        if question_format in {"match_table", "drag_drop"} or has_figure:
            return "medium"
        return "easy"

    high_mark_source = any(
        signal in source_locator_lower
        for signal in (
            "6-mark qwc",
            "4-mark qwc",
            "originally 4-mark",
            "originally 3-mark",
            "3-mark describe",
        )
    )
    if high_mark_source and not recall_stem:
        return "expert"

    if marks >= 2 and question_format in {"match_table", "fill_gap", "drag_drop"}:
        return "expert"

    if marks >= 3 or question_format in {"structured_response", "drag_drop"}:
        return "expert"
    if has_figure or question_format in {"match_table", "short_text"}:
        return "medium"
    return "medium"


def infer_adaptive_tier(source_set: str, difficulty: str, has_figure: bool) -> str:
    if source_set == "practice_bank" and difficulty == "easy" and not has_figure:
        return "support"
    if difficulty == "expert":
        return "challenge"
    return "core"


def infer_asset_kind(caption: str) -> str:
    value = caption.lower()
    if "screenshot" in value:
        return "screenshot"
    if "chart" in value or "graph" in value:
        return "chart"
    if "table" in value or "spreadsheet" in value or "form" in value:
        return "table_image"
    if "diagram" in value:
        return "diagram"
    return "figure"


def infer_interaction_key(question_format: str, stem: str) -> str:
    stem_lower = stem.lower()
    if question_format == "drag_drop":
        return "sequence"
    if question_format == "match_table":
        return "match"
    if question_format == "fill_gap":
        return "complete"
    if "which" in stem_lower or question_format == "mcq":
        return "choose"
    if "state" in stem_lower or "name" in stem_lower or "what is" in stem_lower:
        return "identify"
    if "describe" in stem_lower or "explain" in stem_lower:
        return "apply"
    return "identify"


def infer_concept_key(topic_slug: str, stem: str, answer: str, tags: list[str]) -> str:
    haystack = " ".join([stem.lower(), answer.lower(), " ".join(tags)])
    for concept_key, terms in TOPIC_CONCEPT_RULES.get(topic_slug, []):
        if any(term in haystack for term in terms):
            return concept_key

    words = [
        word for word in re.findall(r"[a-z0-9]+", haystack)
        if word not in STOPWORDS and len(word) > 2
    ]
    if not words:
        return "general"
    return "-".join(words[:3])


def build_family_code(topic_slug: str, question_format: str, stem: str, answer: str, tags: list[str]) -> str:
    concept_key = infer_concept_key(topic_slug, stem, answer, tags)
    interaction_key = infer_interaction_key(question_format, stem)
    return f"{topic_slug}.{concept_key}.{interaction_key}"


def default_selection_weight(source_set: str, question_format: str, has_figure: bool) -> float:
    weight = 1.0
    if source_set == "practice_bank" and question_format == "mcq":
        weight = 1.0
    if source_set in {"past_paper", "mark_scheme"} and has_figure:
        weight = 1.05
    return weight


def normalize_source_set(source_set: str, source_locator: str) -> str:
    locator = source_locator.lower()
    if source_set == "past_paper" and "supplementary item derived from" in locator:
        return "mark_scheme"
    return source_set


def source_title_for_set(source_set: str) -> str:
    if source_set == "past_paper":
        return "Past paper auto-markable pack"
    if source_set == "mark_scheme":
        return "Supplementary mark scheme review pack"
    return "Practice question pack"


def build_dedupe_fingerprint(topic_slug: str, question_format: str, stem: str, answer: str) -> str:
    normalized = " | ".join([
        topic_slug,
        question_format,
        normalize_text(stem).lower(),
        normalize_text(answer).lower(),
    ])
    return stable_hash(normalized, length=16)


def split_accept_terms(text: str) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []

    if " / " in normalized:
        return [part.strip() for part in normalized.split(" / ") if part.strip()]
    if ";" in normalized:
        return [part.strip() for part in normalized.split(";") if part.strip()]
    if "," in normalized:
        return [part.strip() for part in normalized.split(",") if part.strip()]
    if re.search(r"\bor\b", normalized, flags=re.IGNORECASE):
        return [part.strip() for part in re.split(r"\bor\b", normalized, flags=re.IGNORECASE) if part.strip()]
    return [normalized]


def parse_any_n_from_answer(text: str) -> tuple[int, list[str]] | None:
    normalized = normalize_text(text)
    if not normalized:
        return None

    match = ANY_N_FROM_RE.match(normalized)
    if not match:
        return None

    if match.group(1):
        required_count = int(match.group(1))
    else:
        required_count = {"two": 2, "three": 3, "four": 4}.get((match.group(2) or "").lower(), 0)

    accepted_texts = split_semicolon_items(match.group(3).rstrip("."))
    if required_count < 2 or len(accepted_texts) < required_count:
        return None

    return required_count, accepted_texts


def infer_required_count_from_stem(stem: str) -> int | None:
    match = re.search(r"\b(?:state|list|name|identify)\s+((?:\d+)|(?:two|three|four))\b", stem, flags=re.IGNORECASE)
    if not match:
        return None
    token = match.group(1).lower()
    if token.isdigit():
        return int(token)
    return {"two": 2, "three": 3, "four": 4}.get(token)


def parse_shared_gap_answer(stem: str, text: str) -> tuple[int, list[str]] | None:
    from_answer = parse_any_n_from_answer(text)
    if from_answer:
        return from_answer

    normalized = normalize_text(text)
    if not normalized:
        return None

    suffix_match = ANY_N_SUFFIX_RE.match(normalized)
    if suffix_match:
        prefix = normalize_text(suffix_match.group(1))
        count_token = suffix_match.group(2).lower()
        required_count = int(count_token) if count_token.isdigit() else {"two": 2, "three": 3}.get(count_token, 0)
        accepted_texts = split_semicolon_items(prefix)
        if required_count >= 2 and len(accepted_texts) >= required_count:
            return required_count, accepted_texts

    required_count = infer_required_count_from_stem(stem)
    accepted_texts = split_semicolon_items(normalized)
    if required_count and len(accepted_texts) == required_count:
        return required_count, accepted_texts

    return None


def parse_parenthetical_or_answer(text: str) -> list[str] | None:
    normalized = normalize_text(text)
    if not normalized:
        return None
    match = PARENTHETICAL_OR_RE.match(normalized)
    if not match:
        return None
    primary = normalize_text(match.group(1))
    alternate = normalize_text(match.group(2))
    if not primary or not alternate:
        return None
    if ";" in primary or ";" in alternate:
        return None
    return [primary, alternate]


def parse_ordered_gap_answers(text: str) -> list[str] | None:
    items = split_semicolon_items(text)
    if len(items) < 2:
        return None
    if any(not item for item in items):
        return None
    return items


def parse_stem_aligned_gap_answers(stem: str, text: str) -> list[str] | None:
    blank_matches = list(BLANK_RE.finditer(stem))
    if len(blank_matches) < 2:
        return None

    normalized_answer = normalize_text(text)
    if not normalized_answer:
        return None

    region = normalize_text(stem[blank_matches[0].start():blank_matches[-1].end()])
    if not region:
        return None

    pattern_parts: list[str] = []
    cursor = 0
    for match in BLANK_RE.finditer(region):
        static_text = region[cursor:match.start()]
        if static_text:
            pattern_parts.append(re.escape(static_text).replace(r"\ ", r"\s+"))
        pattern_parts.append(r"(.+?)")
        cursor = match.end()
    trailing = region[cursor:]
    if trailing:
        pattern_parts.append(re.escape(trailing).replace(r"\ ", r"\s+"))

    pattern = "^" + "".join(pattern_parts) + "$"
    matched = re.match(pattern, normalized_answer, flags=re.IGNORECASE)
    if not matched:
        return None

    parts = [normalize_text(group) for group in matched.groups()]
    if any(
        not part
        or ";" in part
        or "," in part
        or " / " in part
        or re.search(r"\bor\b", part, flags=re.IGNORECASE)
        for part in parts
    ):
        return None

    return parts


def build_grouped_acceptance(items: list[str]) -> list[dict]:
    groups: list[dict] = []
    for item in items:
        normalized = normalize_text(item)
        if not normalized:
            continue

        match = re.match(r"^(.*?)\s*\((.*?)\)\s*$", normalized)
        if not match:
            groups.append({"canonical": normalized, "accepted_texts": [normalized]})
            continue

        primary = normalize_text(match.group(1))
        detail = normalize_text(match.group(2))
        accepted = [normalized]
        if primary:
            accepted.append(primary)

        detail_word_count = len(detail.split())
        if detail and ";" not in detail and "," not in detail and detail_word_count <= 4:
            accepted.append(detail)

        deduped: list[str] = []
        for candidate in accepted:
            if candidate and candidate not in deduped:
                deduped.append(candidate)

        groups.append({"canonical": primary or normalized, "accepted_texts": deduped})

    return groups


def normalize_answer_fields(question_external_id: str, question_format: str, stem: str, raw_answer: str) -> tuple[dict, list[str], dict]:
    answer_text = normalize_text(raw_answer)
    correct_answer_json: dict = {"raw": answer_text}
    markscheme_points = [part.strip() for part in answer_text.split(";") if part.strip()]
    autograde_rules_json: dict = {"mode": "needs_enrichment", "raw_answer": answer_text}

    if question_format == "fill_gap":
        shared_gap = parse_shared_gap_answer(stem, answer_text)
        if shared_gap:
            required_count, accepted_texts = shared_gap
            accepted_groups = build_grouped_acceptance(accepted_texts)
            gaps = [
                {
                    "id": f"gap{idx}",
                    "accepted_texts": accepted_texts,
                    "accepted_groups": accepted_groups,
                }
                for idx in range(1, required_count + 1)
            ]
            correct_answer_json = {
                "raw": answer_text,
                "gaps": gaps,
                "required_count": required_count,
                "require_distinct": True,
            }
            markscheme_points = accepted_texts
            autograde_rules_json = {
                "mode": "shared_gap_pool",
                "accepted_texts": accepted_texts,
                "accepted_groups": accepted_groups,
                "required_count": required_count,
                "require_distinct": True,
            }
            return correct_answer_json, markscheme_points, autograde_rules_json

        parenthetical_or = parse_parenthetical_or_answer(answer_text)
        if parenthetical_or:
            correct_answer_json = {
                "raw": parenthetical_or[0],
                "gaps": [{"id": "gap1", "accepted_texts": parenthetical_or}],
                "required_count": 1,
                "require_distinct": False,
            }
            markscheme_points = [parenthetical_or[0]]
            autograde_rules_json = {
                "mode": "accepted_texts",
                "accepted_texts": parenthetical_or,
                "requires_review": True,
            }
            return correct_answer_json, markscheme_points, autograde_rules_json

        ordered_gap_answers = parse_ordered_gap_answers(answer_text)
        if ordered_gap_answers:
            correct_answer_json = {
                "raw": answer_text,
                "gaps": [
                    {
                        "id": f"gap{idx}",
                        "accepted_texts": [accepted_text],
                        "accepted_groups": build_grouped_acceptance([accepted_text]),
                    }
                    for idx, accepted_text in enumerate(ordered_gap_answers, start=1)
                ],
                "required_count": len(ordered_gap_answers),
                "require_distinct": False,
            }
            markscheme_points = ordered_gap_answers
            autograde_rules_json = {
                "mode": "ordered_gaps",
                "gaps": [
                    {
                        "id": f"gap{idx}",
                        "accepted_texts": [accepted_text],
                        "accepted_groups": build_grouped_acceptance([accepted_text]),
                    }
                    for idx, accepted_text in enumerate(ordered_gap_answers, start=1)
                ],
                "required_count": len(ordered_gap_answers),
                "require_distinct": False,
            }
            return correct_answer_json, markscheme_points, autograde_rules_json

        stem_aligned_gap_answers = parse_stem_aligned_gap_answers(stem, answer_text)
        if stem_aligned_gap_answers:
            correct_answer_json = {
                "raw": answer_text,
                "gaps": [
                    {
                        "id": f"gap{idx}",
                        "accepted_texts": [accepted_text],
                        "accepted_groups": build_grouped_acceptance([accepted_text]),
                    }
                    for idx, accepted_text in enumerate(stem_aligned_gap_answers, start=1)
                ],
                "required_count": len(stem_aligned_gap_answers),
                "require_distinct": False,
            }
            markscheme_points = stem_aligned_gap_answers
            autograde_rules_json = {
                "mode": "ordered_gaps",
                "gaps": [
                    {
                        "id": f"gap{idx}",
                        "accepted_texts": [accepted_text],
                        "accepted_groups": build_grouped_acceptance([accepted_text]),
                    }
                    for idx, accepted_text in enumerate(stem_aligned_gap_answers, start=1)
                ],
                "required_count": len(stem_aligned_gap_answers),
                "require_distinct": False,
            }
            return correct_answer_json, markscheme_points, autograde_rules_json

    accept_match = re.match(r"^(.*?)\s*\(accept:\s*(.*?)\)\s*$", answer_text, flags=re.IGNORECASE)
    if not accept_match:
        accept_match = re.match(r"^(.*?)\s*\((?:also accept)\s+(.*?)\)\s*$", answer_text, flags=re.IGNORECASE)
    if accept_match:
        primary = normalize_text(accept_match.group(1))
        accept_text = normalize_text(accept_match.group(2))
        accepted_texts = ACCEPTED_ANSWER_OVERRIDES.get(question_external_id)
        if not accepted_texts:
            accepted_texts = [primary]
            for candidate in split_accept_terms(accept_text):
                if candidate and candidate not in accepted_texts:
                    accepted_texts.append(candidate)

        correct_answer_json = {
            "raw": primary,
            "accepted_texts": accepted_texts,
            "accept_note": accept_text,
        }
        markscheme_points = [primary]
        autograde_rules_json = {
            "mode": "accepted_texts",
            "accepted_texts": accepted_texts,
            "requires_review": True,
        }
    else:
        direct_overrides = ACCEPTED_ANSWER_OVERRIDES.get(question_external_id)
        if direct_overrides:
            correct_answer_json = {
                "raw": direct_overrides[0],
                "accepted_texts": direct_overrides,
            }
            markscheme_points = [direct_overrides[0]]
            autograde_rules_json = {
                "mode": "accepted_texts",
                "accepted_texts": direct_overrides,
                "requires_review": True,
            }
            return correct_answer_json, markscheme_points, autograde_rules_json

        if question_format == "short_text" and " / " in answer_text:
            slash_alternatives = [normalize_text(part) for part in answer_text.split(" / ") if normalize_text(part)]
            if len(slash_alternatives) > 1 and all(len(part.split()) <= 4 for part in slash_alternatives):
                correct_answer_json = {
                    "raw": slash_alternatives[0],
                    "accepted_texts": slash_alternatives,
                }
                markscheme_points = [slash_alternatives[0]]
                autograde_rules_json = {
                    "mode": "accepted_texts",
                    "accepted_texts": slash_alternatives,
                    "requires_review": True,
                }
                return correct_answer_json, markscheme_points, autograde_rules_json

        grouped_single = build_grouped_acceptance([answer_text])
        if grouped_single and len(grouped_single) == 1 and len(grouped_single[0].get("accepted_texts", [])) > 1:
            accepted_texts = grouped_single[0]["accepted_texts"]
            correct_answer_json = {
                "raw": grouped_single[0]["canonical"],
                "accepted_texts": accepted_texts,
            }
            markscheme_points = [grouped_single[0]["canonical"]]
            autograde_rules_json = {
                "mode": "accepted_texts",
                "accepted_texts": accepted_texts,
                "requires_review": True,
            }

    return correct_answer_json, markscheme_points, autograde_rules_json


def extract_stem_and_blocks(parsed: ParsedQuestion) -> tuple[str, list[dict]]:
    text_parts: list[str] = []
    blocks: list[dict] = []
    figure_count = 0
    block_count = 0

    for kind, payload in parsed.body_segments:
        if kind == "text":
            text = normalize_text(str(payload))
            text_parts.append(text)
            blocks.append({"type": "text", "text": text})
        elif kind == "figure":
            figure_count += 1
            blocks.append({
                "type": "figure",
                "caption": str(payload),
                "block_key": f"figure_{figure_count}",
            })
        elif kind == "block":
            block_count += 1
            block_payload = dict(payload)
            label_text = normalize_text(block_payload["label"])
            items = block_payload["items"]

            # Some question prompts end with a colon and were parsed as a block
            # label with no real items. Treat those as stem text instead of
            # surfacing them later as false "missing stem" cases.
            if not items:
                text_parts.append(label_text)
                blocks.append({"type": "text", "text": label_text})
                continue

            # If the first block label is not one of the structural labels used
            # for matching/statement groups, treat the label itself as prompt
            # text and still keep the item block.
            if not text_parts and label_text.lower() not in STRUCTURAL_BLOCK_LABELS:
                text_parts.append(label_text)
                blocks.append({"type": "text", "text": label_text})

            blocks.append({
                "type": "list_block",
                "label": label_text,
                "items": items,
                "block_key": f"block_{block_count}",
            })

    stem = "\n\n".join(part for part in text_parts if part)
    return stem, blocks


def parse_marks(text: str) -> int:
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 1


def build_source_bundle(source_root: Path) -> dict:
    automark_dir = source_root / "_automark" / "markdown"
    practice_dir = source_root / "_practice_questions"
    figure_script = source_root / "_automark" / "build_automark_docx.py"
    figure_dir = source_root / "_automark" / "figures"

    figure_caption_map = parse_figure_caption_map(figure_script)

    supplementary_dir = REPO_ROOT / "content" / "unit1_supplementary_questions"
    sources = [
        ("past_paper", sorted(automark_dir.glob("*.md"))),
        ("practice_bank", sorted(practice_dir.glob("*.md"))),
        ("practice_bank", sorted(supplementary_dir.glob("*.md"))),
    ]

    questions: list[dict] = []
    assets: list[dict] = []
    topic_counts: dict[str, dict[str, int]] = {}

    for source_set, paths in sources:
        for path in paths:
            for topic_num, topic_title, topic_sources_line, question_chunks in parse_topics_from_markdown(path):
                topic_slug = TOPIC_SLUG_BY_TITLE[topic_title]
                topic_counts.setdefault(
                    topic_slug,
                    {"past_paper": 0, "mark_scheme": 0, "practice_bank": 0},
                )

                for index, chunk in enumerate(question_chunks, start=1):
                    parsed = parse_question_chunk(chunk)
                    if parsed is None:
                        continue

                    stem, content_blocks = extract_stem_and_blocks(parsed)
                    block_segments = [block for block in content_blocks if block["type"] == "list_block"]
                    question_format = infer_format(
                        parsed.qtype,
                        stem,
                        block_segments,
                        parsed.answer,
                        has_options=bool(parsed.options),
                    )
                    source_locator = parsed.source_line or topic_sources_line or path.name
                    normalized_source_set = normalize_source_set(source_set, source_locator)
                    marks = parse_marks(parsed.marks_text)
                    has_figure = any(block["type"] == "figure" for block in content_blocks)
                    difficulty = infer_difficulty(
                        normalized_source_set,
                        question_format,
                        marks,
                        has_figure,
                        source_locator,
                        stem,
                    )
                    adaptive_tier = infer_adaptive_tier(normalized_source_set, difficulty, has_figure)

                    tags = [slugify(parsed.qtype)]
                    family_code = build_family_code(topic_slug, question_format, stem, parsed.answer, tags)
                    selection_weight = default_selection_weight(normalized_source_set, question_format, has_figure)
                    fingerprint = build_dedupe_fingerprint(topic_slug, question_format, stem, parsed.answer)

                    question_external_id = (
                        f"{topic_slug}.{normalized_source_set}.{path.stem}.q{index:03d}"
                    )
                    source_title = source_title_for_set(normalized_source_set)
                    objective_answer = parsed.answer
                    if parsed.options:
                        for key, value in parsed.options:
                            if normalize_text(parsed.answer).upper() == normalize_text(key).upper():
                                objective_answer = f"{parsed.answer} {value}"
                                break
                    objective_codes = infer_objective_codes(
                        topic_slug,
                        stem=stem,
                        answer=objective_answer,
                        source_locator=source_locator,
                        qtype_label=parsed.qtype,
                        tags=tags,
                        content_blocks=content_blocks,
                    )
                    correct_answer_json, markscheme_points, autograde_rules_json = normalize_answer_fields(
                        question_external_id,
                        question_format,
                        stem,
                        parsed.answer,
                    )
                    options_json: list[dict] | dict = [{"key": key, "text": value} for key, value in parsed.options]
                    if question_format == "match_table":
                        (
                            normalized_options_json,
                            normalized_correct_answer_json,
                            normalized_markscheme_points,
                            normalized_autograde_rules_json,
                        ) = normalize_match_table_fields(stem, content_blocks, parsed.answer, parsed.options)
                        if normalized_options_json:
                            options_json = normalized_options_json
                            correct_answer_json = normalized_correct_answer_json
                            markscheme_points = normalized_markscheme_points
                            autograde_rules_json = normalized_autograde_rules_json
                    elif question_format == "drag_drop":
                        (
                            normalized_options_json,
                            normalized_correct_answer_json,
                            normalized_markscheme_points,
                            normalized_autograde_rules_json,
                        ) = normalize_drag_drop_fields(stem, parsed.answer)
                        if normalized_options_json:
                            options_json = normalized_options_json
                            correct_answer_json = normalized_correct_answer_json
                            markscheme_points = normalized_markscheme_points
                            autograde_rules_json = normalized_autograde_rules_json

                    explanation = build_teaching_explanation(
                        question_format,
                        options_json,
                        correct_answer_json,
                        markscheme_points,
                        objective_codes,
                    )

                    question_record = {
                        "question_external_id": question_external_id,
                        "source_set": normalized_source_set,
                        "topic_number": topic_num,
                        "topic_title": topic_title.removeprefix("Topic " + str(topic_num) + ": ").strip(),
                        "topic_slug": topic_slug,
                        "source_file_name": path.name,
                        "source_title": source_title,
                        "source_locator": source_locator,
                        "question_label": parsed.question_label,
                        "marks_text": parsed.marks_text,
                        "difficulty": difficulty,
                        "format": question_format,
                        "adaptive_tier": adaptive_tier,
                        "qtype_label": parsed.qtype,
                        "stem": stem,
                        "options_json": options_json,
                        "correct_answer_json": correct_answer_json,
                        "markscheme_points_json": markscheme_points,
                        "explanation": explanation,
                        "max_marks": marks,
                        "content_blocks_json": content_blocks,
                        "response_schema_json": {"expected_format": question_format},
                        "autograde_rules_json": autograde_rules_json,
                        "objective_codes_json": objective_codes,
                        "tags_json": tags,
                        "question_family_code": family_code,
                        "selection_weight": selection_weight,
                        "dedupe_fingerprint": fingerprint,
                        "teacher_notes": "First-pass explanation generated from answer and mapped objective; review before approval.",
                        "staging_status": "draft",
                    }
                    questions.append(question_record)
                    topic_counts[topic_slug][normalized_source_set] += 1

                    for block in content_blocks:
                        if block["type"] != "figure":
                            continue
                        caption = block["caption"]
                        image_name = figure_caption_map.get(caption)
                        relative_storage_path = f"{topic_slug}/{image_name}" if image_name else None
                        assets.append({
                            "question_external_id": question_external_id,
                            "asset_external_id": f"{question_external_id}.{block['block_key']}",
                            "asset_kind": infer_asset_kind(caption),
                            "asset_role": "prompt",
                            "file_name": image_name,
                            "source_relative_path": str((figure_dir / image_name).relative_to(source_root)) if image_name else None,
                            "storage_path": relative_storage_path,
                            "mime_type": "image/png" if image_name else None,
                            "alt_text": caption,
                            "caption": caption,
                            "display_order": 1,
                            "block_key": block["block_key"],
                            "source_locator": source_locator,
                            "resolved": bool(image_name),
                        })

    summary = {
        "question_count": len(questions),
        "asset_count": len(assets),
        "topic_counts": topic_counts,
    }

    return {
        "batch_label": "unit1-curated-source-bundle",
        "source_root": str(source_root),
        "questions": questions,
        "question_assets": assets,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    bundle = build_source_bundle(args.source_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(bundle, indent=2 if args.pretty else None, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")
    print(json.dumps(bundle["summary"], indent=2))


if __name__ == "__main__":
    main()
