"""Measure representation, rule coverage, and fairness risks in SBA 928."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from market_data import CLEAN_CSV, OUTPUT_DIR, ROOT, grouped_rates, read_clean_csv, read_jsonl


def profile_records() -> list[dict[str, Any]]:
    records = []
    for filename in ("train.jsonl", "validation.jsonl", "eval_holdout.jsonl"):
        records.extend(read_jsonl(ROOT / "data/splits" / filename))
    return [record for record in records if record["record_type"] == "customer_profile"]


def analyze(rows: list[dict[str, str]]) -> dict[str, Any]:
    profiles = profile_records()
    source_lookup = {int(row["source_row"]): row for row in rows}
    profile_rows = [source_lookup[int(record["source_row"])] for record in profiles]
    comparison = read_jsonl(ROOT / "data/evaluation/comparison_cases.jsonl")

    fatigue_profiles = sum(record.get("metadata", {}).get("fatigue_rule_applies", False) for record in profiles)
    fatigue_comparison = sum(
        record.get("metadata", {}).get("fatigue_rule_applies", False) for record in comparison
    )
    source_marital = grouped_rates(rows, "marital")
    source_education = grouped_rates(rows, "education")
    profile_marital = Counter(row["marital"] for row in profile_rows)
    profile_education = Counter(row["education"] for row in profile_rows)

    return {
        "source": {
            "rows": len(rows),
            "marital_unknown": {
                "rows": int(source_marital["unknown"]["count"]),
                "rate": source_marital["unknown"]["rate"],
            },
            "education_illiterate": {
                "rows": int(source_education["illiterate"]["count"]),
                "conversions": int(source_education["illiterate"]["conversions"]),
                "rate": source_education["illiterate"]["rate"],
            },
            "job_rate_range": {
                "blue-collar": grouped_rates(rows, "job")["blue-collar"]["rate"],
                "student": grouped_rates(rows, "job")["student"]["rate"],
            },
        },
        "profile_dataset": {
            "records": len(profiles),
            "marital_unknown_records": profile_marital["unknown"],
            "education_illiterate_records": profile_education["illiterate"],
            "fatigue_rule_records": fatigue_profiles,
            "fatigue_rule_share": fatigue_profiles / len(profiles),
        },
        "comparison_guard_cases": {
            "records": len(comparison),
            "fatigue_applicable": fatigue_comparison,
            "reported_fine_tuned_successes": 0,
        },
        "scope_limits": {
            "institution_count": 1,
            "country": "Portugal",
            "period": "May 2008-November 2010",
            "unrecorded_attributes": ["race", "ethnicity", "income", "region"],
            "duration_excluded_for_leakage": True,
        },
    }


def render(results: dict[str, Any]) -> str:
    source = results["source"]
    profiles = results["profile_dataset"]
    comparison = results["comparison_guard_cases"]
    blue = source["job_rate_range"]["blue-collar"] * 100
    student = source["job_rate_range"]["student"] * 100
    return f"""SBA 928 BIAS AND FAIRNESS RESULTS
=================================

REPRESENTATION
- Source marital=unknown: {source['marital_unknown']['rows']} rows ({source['marital_unknown']['rate'] * 100:.2f}% conversion)
- Profile records with marital=unknown: {profiles['marital_unknown_records']}
- Source education=illiterate: {source['education_illiterate']['rows']} rows, {source['education_illiterate']['conversions']} conversions ({source['education_illiterate']['rate'] * 100:.2f}%)
- Profile records with education=illiterate: {profiles['education_illiterate_records']}

RULE COVERAGE
- Customer-profile records: {profiles['records']}
- Contact-fatigue targets: {profiles['fatigue_rule_records']} ({profiles['fatigue_rule_share'] * 100:.1f}%)
- Held-out comparison cases where fatigue applies: {comparison['fatigue_applicable']} of {comparison['records']}
- Reported fine-tuned fatigue successes: {comparison['reported_fine_tuned_successes']} of {comparison['fatigue_applicable']}

FAIRNESS RISK
- Occupation conversion range: blue-collar {blue:.2f}% to student {student:.2f}%
- A target rule that deprioritizes below-average segments can reproduce historical access patterns.
- Point estimates for tiny groups (illiterate n=18; marital unknown n=80) are unstable.
- Race, ethnicity, income, and region are not recorded, so fairness cannot be audited on them.

MITIGATIONS
1. Stratified sampling with a minimum category floor.
2. Minimum sample thresholds or confidence intervals for segment claims.
3. Oversample rare conditional branches such as contact fatigue.
4. Test neutral, positive, and negative prompt framings on identical evidence.
5. Report performance by segment and rule branch, not only aggregate loss.
6. Require human review for recommendations that affect financial-product access.
7. Attach scope and time-period limitations to every reported conclusion.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=CLEAN_CSV)
    parser.add_argument("--text-output", type=Path, default=OUTPUT_DIR / "bias_results.txt")
    parser.add_argument("--json-output", type=Path, default=OUTPUT_DIR / "bias_results.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = analyze(read_clean_csv(args.data))
    args.text_output.parent.mkdir(parents=True, exist_ok=True)
    args.text_output.write_text(render(results), encoding="utf-8")
    args.json_output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote bias analysis to {args.text_output} and {args.json_output}")


if __name__ == "__main__":
    main()
