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
