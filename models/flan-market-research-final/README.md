# FLAN market-research checkpoint

The submitted run saved its checkpoint to `./flan-market-research-final` after five CPU epochs. Normal GitHub files are limited to 100 MB, so this directory records the checkpoint configuration and reported metrics without committing the large binary weight file.

Recreate the full checkpoint with:

```bash
uv sync
unzip -o data/raw/bank-additional.zip -d data/raw
uv run python clean_dataset.py
uv run python build_dataset.py
uv run python review.py
uv run python train_flan.py
```

`train_flan.py` saves model weights, tokenizer files, trainer state, metrics, data hashes, and a fresh `checkpoint_manifest.json` here. The binary weight patterns are excluded by `.gitignore` but remain available locally for `compare_models.py`.
