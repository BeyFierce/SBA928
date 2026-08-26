"""Fast integrity tests that do not download or train a language model."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from market_data import CLEAN_CSV, ROOT, read_jsonl
from review import review


def test_split_counts_and_uniqueness() -> None:
    errors, counts = review(ROOT / "data/splits")
    assert errors == []
    assert counts == {"train.jsonl": 149, "validation.jsonl": 32, "eval_holdout.jsonl": 33}


def test_cleaned_dataset_removes_duration() -> None:
    with CLEAN_CSV.open(encoding="utf-8", newline="") as handle:
        fields = next(csv.reader(handle))
    assert "duration" not in fields
    assert {"source_row", "age_group", "converted"}.issubset(fields)


def test_comparison_guard_cases() -> None:
    records = read_jsonl(ROOT / "data/evaluation/comparison_cases.jsonl")
    assert len(records) == 8
    assert [record["metadata"]["campaign_contacts"] for record in records] == [1, 6, 14, 4, 2, 3, 6, 4]
    assert sum(record["metadata"]["fatigue_rule_applies"] for record in records) == 5


def test_reported_training_metrics_are_labeled() -> None:
    payload = json.loads((ROOT / "outputs/reported_training_metrics.json").read_text(encoding="utf-8"))
    assert payload["provenance"] == "recovered from the submitted SBA928_report.md"
    assert payload["final_training_loss"] == 0.5686
    assert payload["validation_loss"]["5"] == 0.2676
