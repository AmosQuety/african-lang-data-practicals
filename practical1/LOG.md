# Log — Practical I

All timestamps local session time (session runs 2026-09-28, Africa/Kampala UTC+03:00 for the
requester; the underlying container clock may differ — timestamps below are wall-clock at time of
action as recorded by the tool environment).

---

### 2026-09-28 — Stage 1: Sourcing
- Cloned `masakhane-io/masakhane-ner` (commit `ba5843cd08aa491d5f96a5e809e71eb9ec461391`,
  authored 2025-10-15) read-only, via `git clone --depth 1`.
- Located Luganda folders: `data/lug/` (MasakhaNER 1.0) and `MasakhaNER2.0/data/lug/`
  (MasakhaNER 2.0). Chose `data/lug/` (MasakhaNER 1.0) — see DECISIONS.md D1.
- Copied `train.txt` (34,431 lines), `dev.txt` (3,971 lines), `test.txt` (10,248 lines) verbatim
  into `practical1/data/raw/`. Verified byte-identical via MD5 checksum against source.
- Read root `README.md`, `data/README.md`, and `LICENSE` in the source repo. Recorded dataset
  info, primary/secondary classification, license (CC BY-NC 4.0 for data, Apache 2.0 for code),
  and citation in `DATASET_INFO.md`.
- Wrote `DECISIONS.md` with D1–D4.

### 2026-09-28 — Stage 2: Profile raw data ("before" snapshot)
- Wrote `scripts/profile.py`. Ran it against `practical1/data/raw/`, producing
  `practical1/reports/profile_before.json` and `profile_before.md`.
- Findings (all splits, full detail in profile_before.md):
  - train: 1428 sentences, 33003 tokens, 11362 unique tokens. dev: 200 sentences, 3771 tokens.
    test: 407 sentences, 9841 tokens.
  - 0 empty sentences in any split. 1 one-token sentence in train (line 19929, token "." tagged O).
  - Exact duplicate sentences within split: train 8 groups, test 4 groups, dev 0.
  - Cross-split exact duplicate: 1 sentence appears in both train and test.
  - Unicode issues (non-NFC, invisible/control chars, unusual whitespace, curly quotes): 0 found
    in any split.
  - Invalid BIO sequences: 3 in train (lines 6309, 17415, 25539), 0 in dev/test — all 3 are the
    same pattern: an I- tag as the very first tag of the sentence.
  - Malformed lines (wrong column count): 0 in any split.
- Recorded decisions D5 (skip Unicode normalisation - none needed), D6 (skip whitespace/quote
  normalisation - none needed), D7 (dedup within split, flag not delete cross-split overlap),
  D8 (auto-fix only unambiguous leading-I- BIO case), D9 (JSONL field/ID design) in
  `DECISIONS.md`.

### 2026-09-28 — Stage 3: Preprocessing
- Wrote `scripts/preprocess.py`, implementing exactly the steps justified in D5-D9 (no
  speculative steps).
- Ran it against `practical1/data/raw/`. Output counts:
  - train: 1428 raw -> 1420 processed (8 exact duplicates removed)
  - dev: 200 raw -> 200 processed (no change)
  - test: 407 raw -> 403 processed (4 exact duplicates removed)
  - 1 train/test cross-split duplicate sentence flagged in `changes.csv` and kept in test
    (not deleted), per instructions.
  - 3 BIO issues found in train, all auto-fixed (leading I- -> B-) and all fully resolved after
    the fix (verified: re-checked each fixed sentence's tags with the same BIO validator; no
    downstream issue introduced).
- Wrote `practical1/data/processed/{train,dev,test}.jsonl` (id, split, tokens, ner_tags).
- Wrote `practical1/reports/changes.csv` (12 dedup removals + 1 cross-split flag + 3 BIO fixes =
  16 rows) and `practical1/reports/bio_issues.csv` (3 rows, all auto_fixed=yes,
  fully_resolved=yes).
- Verified programmatically that every output sentence has `len(tokens) == len(ner_tags)`
  (assertion in the script, plus an independent check afterward) — all passed.

### 2026-09-28 — Stage 4: Validation
- Ran `scripts/profile.py --jsonl` against `practical1/data/processed/`, producing
  `profile_after.json`/`.md`. Compared to `profile_before`: 0 duplicates remain within any
  split, 0 invalid BIO sequences remain, token counts dropped by exactly the number of tokens in
  removed duplicate sentences (train 33003->32883, test 9841->9758, dev unchanged at 3771).
  The train/test cross-split duplicate is still present in both profiles, as intended (D7).
- Wrote `scripts/validate.py` with automated assertions: valid JSONL, token/tag length match,
  valid BIO, no empty sentences, no within-split duplicates, unique IDs per split, and an
  informational (non-gating) check that surfaces the known train/test overlap. Wrote
  `practical1/reports/validation.md` — **all 19 checks passed**.
- Wrote `scripts/sample_for_review.py`. Drew a reproducible (seed=42) 100-sentence sample from
  RAW data, proportional to split size (train 70, dev 10, test 20). Wrote
  `practical1/reports/manual_review_sample.csv` with `my_verdict`/`my_notes` left blank for
  the student. Recorded the allocation method as D10 in `DECISIONS.md`.

### 2026-09-28 — Stage 5: Draft write-up
- Wrote `practical1/REPORT.md` (sections 1-6) drawing all numbers directly from
  `profile_before.json/.md`, `profile_after.json/.md`, `changes.csv`, `bio_issues.csv`, and
  `validation.md`; cross-checked every reported figure against the JSON source files before
  finalizing.
- Manual-review subsection left with the required placeholder
  `[TO BE COMPLETED BY STUDENT AFTER MANUAL REVIEW]`.
- Recorded D11 in `DECISIONS.md`: near-duplicate detection was not attempted (explicitly
  distinguished from D5/D6, where a check was run and returned zero results) — corrected an
  earlier draft of REPORT.md that had implied "none found" for near-duplicates.

### 2026-09-28 — Stage 6: Hand-off
- Wrote `practical1/README.md` (folder layout, exact re-run commands) and
  `practical1/requirements.txt` (no third-party dependencies — stdlib only, tested on
  Python 3.11.15).
- Wrote `practical1/VIVA_NOTES.md`: anticipated viva questions, each answered strictly from
  `DECISIONS.md` and the reports, including honest "this was a default"/"I'm not certain"
  answers where that's the true answer (e.g. BIO-fix correctness, near-duplicate scope).
- **Reproducibility check:** recorded MD5 checksums of all 10 pipeline output files
  (`data/processed/*.jsonl`, `reports/changes.csv`, `reports/bio_issues.csv`,
  `reports/profile_before.json`, `reports/profile_after.json`, `reports/validation.md`,
  `reports/manual_review_sample.csv`, `reports/preprocess_summary.json`). Deleted all of them
  (leaving only `data/raw/` and the scripts), then re-ran the full pipeline from scratch in the
  order listed in `README.md`. Compared checksums: **all 10 files byte-identical** to the
  pre-deletion versions. `git diff --stat practical1/data/raw` confirmed the raw files were
  never touched (no diff). Pipeline is confirmed reproducible.
- Final commit and push to `practical1-run`.
