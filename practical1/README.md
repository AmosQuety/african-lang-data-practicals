# Practical I — Luganda MasakhaNER Data Preparation Pipeline

Data-preparation pipeline (sourcing → profiling → preprocessing → validation → write-up) for
the Luganda subset of MasakhaNER 1.0. See `REPORT.md` for the full write-up and `DECISIONS.md`
for the reasoning behind every choice made.

## Folder layout

```
practical1/
├── README.md                  # this file
├── requirements.txt           # dependencies (none beyond Python stdlib)
├── DATASET_INFO.md            # source, license, citation
├── DECISIONS.md               # every choice made, with evidence, alternatives, risk
├── LOG.md                     # running log of what was done, in order
├── REPORT.md                  # the write-up (sections 1-6)
├── VIVA_NOTES.md              # anticipated viva questions and answers
├── data/
│   ├── raw/                   # UNMODIFIED originals: train.txt, dev.txt, test.txt
│   └── processed/             # pipeline output: train.jsonl, dev.jsonl, test.jsonl
└── reports/
    ├── profile_before.json / .md      # Stage 2: raw-data profile
    ├── profile_after.json / .md       # Stage 4: processed-data profile
    ├── changes.csv                    # every change made in preprocessing, step by step
    ├── bio_issues.csv                 # every BIO tag issue found, fixed or not
    ├── preprocess_summary.json        # counts summary from the preprocessing run
    ├── validation.md                  # Stage 4a: automatic validation results
    └── manual_review_sample.csv       # Stage 4b: 100-sentence sample for manual QA

scripts/
├── profile.py            # Stage 2 & 4a "after": profiles a CoNLL or JSONL split
├── preprocess.py         # Stage 3: dedup, BIO auto-fix, reformat to JSONL
├── validate.py           # Stage 4a: automatic assertions over processed data
└── sample_for_review.py  # Stage 4b: reproducible manual-review sample
```

`data/raw/` is never modified by any script — it is only ever read from.

## How to re-run the pipeline

All commands assume the working directory is the repository root (the folder containing
`practical1/` and `scripts/`), and Python 3.8+ with no extra packages (see `requirements.txt`).

```bash
# Stage 2: profile the raw data (writes profile_before.json/.md)
python3 scripts/profile.py \
  --data-dir practical1/data/raw \
  --out-json practical1/reports/profile_before.json \
  --out-md practical1/reports/profile_before.md \
  --title "Profile: Raw Data (before preparation)"

# Stage 3: preprocess (writes data/processed/*.jsonl, changes.csv, bio_issues.csv,
# preprocess_summary.json)
python3 scripts/preprocess.py

# Stage 4a: profile the processed data (writes profile_after.json/.md)
python3 scripts/profile.py \
  --data-dir practical1/data/processed \
  --out-json practical1/reports/profile_after.json \
  --out-md practical1/reports/profile_after.md \
  --jsonl \
  --title "Profile: Processed Data (after preparation)"

# Stage 4a: run automatic validation assertions (writes validation.md)
python3 scripts/validate.py

# Stage 4b: draw the manual-review sample (writes manual_review_sample.csv)
python3 scripts/sample_for_review.py
```

Re-running the full sequence above from a clean checkout of `data/raw/` reproduces
`data/processed/`, all files in `reports/`, byte-for-byte, because:
- `preprocess.py` and `profile.py` have no randomness.
- `sample_for_review.py` uses a fixed random seed (42).

This was verified directly — see the Stage 6 entry in `LOG.md` for the confirmation run.

## Notes on scope

- `data/raw/` is the unmodified original from `masakhane-io/masakhane-ner` (`data/lug/`,
  MasakhaNER 1.0). See `DATASET_INFO.md`.
- `manual_review_sample.csv`'s `my_verdict` and `my_notes` columns are intentionally blank —
  filling them in is a manual step for the student, not part of this automated pipeline.
