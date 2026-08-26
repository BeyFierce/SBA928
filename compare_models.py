"""Compare base and fine-tuned FLAN-T5 outputs on held-out guard cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from market_data import MODEL_DIR, OUTPUT_DIR, ROOT, model_input, read_jsonl, write_jsonl


def load_generator(model_name_or_path: str):
    """Return a deterministic generation function for a seq2seq checkpoint."""
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name_or_path)

    def generate(text: str, max_new_tokens: int = 160) -> str:
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        generated = model.generate(**encoded, max_new_tokens=max_new_tokens, do_sample=False)
        return tokenizer.decode(generated[0], skip_special_tokens=True)

    return generate


def score_output(output: str) -> dict[str, bool]:
    normalized = output.lower()
    return {
        "has_likelihood": "conversion likelihood:" in normalized,
        "has_strongest": "strongest signal:" in normalized,
        "has_weakest": "weakest signal:" in normalized,
        "has_barrier": "primary barrier:" in normalized,
        "has_recommendation": "recommendation:" in normalized,
        "identifies_fatigue": "contact fatigue" in normalized,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", default="google/flan-t5-small")
    parser.add_argument("--fine-tuned-model", type=Path, default=MODEL_DIR)
    parser.add_argument(
        "--cases", type=Path, default=ROOT / "data/evaluation/comparison_cases.jsonl"
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR / "generated_comparison")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    weight_files = list(args.fine_tuned_model.glob("*.safetensors")) + list(
        args.fine_tuned_model.glob("pytorch_model*.bin")
    )
    if not weight_files:
        raise SystemExit(
            "Fine-tuned weights are not stored in GitHub. Run `uv run python train_flan.py` "
            "to recreate the checkpoint, then rerun this comparison."
        )

    cases = read_jsonl(args.cases)
    base_generate = load_generator(args.base_model)
    fine_generate = load_generator(str(args.fine_tuned_model))
    base_rows: list[dict[str, Any]] = []
    fine_rows: list[dict[str, Any]] = []
    report_blocks = []

    for position, record in enumerate(cases, start=1):
        prompt = model_input(record)
        base_output = base_generate(prompt)
        fine_output = fine_generate(prompt)
        base_rows.append(
            {"evaluation": position, "id": record["id"], "output": base_output, **score_output(base_output)}
        )
        fine_rows.append(
            {"evaluation": position, "id": record["id"], "output": fine_output, **score_output(fine_output)}
        )
        report_blocks.append(
            f"EVALUATION {position}\nCONTEXT: {record['context']}\nBASE: {base_output}\n"
            f"FINE-TUNED: {fine_output}\nREFERENCE: {record['target']}\n"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "base_model_outputs.jsonl", base_rows)
    write_jsonl(args.output_dir / "fine_tuned_model_outputs.jsonl", fine_rows)
    (args.output_dir / "comparison.txt").write_text("\n---\n\n".join(report_blocks), encoding="utf-8")
    print(f"Compared {len(cases)} held-out cases in {args.output_dir}")


if __name__ == "__main__":
    main()
