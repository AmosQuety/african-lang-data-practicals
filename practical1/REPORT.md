# Practical I: Data Preparation Pipeline — Luganda MasakhaNER

## 1. Dataset and source

**Dataset:** MasakhaNER 1.0, Luganda (`lug`) subset — a named entity recognition (NER) corpus
in CoNLL format (`TOKEN TAG` per line, blank line between sentences).

**Source:** `masakhane-io/masakhane-ner` GitHub repository, `data/lug/` directory, commit
`ba5843cd08aa491d5f96a5e809e71eb9ec461391` (authored 2025-10-15), retrieved 2026-09-28.
Two dataset versions exist in this repository (MasakhaNER 1.0 in `data/`, MasakhaNER 2.0 in
`MasakhaNER2.0/data/`); MasakhaNER 1.0 was used because the source repository's own README
lists it first (see `DECISIONS.md` D1).

**Primary or secondary:** Secondary. The data was collected and annotated by named Masakhane
community volunteers (for Luganda: Joyce Nabende, Jonathan Mukiibi, Eric Peter Kigaye, Ivan
Ssenkungu, Ibrahim Mbabaali, Batista Tobius, Maurice Katusiime, Deborah Nabagereka, Tobius
Saolo — per the source repo's `data/README.md`), not by me.

**License:** Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
applies to the NER dataset (the code, separately, is Apache 2.0). Quoted verbatim from the
source repository's `LICENSE` file starting at line 212; the full text and provenance are in
`DATASET_INFO.md`. The source `data/README.md` additionally notes that the underlying
monolingual news text "have difference licenses depending on the news website license" — a
caveat from the source, not independently verified here.

**Citation:**
Adelani et al. (2021), "MasakhaNER: Named Entity Recognition for African Languages,"
*Transactions of the Association for Computational Linguistics*, 9, 1116–1131.
doi: 10.1162/tacl_a_00416. Full BibTeX in `DATASET_INFO.md`.

## 2. State before preparation

Raw split sizes (from `practical1/reports/profile_before.json`):

| Split | Sentences | Tokens | Unique tokens |
|---|---|---|---|
| train | 1,428 | 33,003 | 11,362 |
| dev | 200 | 3,771 | 2,009 |
| test | 407 | 9,841 | 4,501 |

Sentence length (tokens): train min 1 / median 21 / mean 23.11 / max 91; dev min 6 / median 17 /
mean 18.86 / max 49; test min 6 / median 23 / mean 24.18 / max 67.

Issues found by `scripts/profile.py`:

- **Unicode issues** (non-NFC strings, invisible/zero-width/control characters, unusual
  whitespace, curly quotes): **none found** in any split.
- **Malformed lines** (wrong column count): **none found** — every non-blank line in all three
  files has exactly 2 space-separated columns.
- **Empty sentences:** none.
- **One-token sentences:** 1, in train (raw line 19929: token `.` tagged `O`).
- **Exact duplicate sentences within a split:** train had 8 duplicate groups (8 extra instances
  beyond the first occurrence), test had 4 groups (4 extra instances), dev had 0. Example (train):
  `"Sizoni ewedde baamalira mu kyamwenda ku ttiimu 21 ."` appeared twice.
- **Exact duplicate sentences across splits (train vs. test):** 1 — the sentence starting
  `"Ye omubaka we Buvuma mu Palamenti Robert Migadde Ndugwa..."` appears verbatim in both train
  and test.
- **Invalid BIO sequences:** 3, all in train (lines 6309, 17415, 25539), all the same shape: the
  very first tag of the sentence is an `I-<TYPE>` tag with nothing preceding it, e.g. sentence
  starting `Amagatte bibiri ebivunaanyizibwa...` began with tag `I-ORG` instead of `B-ORG` or `O`.

Full detail, including all examples, is in `practical1/reports/profile_before.md` and
`profile_before.json`.

## 3. Preprocessing steps and what each changed

Implemented in `scripts/preprocess.py`. Only steps shown to be needed by Stage 2 profiling were
applied; the rest were deliberately skipped (see `DECISIONS.md` D5–D9 for full reasoning on
every step below).

| Step | Applied? | Result |
|---|---|---|
| Unicode NFC normalisation / invisible-control-char removal | **Skipped** | Stage 2 found 0 instances in any split — nothing to normalise (D5) |
| Whitespace / quote normalisation | **Skipped** | Stage 2 found 0 unusual whitespace / curly quotes (D6) |
| Exact-duplicate removal (within split, keep first) | **Applied** | train: 8 removed (1428→1420); test: 4 removed (407→403); dev: unchanged |
| Cross-split (train/test) duplicate handling | **Flagged, not deleted** | 1 sentence (`test-343` in processed output) is reported in `changes.csv` as also appearing in train; kept in test per task instructions (D7) |
| BIO repair | **Applied, unambiguous cases only** | All 3 invalid-BIO sentences had the identical, unambiguous shape (leading `I-` tag with no preceding token) and were auto-fixed to `B-`; all 3 logged in `bio_issues.csv` with before/after tags; re-validated as fully resolved |
| Reformat to JSONL | **Applied** | `{id, split, tokens, ner_tags}` per line, written to `practical1/data/processed/{split}.jsonl` |

**Before/after examples** (full detail in `practical1/reports/changes.csv` and `bio_issues.csv`,
16 and 3 rows respectively):

- Duplicate removal (train): `"Sizoni ewedde baamalira mu kyamwenda ku ttiimu 21 ."` — kept the
  first occurrence, removed the second.
- Cross-split flag (test): `"Ye omubaka we Buvuma mu Palamenti Robert Migadde Ndugwa yagambye
  nti ebbanga ddene..."` — logged as present in both train and test; test copy retained.
- BIO fix (train, line 6309): tags before `I-ORG O O O O O O B-ORG ...` → after
  `B-ORG O O O O O O B-ORG ...` (first tag only changed).

Token and tag list lengths were asserted equal for every sentence at the end of the script
(checked twice: once inside `preprocess.py`, once independently afterward) — no mismatches.

## 4. Validation

**Automatic (Stage 4a):** `scripts/validate.py` re-parsed every processed JSONL file and ran 19
checks: valid JSONL per split, token/tag length match per split, valid BIO per split, no empty
sentences per split, no duplicate sentences within split, unique IDs per split, plus one
informational (non-gating) check surfacing the retained train/test overlap. **All 19 checks
passed.** Full results in `practical1/reports/validation.md`.

**Manual review (Stage 4b):** [TO BE COMPLETED BY STUDENT AFTER MANUAL REVIEW]

A reproducible (seed=42) sample of 100 sentences was drawn from the *raw* data, allocated
proportionally to split size (train 70, dev 10, test 20 — see `DECISIONS.md` D10), and written
to `practical1/reports/manual_review_sample.csv` with columns `id, split, raw_text,
processed_text, auto_flags, my_verdict, my_notes`. The `my_verdict` and `my_notes` columns are
intentionally blank; this section will be completed once that manual review is done.

## 5. State after preparation

| Split | Sentences (raw → processed) | Tokens (raw → processed) | Duplicates removed | BIO issues fixed |
|---|---|---|---|---|
| train | 1,428 → 1,420 | 33,003 → 32,883 | 8 | 3 |
| dev | 200 → 200 | 3,771 → 3,771 | 0 | 0 |
| test | 407 → 403 | 9,841 → 9,758 | 4 | 0 |

Unique token counts are unchanged (11,362 / 2,009 / 4,501) since no token text was altered by
any applied step — only whole sentences were removed (duplicates) or single tag characters
changed (BIO fix), and no Unicode/whitespace normalisation was needed. Label distributions
shifted only by the small amount contributed by the 12 removed duplicate sentences (e.g. train
`O` count 27,964 → 27,862); full distributions are in `profile_before.md` / `profile_after.md`.

After preprocessing: 0 exact duplicates remain within any split, 0 invalid BIO sequences remain,
0 malformed lines, 0 empty sentences — confirmed by both `profile_after.json`/`.md` and
`validation.md`.

## 6. Limitations and remaining issues

- **Train/test leakage (1 sentence):** One sentence is verbatim-identical between train and
  test. It was deliberately *not* removed from test, per the task's instruction to report rather
  than silently delete such cases (`DECISIONS.md` D7). Any downstream evaluation on this test
  set should be aware that this single sentence could be memorised rather than generalised on.
- **Version choice:** MasakhaNER 1.0 was used rather than the larger, more recent MasakhaNER 2.0
  (also present in the same source repository), because the task instructed use of whichever
  version is found first and the source README lists 1.0 first (`DECISIONS.md` D1). Numbers in
  this report describe MasakhaNER 1.0 only.
- **BIO fix scope:** Only the single unambiguous BIO error pattern (leading `I-` tag at sentence
  start) was auto-fixed. No mid-sentence BIO anomalies of this kind were found in this dataset,
  so no judgement call about repairing an ambiguous mid-sentence case was needed here — but if a
  future version of this data contains such cases, this pipeline will not repair them and will
  need `bio_issues.csv`-style manual handling for those instead.
- **License caveat inherited from source:** the source repository states the underlying
  monolingual news text may carry additional per-outlet licensing beyond CC BY-NC 4.0; this was
  not independently verified per sentence.
- **Manual review not yet done:** Section 4's manual-review subsection is a placeholder pending
  the student's own pass over `manual_review_sample.csv`.
- **Near-duplicate (fuzzy) detection was not attempted** — only exact string matches were
  checked and removed. This is a scope limitation, not a finding: no fuzzy-similarity search
  (e.g. edit distance or n-gram overlap) was run, so it is unknown whether near-duplicate
  sentences (e.g. differing by punctuation or a single reworded clause) exist in this data. See
  `DECISIONS.md` D11 for why this was out of scope for this pipeline rather than a "none found"
  result.
