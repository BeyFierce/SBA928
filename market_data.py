"""Shared data utilities for the SBA 928 market-research pipeline."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
RAW_CSV = ROOT / "data/raw/bank-additional/bank-additional-full.csv"
CLEAN_CSV = ROOT / "data/processed/bank-additional-cleaned.csv"
SPLIT_DIR = ROOT / "data/splits"
OUTPUT_DIR = ROOT / "outputs"
MODEL_DIR = ROOT / "models/flan-market-research-final"

AGE_GROUPS = (
    (25, "18-25"),
    (35, "26-35"),
    (45, "36-45"),
    (55, "46-55"),
    (65, "56-65"),
    (10_000, "66+"),
)

MONTH_NAMES = {
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}


def age_group(age: int) -> str:
    """Map a source age to the bands used in the submitted analysis."""
    for upper, label in AGE_GROUPS:
        if age <= upper:
            return label
    raise ValueError(f"Unexpected age: {age}")


def read_semicolon_csv(path: Path = RAW_CSV) -> list[dict[str, str]]:
    """Read the original UCI semicolon-delimited file."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def read_clean_csv(path: Path = CLEAN_CSV) -> list[dict[str, str]]:
    """Read the cleaned comma-delimited dataset."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    """Write dictionaries as deterministic UTF-8 JSON Lines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSON Lines file."""
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def conversion_rate(rows: Iterable[dict[str, str]]) -> float:
    """Return the share of records whose target is yes."""
    materialized = list(rows)
    if not materialized:
        return 0.0
    return sum(row["y"] == "yes" for row in materialized) / len(materialized)


def grouped_rates(rows: Iterable[dict[str, str]], field: str) -> dict[str, dict[str, float]]:
    """Compute count, conversions, and conversion rate for one field."""
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row[field]].append(row)
    return {
        key: {
            "count": len(group),
            "conversions": sum(item["y"] == "yes" for item in group),
            "rate": conversion_rate(group),
        }
        for key, group in sorted(groups.items())
    }


def format_pct(value: float) -> str:
    """Format a rate as a one-decimal percentage, matching the report."""
    return f"{value * 100:.1f}%"


def profile_context(row: dict[str, str]) -> str:
    """Build a compact market-research context from one cleaned source row."""
    return (
        f"Age {row['age']} ({row['age_group']}), {row['job']}, {row['education']}, "
        f"{row['marital']}, housing loan {row['housing']}, personal loan {row['loan']}, "
        f"{row['contact']}, {MONTH_NAMES[row['month']]}, "
        f"{row['campaign']} contacts this campaign, prior outcome {row['poutcome']}, "
        f"Euribor 3m {float(row['euribor3m']):.3f}."
    )


def benchmark_tables(rows: list[dict[str, str]]) -> tuple[float, dict[str, dict[str, dict[str, float]]]]:
    """Build the five benchmark tables used in customer-profile targets."""
    overall = conversion_rate(rows)
    tables = {
        "occupation": grouped_rates(rows, "job"),
        "education level": grouped_rates(rows, "education"),
        "age cohort": grouped_rates(rows, "age_group"),
        "prior campaign outcome": grouped_rates(rows, "poutcome"),
        "contact timing": grouped_rates(rows, "month"),
    }
    return overall, tables


def profile_target(
    row: dict[str, str],
    overall: float,
    tables: dict[str, dict[str, dict[str, float]]],
) -> str:
    """Create a grounded target with verdict, evidence, barrier, and action."""
    signals = {
        "occupation": tables["occupation"][row["job"]]["rate"],
        "education level": tables["education level"][row["education"]]["rate"],
        "age cohort": tables["age cohort"][row["age_group"]]["rate"],
        "prior campaign outcome": tables["prior campaign outcome"][row["poutcome"]]["rate"],
        "contact timing": tables["contact timing"][row["month"]]["rate"],
    }
    average_signal = sum(signals.values()) / len(signals)
    if average_signal >= overall + 0.02:
        likelihood = "High"
    elif average_signal <= overall - 0.02:
        likelihood = "Low"
    else:
        likelihood = "Moderate"

    strongest_name, strongest_rate = max(signals.items(), key=lambda item: item[1])
    weakest_name, weakest_rate = min(signals.items(), key=lambda item: item[1])
    campaign_contacts = int(row["campaign"])

    if campaign_contacts >= 4:
        barrier = f"repeated contact fatigue ({campaign_contacts} contacts this campaign)"
    else:
        barrier = f"below-average response for this {weakest_name}"

    recommendations = {
        "High": "prioritize for personalized outreach with a competitive rate offer",
        "Moderate": "include in standard outreach with a tailored rate offer",
        "Low": "deprioritize; retarget after 90 days with a lower-minimum product",
    }
    return (
        f"Conversion likelihood: {likelihood}. "
        f"Strongest signal: {strongest_name} at {format_pct(strongest_rate)}. "
        f"Weakest signal: {weakest_name} at {format_pct(weakest_rate)}, "
        f"against a {format_pct(overall)} overall benchmark. "
        f"Primary barrier: {barrier}. "
        f"Recommendation: {recommendations[likelihood]}."
    )


def model_input(record: dict[str, Any]) -> str:
    """Join instruction and context in the format used during fine-tuning."""
    return f"{record['instruction']}\nContext: {record['context']}"
