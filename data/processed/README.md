# Processed data

`bank-additional-cleaned.csv.gz` is the complete cleaned 41,188-row dataset in lossless gzip form.

Changes from the original:

- removed `duration` to prevent post-call outcome leakage;
- added `source_row` for traceability to the original CSV;
- added `age_group` using the report's six age bands; and
- added numeric `converted` (`1` for `y=yes`, otherwise `0`).

Rebuild the uncompressed CSV after expanding the raw archive:

```bash
uv run python clean_dataset.py
gzip -n -9 -c data/processed/bank-additional-cleaned.csv > data/processed/bank-additional-cleaned.csv.gz
```

`gzip -n` omits timestamps so the compressed artifact is deterministic.
