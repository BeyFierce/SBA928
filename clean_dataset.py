"""Create the cleaned SBA 928 dataset from the official UCI CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from market_data import CLEAN_CSV, RAW_CSV, age_group, read_semicolon_csv


def clean(source: Path, destination: Path) -> tuple[int, int]:
    """Remove leakage, add audit columns, and write a conventional CSV."""
    rows = read_semicolon_csv(source)
    if not rows:
        raise ValueError(f"No records found in {source}")

    source_fields = list(rows[0])
    if "duration" not in source_fields:
        raise ValueError("Expected the source-only duration column")

    fields = ["source_row"] + [name for name in source_fields if name != "duration"]
    fields += ["age_group", "converted"]
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for source_row, raw in enumerate(rows):
            cleaned = {key: value.strip() for key, value in raw.items() if key != "duration"}
            cleaned["source_row"] = source_row
            cleaned["age_group"] = age_group(int(raw["age"]))
            cleaned["converted"] = int(raw["y"] == "yes")
            writer.writerow(cleaned)

    return len(rows), len(fields)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=RAW_CSV)
    parser.add_argument("--output", type=Path, default=CLEAN_CSV)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    row_count, column_count = clean(args.source, args.output)
    print(f"Wrote {row_count:,} rows x {column_count} columns to {args.output}")


if __name__ == "__main__":
    main()
