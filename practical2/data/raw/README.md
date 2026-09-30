# data/raw/

This folder is where **our own collected data** goes — the CSV files each
author fills in by hand (or exports from a Google Form) while collecting
entries from real contributors.

**Nothing in this folder is created by the pipeline.** It is intentionally
empty in this repository except for this README and the blank
`practical2/docs/raw_template.csv` template (see `docs/SCHEMA.md` and
`docs/COLLECTION_PROTOCOL.md` for how to fill it in).

## What goes here

- One CSV file per author/collector (e.g. `raw_lug_author1.csv`,
  `raw_yor_author2.csv`), each following the schema in
  `practical2/docs/SCHEMA.md`.
- Files should use the columns from `practical2/docs/raw_template.csv`.

## What must NOT go here

- Real names, phone numbers, emails, or any other personal identifier for a
  contributor. Use anonymous `contributor_id` codes (e.g. `C001`) only.
- Any file mapping a `contributor_id` or `reviewer_id` to a real person's
  identity. That mapping (if you keep one at all, e.g. in your own notes)
  must live **outside this repository**, per `practical2/.gitignore` and
  `docs/COLLECTION_PROTOCOL.md`.

## Next step

Once raw CSVs are here, run `scripts/preprocess.py` (see the top-level
`practical2/README.md` for the exact command) to combine, clean and
validate them into `data/processed/dataset.jsonl`.
