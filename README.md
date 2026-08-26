# SBA 928 — Enhancing Market Research with AI Prompt Engineering

This repository is the complete `uv` project for Brittney Perry's SBA 928 assessment. It uses the [UCI Bank Marketing dataset](https://archive.ics.uci.edu/dataset/222/bank%2Bmarketing) to demonstrate prompt variation, dataset construction, FLAN-T5-small fine-tuning, held-out comparison, and bias/fairness analysis.

The original Canvas submission contained the written report and a large archive, but not a usable GitHub project link. This reconstruction follows the report's recorded configuration and results, preserves the original metrics with explicit provenance, and makes every data-processing and model step reproducible.

## Checklist from instructor feedback

| Required item | Location |
|---|---|
| All Python files | Repository root and `tests/` |
| `pyproject.toml` and `uv.lock` | Repository root |
| Original dataset | `data/raw/bank-additional.zip` (official UCI archive) |
| Cleaned dataset | `data/processed/bank-additional-cleaned.csv.gz` |
| Train / validation / held-out data | `data/splits/` |
| Prompt script and outputs | `prompt_variations.py`, `outputs/part1_baseline_results.txt` |
| Model-training script | `train_flan.py` |
| Training configuration and logs | `outputs/training_config.json`, `outputs/training_log.csv`, `outputs/reported_training_metrics.json` |
| Checkpoint information | `models/flan-market-research-final/` |
| Base and fine-tuned outputs | `outputs/*model_outputs_reported.jsonl` |
| Comparison code and results | `compare_models.py`, `outputs/comparison.txt` |
| Bias code and results | `bias_analysis.py`, `outputs/bias_results.*` |
| Written report | `SBA928_report.md` |

## Project structure

```text
.
├── data/
│   ├── raw/                         # Lossless official UCI source archive
│   ├── processed/                   # Cleaned data with leakage removed
│   ├── splits/                      # 149 train / 32 validation / 33 held-out
│   └── evaluation/                  # Eight held-out guard cases
├── models/flan-market-research-final/
│   ├── README.md
│   └── checkpoint_info.json
├── outputs/                         # Prompt, training, comparison, and bias results
├── tests/
├── clean_dataset.py
├── explore.py
├── build_dataset.py
├── review.py
├── flan_inference.py
├── prompt_variations.py
├── train_flan.py
├── compare_models.py
├── bias_analysis.py
├── market_data.py
├── pyproject.toml
└── uv.lock
```

## Install

Install [uv](https://docs.astral.sh/uv/) and run:

```bash
uv sync
```

The lockfile pins the full dependency graph. `transformers` is constrained to version 4 because the original run recorded an incompatibility with version 5.

## Reproduce the data pipeline

The tracked UCI archive contains `bank-additional/bank-additional-full.csv` (41,188 rows, 21 columns). Expand it, clean it, rebuild all splits, review them, and regenerate descriptive/bias outputs:

```bash
unzip -o data/raw/bank-additional.zip -d data/raw
uv run python clean_dataset.py
uv run python explore.py
uv run python build_dataset.py
uv run python review.py
uv run python bias_analysis.py
uv run pytest
```

Cleaning removes `duration`, which is only known after a marketing call and would leak outcome information. It adds `source_row`, `age_group`, and numeric `converted` audit fields. The JSONL records use the required `instruction`, `context`, and `target` fields.

The dataset builder creates 214 records:

- 180 customer profiles;
- 11 known occupational segment benchmarks;
- 5 macroeconomic trend records;
- 8 campaign-fatigue records; and
- 10 monthly seasonality records.

The deterministic split is 149 train, 32 validation, and 33 held-out. Eight profile records are reserved as comparison guard cases. Five trigger the contact-fatigue rule, matching the evaluation described in the report.

## Re-run prompt engineering

```bash
uv run python prompt_variations.py
```

The submitted run held the product-review evidence constant and changed only prompt design. The recorded outputs are preserved in `outputs/part1_baseline_results.txt`, including the leading-question failure where a positively framed prompt produced a positive conclusion from negative evidence.

## Re-train FLAN-T5-small

```bash
uv run python train_flan.py
```

Recorded configuration:

| Parameter | Value |
|---|---|
| Base model | `google/flan-t5-small` |
| Learning rate | `3e-4` |
| Batch size | `4` |
| Epochs | `5` |
| Max input / target length | `256 / 160` |
| Original device | CPU |
| Original steps / runtime | `190 / 96.1 seconds` |
| Original final training loss | `0.5686` |

The command writes fresh logs and checkpoint files. Large model weights are intentionally not committed because GitHub's normal file limit is 100 MB; the repository includes exact configuration, data hashes, reported metrics, and rebuild instructions under `models/`. This satisfies checkpoint-information review without placing a several-hundred-megabyte binary in ordinary Git history.

## Re-run comparison

After training:

```bash
uv run python compare_models.py
```

This runs the base and local fine-tuned models with identical deterministic generation settings (`max_new_tokens=160`, `do_sample=False`). The report's verified example and 0-of-5 contact-fatigue result are preserved separately in `outputs/` and are labeled as recovered results, not newly generated output.

## Main findings

- The base model returned one extracted fact and did not follow the requested analysis format.
- Fine-tuning substantially improved structure, relevance, specificity, and retrieval of benchmark values.
- The fine-tuned model failed the minority contact-fatigue branch in all 5 applicable guard cases.
- `marital=unknown` is 0.19% of the source and appears in 0 profile-training records.
- `education=illiterate` has only 18 source rows and 4 conversions, so its 22.22% point estimate is unstable.
- Historical response-rate targets can systematically deprioritize blue-collar and lower-education customers.
- The data covers one Portuguese bank, one product, and May 2008-November 2010; it does not record race, ethnicity, income, or region.

## Data citation and license

Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5K306

The dataset is licensed under CC BY 4.0. Source details and checksums are documented in `data/raw/README.md`.
