"""Generate descriptive statistics for the UCI Bank Marketing dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

from market_data import CLEAN_CSV, OUTPUT_DIR, conversion_rate, grouped_rates, read_clean_csv


def render_table(title: str, rates: dict[str, dict[str, float]]) -> list[str]:
    lines = [title, "segment\trows\tconversions\trate"]
    for segment, values in sorted(rates.items(), key=lambda item: item[1]["rate"], reverse=True):
        lines.append(
            f"{segment}\t{int(values['count'])}\t{int(values['conversions'])}\t"
            f"{values['rate'] * 100:.2f}%"
        )
    return lines


def build_report(rows: list[dict[str, str]]) -> str:
    output = [
        "SBA 928 DATASET STATISTICS",
        "==========================",
        f"Rows: {len(rows):,}",
        f"Overall conversion rate: {conversion_rate(rows) * 100:.2f}%",
        "Leakage control: duration is absent from the cleaned dataset",
        "Source period: May 2008 through November 2010",
        "",
    ]
    for title, field in (
        ("Conversion by occupation", "job"),
        ("Conversion by education", "education"),
        ("Conversion by marital status", "marital"),
        ("Conversion by age cohort", "age_group"),
        ("Conversion by month", "month"),
        ("Conversion by prior outcome", "poutcome"),
    ):
        output.extend(render_table(title, grouped_rates(rows, field)))
        output.append("")

    output.append("Macroeconomic indicator ranges")
    for field in ("emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"):
        values = [float(row[field]) for row in rows]
        output.append(f"{field}\tmin={min(values):.3f}\tmax={max(values):.3f}")
    return "\n".join(output) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=CLEAN_CSV)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "stats.txt")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_clean_csv(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_report(rows), encoding="utf-8")
    print(f"Wrote statistics to {args.output}")


if __name__ == "__main__":
    main()
