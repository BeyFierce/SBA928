"""Fine-tune google/flan-t5-small on the SBA 928 training split."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Any

from market_data import MODEL_DIR, OUTPUT_DIR, SPLIT_DIR


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="google/flan-t5-small")
    parser.add_argument("--train", type=Path, default=SPLIT_DIR / "train.jsonl")
    parser.add_argument("--validation", type=Path, default=SPLIT_DIR / "validation.jsonl")
    parser.add_argument("--output-dir", type=Path, default=MODEL_DIR)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--max-input-length", type=int, default=256)
    parser.add_argument("--max-target-length", type=int, default=160)
    parser.add_argument("--seed", type=int, default=928)
    parser.add_argument("--use-cpu", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args()


def write_run_artifacts(args: argparse.Namespace, trainer: Any) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    history_path = OUTPUT_DIR / "training_logs.jsonl"
    with history_path.open("w", encoding="utf-8") as handle:
        for item in trainer.state.log_history:
            handle.write(json.dumps(item, sort_keys=True) + "\n")

    manifest = {
        "base_model": args.model,
        "checkpoint_directory": str(args.output_dir),
        "python": platform.python_version(),
        "training_arguments": {
            "learning_rate": args.learning_rate,
            "train_batch_size": args.batch_size,
            "eval_batch_size": args.batch_size,
            "epochs": args.epochs,
            "max_input_length": args.max_input_length,
            "max_target_length": args.max_target_length,
            "seed": args.seed,
            "use_cpu": args.use_cpu,
        },
        "data_sha256": {
            "train": sha256(args.train),
            "validation": sha256(args.validation),
        },
        "metrics": trainer.state.log_history[-1] if trainer.state.log_history else {},
        "files": sorted(path.name for path in args.output_dir.iterdir()),
    }
    (args.output_dir / "checkpoint_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    args = parse_args()
    from datasets import load_dataset
    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        DataCollatorForSeq2Seq,
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
        set_seed,
    )

    set_seed(args.seed)
    dataset = load_dataset(
        "json",
        data_files={"train": str(args.train), "validation": str(args.validation)},
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)

    def preprocess(batch: dict[str, list[str]]) -> dict[str, Any]:
        inputs = [
            f"{instruction}\nContext: {context}"
            for instruction, context in zip(batch["instruction"], batch["context"], strict=True)
        ]
        encoded = tokenizer(inputs, max_length=args.max_input_length, truncation=True)
        labels = tokenizer(
            text_target=batch["target"], max_length=args.max_target_length, truncation=True
        )
        encoded["labels"] = labels["input_ids"]
        return encoded

    tokenized = dataset.map(
        preprocess,
        batched=True,
        remove_columns=dataset["train"].column_names,
        desc="Tokenizing market-research records",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(args.output_dir),
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=10,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        predict_with_generate=False,
        report_to=[],
        use_cpu=args.use_cpu,
        seed=args.seed,
        data_seed=args.seed,
    )
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model),
        processing_class=tokenizer,
    )
    train_result = trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    trainer.save_metrics("train", train_result.metrics)
    trainer.save_state()
    write_run_artifacts(args, trainer)
    print(json.dumps(train_result.metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
