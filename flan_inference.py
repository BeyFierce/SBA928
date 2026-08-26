"""Run a small, reproducible inference check with FLAN-T5-small."""

from __future__ import annotations

import argparse


DEFAULT_PROMPT = (
    "What is the main problem customers report with this product?\n"
    "Context: A reusable water bottle was rated 2 out of 5. The reviewer says it keeps "
    "drinks cold, but the lid began leaking after two weeks."
)


def generate(prompt: str, model_name: str, max_new_tokens: int) -> str:
    """Load a text-to-text model and greedily decode one response."""
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    encoded = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
    generated = model.generate(**encoded, max_new_tokens=max_new_tokens, do_sample=False)
    return tokenizer.decode(generated[0], skip_special_tokens=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--model", default="google/flan-t5-small")
    parser.add_argument("--max-new-tokens", type=int, default=80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(generate(args.prompt, args.model, args.max_new_tokens))


if __name__ == "__main__":
    main()
