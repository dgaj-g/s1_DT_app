#!/usr/bin/env python3
"""Package question visual assets into the expected Supabase Storage layout.

The question payload stores assets as bucket/path pairs, for example:

  bucket: question-imports
  path: network-technologies/image42.png

This script copies the source image files into a local upload package that
matches that layout. It does not upload anything to Supabase.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "supabase" / "imports" / "unit1_stage4_staging_payload.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "supabase" / "imports" / "question_assets_upload"
DEFAULT_MANIFEST_CSV = REPO_ROOT / "docs" / "unit1-stage5-asset-upload-manifest.csv"
DEFAULT_MANIFEST_JSON = REPO_ROOT / "docs" / "unit1-stage5-asset-upload-manifest.json"

MANIFEST_COLUMNS = [
    "question_external_id",
    "asset_external_id",
    "bucket",
    "storage_path",
    "source_path",
    "packaged_path",
    "asset_kind",
    "caption",
    "status",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_cell(value: Any) -> str:
    return " ".join(str(value or "").split())


def source_root_from_payload(payload: dict[str, Any]) -> Path:
    metadata = payload.get("import_batch", {}).get("metadata_json", {})
    source_root = metadata.get("source_root") if isinstance(metadata, dict) else None
    if not source_root:
        raise ValueError("Could not find import_batch.metadata_json.source_root in staging payload")
    return Path(source_root)


def resolve_source_path(source_root: Path, asset: dict[str, Any]) -> Path | None:
    metadata = asset.get("metadata_json") if isinstance(asset.get("metadata_json"), dict) else {}
    relative_path = metadata.get("source_relative_path")
    if relative_path:
        candidate = source_root / str(relative_path)
        if candidate.exists():
            return candidate

    original = clean_cell(asset.get("original_file_name"))
    if original:
        matches = sorted((source_root / "_automark" / "figures").glob(original))
        if matches:
            return matches[0]

    return None


def package_assets(payload: dict[str, Any], output_dir: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    source_root = source_root_from_payload(payload)
    rows: list[dict[str, str]] = []
    status_counts: Counter[str] = Counter()
    bucket_counts: Counter[str] = Counter()

    seen_storage_paths: set[tuple[str, str]] = set()
    for asset in payload.get("staged_question_assets", []):
        bucket = clean_cell(asset.get("storage_bucket")) or "question-imports"
        storage_path = clean_cell(asset.get("storage_path"))
        source_path = resolve_source_path(source_root, asset)
        packaged_path = output_dir / bucket / storage_path
        status = "packaged"

        if not storage_path:
            status = "missing_storage_path"
        elif source_path is None:
            status = "missing_source_file"
        elif (bucket, storage_path) not in seen_storage_paths:
            packaged_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, packaged_path)
            seen_storage_paths.add((bucket, storage_path))

        status_counts[status] += 1
        bucket_counts[bucket] += 1
        rows.append(
            {
                "question_external_id": clean_cell(asset.get("question_external_id")),
                "asset_external_id": clean_cell(asset.get("asset_external_id")),
                "bucket": bucket,
                "storage_path": storage_path,
                "source_path": str(source_path) if source_path else "",
                "packaged_path": str(packaged_path) if storage_path else "",
                "asset_kind": clean_cell(asset.get("asset_kind")),
                "caption": clean_cell(asset.get("caption")),
                "status": status,
            }
        )

    summary = {
        "source_root": str(source_root),
        "output_dir": str(output_dir),
        "asset_reference_count": len(rows),
        "unique_storage_file_count": len(seen_storage_paths),
        "status_counts": dict(status_counts),
        "bucket_counts": dict(bucket_counts),
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest-csv", type=Path, default=DEFAULT_MANIFEST_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--fail-on-missing", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_json(args.input)
    rows, summary = package_assets(payload, args.output_dir)

    write_csv(args.manifest_csv, rows)
    args.manifest_json.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_json.write_text(
        json.dumps(
            {
                "source_payload": str(args.input),
                "manifest_csv": str(args.manifest_csv),
                "summary": summary,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote asset upload manifest to {args.manifest_csv}")
    print(json.dumps(summary, indent=2))

    missing_count = sum(
        count for status, count in summary["status_counts"].items() if status.startswith("missing_")
    )
    if args.fail_on_missing and missing_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
