"""Build deterministic train, validation, held-out, and comparison datasets."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any

from market_data import (
    CLEAN_CSV,
    MONTH_NAMES,
    SPLIT_DIR,
    benchmark_tables,
    conversion_rate,
    format_pct,
    grouped_rates,
    profile_context,
    profile_target,
    read_clean_csv,
    write_jsonl,
)


PROFILE_SAMPLE_SEED = 8
SPLIT_SEED = 928
FIXED_COMPARISON_SOURCE_ROWS = (0, 694, 23558, 278, 28, 101, 786, 299)
EXPECTED_COMPARISON_CONTACTS = (1, 6, 14, 4, 2, 3, 6, 4)

PROFILE_INSTRUCTIONS = (
    "Assess this customer's term-deposit conversion likelihood and recommend an outreach action.",
    "Analyze this customer profile against segment benchmarks and propose the next marketing step.",
    "Evaluate the strongest signal, weakest signal, likely barrier, and appropriate campaign action.",
)


def make_profile_record(
    row: dict[str, str],
    record_id: str,
    instruction_index: int,
    overall: float,
    tables: dict[str, dict[str, dict[str, float]]],
) -> dict[str, Any]:
    return {
        "id": record_id,
        "record_type": "customer_profile",
        "source_row": int(row["source_row"]),
        "instruction": PROFILE_INSTRUCTIONS[instruction_index % len(PROFILE_INSTRUCTIONS)],
        "context": profile_context(row),
        "target": profile_target(row, overall, tables),
        "metadata": {
            "campaign_contacts": int(row["campaign"]),
            "fatigue_rule_applies": int(row["campaign"]) >= 4,
        },
    }


def make_segment_records(rows: list[dict[str, str]], overall: float) -> list[dict[str, Any]]:
    rates = grouped_rates(rows, "job")
    records = []
    for job, values in rates.items():
        if job == "unknown":
            continue
        direction = "above" if values["rate"] >= overall else "below"
        records.append(
            {
                "id": f"segment-{job}",
                "record_type": "segment_benchmark",
                "instruction": "Benchmark this occupational segment against the bank's full campaign population.",
                "context": (
                    f"Occupation: {job}. Segment rows: {int(values['count'])}. "
                    f"Conversions: {int(values['conversions'])}. Overall benchmark: {format_pct(overall)}."
                ),
                "target": (
                    f"The {job} segment converts at {format_pct(values['rate'])}, which is {direction} "
                    f"the {format_pct(overall)} overall benchmark. Treat this as an internal segment "
                    "benchmark, not competitor intelligence."
                ),
            }
        )
    return records


def make_economic_records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    records = []
    for field in ("emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"):
        values = sorted(float(row[field]) for row in rows)
        median = values[len(values) // 2]
        low = [row for row in rows if float(row[field]) <= median]
        high = [row for row in rows if float(row[field]) > median]
        low_rate = conversion_rate(low)
        high_rate = conversion_rate(high)
        stronger = "lower" if low_rate >= high_rate else "higher"
        records.append(
            {
                "id": f"economic-{field}",
                "record_type": "market_trend",
                "instruction": "Interpret this macroeconomic indicator as a market trend without claiming causation.",
                "context": (
                    f"Indicator: {field}. Median: {median:.3f}. Conversion at or below median: "
                    f"{format_pct(low_rate)}. Conversion above median: {format_pct(high_rate)}."
                ),
                "target": (
                    f"Observed conversion is stronger in the {stronger} {field} group. This is an association "
                    "from one Portuguese bank during 2008-2010 and should not be interpreted as causal."
                ),
            }
        )
    return records


def make_campaign_records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    records = []
    for contacts in range(1, 9):
        group = [row for row in rows if int(row["campaign"]) == contacts]
        rate = conversion_rate(group)
        barrier = "contact fatigue risk" if contacts >= 4 else "no fatigue rule triggered"
        records.append(
            {
                "id": f"campaign-{contacts}",
                "record_type": "campaign_fatigue",
                "instruction": "Assess outreach fatigue for this campaign-contact count.",
                "context": (
                    f"Contacts this campaign: {contacts}. Matching source rows: {len(group)}. "
                    f"Observed conversion: {format_pct(rate)}."
                ),
                "target": f"Assessment: {barrier}. The observed conversion rate is {format_pct(rate)}.",
            }
        )
    return records


def make_month_records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    records = []
    for month, values in grouped_rates(rows, "month").items():
        records.append(
            {
                "id": f"month-{month}",
                "record_type": "seasonality",
                "instruction": "Summarize the observed monthly response pattern and its limitation.",
                "context": (
                    f"Month: {MONTH_NAMES[month]}. Rows: {int(values['count'])}. "
                    f"Conversions: {int(values['conversions'])}."
                ),
                "target": (
                    f"{MONTH_NAMES[month]} has an observed conversion rate of {format_pct(values['rate'])}. "
                    "The dataset is not a balanced calendar sample, so this is descriptive rather than causal."
                ),
            }
        )
    return records


def build(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], ...]:
    overall, tables = benchmark_tables(rows)
    by_source_row = {int(row["source_row"]): row for row in rows}
    fixed_rows = [by_source_row[index] for index in FIXED_COMPARISON_SOURCE_ROWS]
    actual_contacts = tuple(int(row["campaign"]) for row in fixed_rows)
    if actual_contacts != EXPECTED_COMPARISON_CONTACTS:
        raise ValueError(f"Comparison guard cases changed: {actual_contacts}")

    fixed_ids = set(FIXED_COMPARISON_SOURCE_ROWS)
    remaining_rows = [row for row in rows if int(row["source_row"]) not in fixed_ids]
    sampled_rows = random.Random(PROFILE_SAMPLE_SEED).sample(remaining_rows, 172)

    comparison = [
        make_profile_record(row, f"profile-eval-{position:02d}", position, overall, tables)
        for position, row in enumerate(fixed_rows, start=1)
    ]
    profiles = [
        make_profile_record(row, f"profile-{position:04d}", position, overall, tables)
        for position, row in enumerate(sampled_rows, start=1)
    ]

    non_fixed = (
        profiles
        + make_segment_records(rows, overall)
        + make_economic_records(rows)
        + make_campaign_records(rows)
        + make_month_records(rows)
    )
    if len(non_fixed) != 206:
        raise AssertionError(f"Expected 206 non-fixed records, found {len(non_fixed)}")

    random.Random(SPLIT_SEED).shuffle(non_fixed)
    train = non_fixed[:149]
    validation = non_fixed[149:181]
    holdout = non_fixed[181:] + comparison

    if (len(train), len(validation), len(holdout)) != (149, 32, 33):
        raise AssertionError("Expected 149/32/33 split")
    return train, validation, holdout, comparison


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=CLEAN_CSV)
    parser.add_argument("--output-dir", type=Path, default=SPLIT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_clean_csv(args.data)
    train, validation, holdout, comparison = build(rows)
    write_jsonl(args.output_dir / "train.jsonl", train)
    write_jsonl(args.output_dir / "validation.jsonl", validation)
    write_jsonl(args.output_dir / "eval_holdout.jsonl", holdout)
    write_jsonl(args.output_dir.parent / "evaluation/comparison_cases.jsonl", comparison)
    print(
        f"Wrote train={len(train)}, validation={len(validation)}, "
        f"held-out={len(holdout)}, comparison={len(comparison)}"
    )


if __name__ == "__main__":
    main()
