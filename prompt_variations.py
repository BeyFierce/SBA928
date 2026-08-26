"""Run four prompt designs against the same product-review evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from flan_inference import generate
from market_data import OUTPUT_DIR


SOURCE = (
    "Product: reusable water bottle. Rating: 2 out of 5. Review: It keeps drinks cold, "
    "but the lid began leaking after two weeks."
)

PROMPTS = {
    "A — multi-part numbered list": (
        "Analyze the following customer review. Identify: 1. strongest positive feature "
        "2. primary problem 3. one recommendation.\nContext: " + SOURCE
    ),
    "B — single direct question": (
        "What is the main problem customers report with this product?\nContext: " + SOURCE
    ),
    "C — positive framing": (
        "What feature do customers like most about this product?\nContext: " + SOURCE
    ),
    "D — role plus constraint": (
        "You are a market research analyst. In one sentence, state the product defect "
        "supported by this review.\nContext: " + SOURCE
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="google/flan-t5-small")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "part1_baseline_results.txt")
    parser.add_argument("--max-new-tokens", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    blocks = []
    for label, prompt in PROMPTS.items():
        response = generate(prompt, args.model, args.max_new_tokens)
        blocks.append(f"{label}\nPROMPT\n{prompt}\n\nOUTPUT\n{response}\n")
        print(f"{label}: {response}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n---\n\n".join(blocks), encoding="utf-8")


if __name__ == "__main__":
    main()
