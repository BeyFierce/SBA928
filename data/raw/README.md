# Raw data

`bank-additional.zip` is the lossless official UCI archive used by this project. It contains:

- `bank-additional/bank-additional-full.csv` — 41,188 rows and 21 columns;
- `bank-additional/bank-additional.csv` — the official 10% sample; and
- `bank-additional/bank-additional-names.txt` — field documentation.

Source: https://archive.ics.uci.edu/dataset/222/bank%2Bmarketing  
Direct archive: https://archive.ics.uci.edu/static/public/222/bank%2Bmarketing.zip  
Dataset DOI: https://doi.org/10.24432/C5K306  
License: CC BY 4.0

The UCI download bundles `bank.zip` and `bank-additional.zip`. This repository tracks the inner `bank-additional.zip`, which is the exact source archive for the file analyzed in the report.

Expand it with:

```bash
unzip -o data/raw/bank-additional.zip -d data/raw
```

The expanded directory is ignored because it is a byte-for-byte reproducible copy of this archive.
