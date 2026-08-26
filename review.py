"""Validate SBA 928 data splits before any model training begins."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from market_data import SPLIT_DIR, read_jsonl


RATE_PATTERN = re.compile(r"(?<!\d)(\d{1,2}\.\d)%")
REQUIRED_FIELDS = {"id", "record_type", "instruction", "context", "target"}


def validate_record(record: dict[str, Any], path: Path, line_number: int) -> list[str]:
    errors = []
    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        errors.append(f"{path}:{line_number}: missing {sorted(missing)}")
        return errors
    for field in ("id", "instruction", "context", "target"):
        if not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"{path}:{line_number}: {field} must be a non-empty string")
    for rate in RATE_PATTERN.findall(record["target"]):
        if float(rate) > 100:
            errors.append(f"{path}:{line_number}: invalid percentage {rate}%")
    if "duration" in record["context"].lower():
        errors.append(f"{path}:{line_number}: duration leakage found in context")
    return errors


def review(split_dir: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    seen: dict[str, Path] = {}
    counts: dict[str, int] = {}
    for filename in ("train.jsonl", "validation.jsonl", "eval_holdout.jsonl"):
        path = split_dir / filename
        records = read_jsonl(path)
        counts[filename] = len(records)
        for line_number, record in enumerate(records, start=1):
            errors.extend(validate_record(record, path, line_number))
            record_id = record.get("id")
            if record_id in seen:
                errors.append(f"{path}:{line_number}: duplicate id also found in {seen[record_id]}")
            elif isinstance(record_id, str):
                seen[record_id] = path

    expected = {"train.jsonl": 149, "validation.jsonl": 32, "eval_holdout.jsonl": 33}
    if counts != expected:
        errors.append(f"Split counts are {counts}; expected {expected}")
    return errors, counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split-dir", type=Path, default=SPLIT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    errors, counts = review(args.split_dir)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {sum(counts.values())} unique records: {counts}")


if __name__ == "__main__":
    main()
