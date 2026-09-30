# Review sheets — how to use them

Generated reproducibly with random seed 42: re-running `scripts/make_review_sheet.py` on the same dataset and flags produces the same sheets.

## Layer 1 — independent language review (per language)

- `layer1_cgg.csv` (Rukiga): 57 of 63 entries. See `layer1_cgg.NOTE.md`.
- `layer1_yor.csv` (Yoruba): 15 of 15 entries. See `layer1_yor.NOTE.md`.

## Layer 2 — cross-review between the two authors (English-side only)

- `layer2_by_author1.csv`: 28 entries. See `layer2_by_author1.NOTE.md`.
- `layer2_by_author2.csv`: 66 entries. See `layer2_by_author2.NOTE.md`.
- Shared overlap set: 16 entries, present in BOTH Layer 2 sheets (see `overlap_ids.csv`) — used by `scripts/compute_agreement.py` to measure inter-reviewer agreement.

**Note:** no `--contributor-map` was supplied, so author assignment used the project default (Author 1 = Rukiga collector, Author 2 = Yoruba collector, per docs/TEAM_PLAN.md). Pass `--contributor-map path/to/local/file.csv` (never committed) if contributors ever span both languages/authors.

## All sheets share these columns

`id, language, text, translation_en, auto_flags, reviewer_verdict, reviewer_correction, reviewer_notes`

`reviewer_verdict`, `reviewer_correction`, and `reviewer_notes` start blank — reviewers fill these in. `reviewer_verdict` is free text but `scripts/apply_corrections.py` and `scripts/compute_agreement.py` expect one of: `ok`, `needs_correction`, `reject` (see docs/VIVA_NOTES.md).

Once sheets are completed, run `scripts/compute_agreement.py` (on the two Layer 2 sheets) and `scripts/apply_corrections.py` (on all completed sheets).
