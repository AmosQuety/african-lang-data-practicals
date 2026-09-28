# Decision Record — Practical I

Entries are written as decisions are made, in order.

---

## D1: Which dataset version to use (MasakhaNER 1.0 vs 2.0)

- **Decision:** Use MasakhaNER 1.0's `data/lug/` folder (not `MasakhaNER2.0/data/lug/`).
- **Evidence:** The source repo's root `README.md` lists dataset locations in this order:
  "MasakhaNER 1.0 can be found in CoNLL format in `data/`" is stated before "MasakhaNER 2.0 can
  be found in CoNLL format in `MasakhaNER2.0/data/`". `data/lug/` is also the top-level, simpler
  path, and is the version that was found first while browsing the repo tree from its root.
  Instructions said to use whichever is found first; `data/lug/` is that one.
- **Alternatives considered:** `MasakhaNER2.0/data/lug/` — larger (train.txt 821,977 bytes vs
  315,679 bytes for 1.0; sizes from `ls -la` on both folders), expanded annotation. Rejected only
  because the task explicitly says to use whichever is found first, not the "best" or largest
  version — this was a rule-following choice, not a quality judgement.
- **Risk:** MasakhaNER 2.0 is a strict superset/improvement for Luganda per the paper abstract, so
  this run is not using the most complete available annotation for this language. Numbers in this
  report describe MasakhaNER 1.0 only and should not be assumed to describe 2.0.
- **Confidence:** High that this satisfies the stated instruction (use whichever found first).
  Low confidence this is the "better" dataset for downstream use — that was not the question asked.

---

## D2: Primary vs secondary data classification

- **Decision:** Treat this as secondary data.
- **Evidence:** `data/README.md` in the source repo lists named volunteer annotators (e.g. for
  Luganda: Joyce Nabende, Jonathan Mukiibi, Eric Peter Kigaye, Ivan Ssenkungu, Ibrahim Mbabaali,
  Batista Tobius, Maurice Katusiime, Deborah Nabagereka, Tobius Saolo) as the people who collected
  and annotated the data — not me.
- **Alternatives considered:** None reasonably — I did not perform any original data collection,
  so "primary" was never a live option.
- **Risk:** None from this classification itself; it just needs to be stated correctly in the
  report.
- **Confidence:** High.

---

## D3: License text handling

- **Decision:** Quote the CC BY-NC 4.0 license verbatim from the source repo's `LICENSE` file
  (starting at "Attribution-NonCommercial 4.0 International"), and note the Apache 2.0 license
  that applies to the code (not the data) separately, per the explicit split described in
  `data/README.md` line 7.
- **Evidence:** `LICENSE` (source repo root) contains both texts concatenated; `data/README.md`
  explicitly attributes CC BY-NC 4.0 to "the NER dataset" and Apache 2.0 to "the code."
- **Alternatives considered:** Summarizing the license in my own words. Rejected because the task
  requires the license "copied VERBATIM ... with the file path it came from," and paraphrasing a
  legal text risks misstating its terms.
- **Risk:** The full CC BY-NC 4.0 legal code is long (~400 lines); DATASET_INFO.md quotes the
  license header/preamble verbatim and points to the exact lines in the source repo (`LICENSE`,
  lines 212–610) rather than reproducing all ~400 lines inline, to keep DATASET_INFO.md readable.
  This is a judgement call on how much verbatim text to inline vs cite by location.
  Risk: someone reading only DATASET_INFO.md doesn't see the complete legal text inline (they get
  the exact source location instead).
- **Confidence:** Medium. The attribution split (code=Apache2, data=CC-BY-NC-4.0) is explicitly
  stated by the source repo, so that part is high confidence. The choice of how much of the long
  CC BY-NC 4.0 text to inline vs point to is a formatting judgement call, not something the source
  data dictated.

---

## D4: Raw data must stay byte-identical

- **Decision:** Copy `train.txt`, `dev.txt`, `test.txt` from the source repo into
  `practical1/data/raw/` with no modification, and verify with MD5 checksums.
- **Evidence:** MD5 checksums of source and copy are identical:
  train `eb2b2b6ed24401eb7f35f3e9470e0247`, dev `03c881a9cd667bb0e29ac1da166ec2ca`,
  test `cebccbf4d1e278617aa6f5a399738b7b` (matched on both sides — see DATASET_INFO.md).
- **Alternatives considered:** None — the task explicitly requires unmodified originals in
  `data/raw/`.
- **Risk:** None identified.
- **Confidence:** High.

---

## D5: Unicode normalisation and control/invisible characters — skipped

- **Decision:** Skip Unicode NFC normalisation and invisible/control-character stripping as an
  active preprocessing step.
- **Evidence:** `profile_before.json`/`.md` (Stage 2) report `unicode_issue_sentence_count: 0`
  for all three splits (train, dev, test) — no non-NFC strings, zero-width/invisible characters,
  control characters, unusual whitespace, or curly quotes were found anywhere in the raw data.
- **Alternatives considered:** Running NFC normalisation unconditionally "just in case." Rejected
  per the task's own rule ("Only apply a step if Stage 2 showed it is needed") — applying a no-op
  transform for the sake of it is exactly what the instructions say not to do, and it would still
  need to appear as a "changed" step in changes.csv (with zero actual changes), which is noise.
- **Risk:** If some other Luganda MasakhaNER copy or downstream tool has different Unicode
  handling, this dataset copy simply doesn't need it — the risk is low since this was checked
  exhaustively, not assumed.
- **Confidence:** High — this is a directly observed absence, not a guess.

## D6: Whitespace/quote normalisation — skipped

- **Decision:** Skip whitespace and quote/punctuation normalisation.
- **Evidence:** Same profiling pass found no unusual whitespace characters (tabs, no-break
  spaces, etc.) and no curly/smart quotes in any split (see D5 evidence — same check covers both).
- **Alternatives considered:** None applied, for the same reason as D5.
- **Risk:** None identified from the data itself.
- **Confidence:** High.

## D7: Exact-duplicate sentence removal — apply, but only within-split; test/train overlap flagged not deleted

- **Decision:** Remove exact-duplicate sentences within each split (keep first occurrence only).
  Do NOT delete the train/test overlap sentence; instead report it explicitly.
- **Evidence:** `profile_before.json` found: train has 8 duplicate groups (8 extra instances),
  test has 4 duplicate groups (4 extra instances), dev has 0. Additionally there is exactly 1
  sentence that appears in BOTH train and test (the "Ye omubaka we Buvuma..." sentence, full text
  in `profile_before.json` under `cross_split_exact_duplicates`).
- **Alternatives considered:** (a) Do nothing about duplicates — rejected because within-split
  exact duplicates inflate frequency counts and give a model repeated identical training signal
  for no benefit. (b) Silently delete the train/test overlapping sentence from test — rejected
  per the task's explicit instruction: "report any test sentences that also appear in train
  instead of silently deleting them from test." Silent deletion would also change the test set
  size in a way future readers of this repo wouldn't know about without diffing files.
- **Risk:** Keeping the train/test overlap sentence in test means test-set metrics computed
  downstream will include one sentence the model may have memorised verbatim from train — a
  (very small, n=1) train/test leakage risk. Given it's a single sentence out of 407 test
  sentences, the effect on aggregate metrics is expected to be negligible, but it is a real,
  disclosed limitation.
- **Confidence:** High on the mechanics (what was found, what was removed). Medium on whether
  leaving the leak sentence in test is the "best" choice for someone about to train a model with
  this data vs. removing it — the assignment's instruction is followed here rather than an
  independent ML-methodology judgement call.

## D8: BIO issues — auto-fix only the unambiguous leading-I- case, flag nothing else for auto-repair

- **Decision:** Auto-fix only sentences where an `I-<TYPE>` tag appears at position 0 of the
  sentence (i.e., with no preceding token at all) — convert it to `B-<TYPE>`. All three BIO issues
  found in Stage 2 profiling are exactly this pattern. No other BIO error types were found, so no
  other auto-fix rule was needed.
- **Evidence:** All 3 invalid-BIO sentences reported in `profile_before.json` (train lines 6309,
  17415, 25539) have the identical issue shape: `'I-<TYPE>' follows 'O' (I- tag with no preceding
  B-/I- of same type)` at `index: 0` — the very first tag of the sentence. dev and test had zero
  BIO issues.
- **Alternatives considered:** Auto-fixing any `I-` tag that follows `O` regardless of position
  (not just position 0) — rejected as NOT unambiguous: an `I-PER` following `O` mid-sentence could
  indicate an annotation error where a `B-PER` was intended, OR it could indicate a missing token
  boundary, OR (in principle) an annotator inconsistency about entity continuation across a
  conjunction — the correct fix is not obvious from the tag sequence alone. The task explicitly
  says "do NOT silently repair" ambiguous cases and only auto-fix "unambiguous cases like a
  leading I- tag that should be B-" — which is precisely and only the case found here.
- **Risk:** If any of these 3 sentences' leading I- tag was actually meant to signal "this
  continues an entity from a previous (truncated) sentence" rather than a plain annotation slip,
  the auto-fix would be wrong. Given these are standalone sentences (not a continued document
  stream) and the CoNLL format used here doesn't carry cross-sentence entity continuation, this
  risk is considered low but is disclosed. All 3 affected sentences are logged before/after in
  `changes.csv` and also in `bio_issues.csv` for manual review.
- **Confidence:** High that the fix rule matches the task's stated "unambiguous" bar. Medium-high
  confidence the fix is linguistically correct, since I cannot verify original annotator intent.

## D9: Reformatting to JSONL — field choices

- **Decision:** Each output line: `{"id": "<split>-<index>", "split": "<split>", "tokens": [...],
  "ner_tags": [...]}`. `id` is a newly assigned stable index per split (0-based), not taken from
  the source (the raw CoNLL files carry no sentence IDs).
- **Evidence:** Raw files have no sentence-ID column — confirmed by inspecting the 2-column
  format in Stage 2 profiling (`TOKEN TAG` only).
- **Alternatives considered:** Using the original file's starting line number as the ID instead
  of a fresh index. Rejected because line numbers shift if any lines are removed (e.g. duplicate
  sentences), which would make IDs non-contiguous and confusing; a clean 0-based per-split index
  is simpler and every ID is traceable to a raw start_line via `changes.csv`.
- **Risk:** IDs are not stable across raw-file edits upstream (if MasakhaNER updates its data,
  regenerating IDs here would renumber everything) — acceptable for a one-off coursework pipeline.
- **Confidence:** Medium — this is a default naming choice, not dictated by the data.

## D10: Manual review sample size and allocation

- **Decision:** 100 sentences total, drawn with a fixed seed (42) from the RAW data,
  allocated proportionally to split size using largest-remainder rounding: train 70, dev 10,
  test 20.
- **Evidence:** Raw split sizes are train 1428, dev 200, test 407 (total 2035 sentences,
  from `profile_before.json`). Proportional shares of 100 are 70.17 (train), 9.83 (dev), 20.0
  (test); rounding down and distributing the 0 remaining slot(s) by largest fractional part
  gives exactly 70/10/20 (this happened to require no remainder redistribution since the
  base allocation already summed to 100).
- **Alternatives considered:** Equal allocation across splits (33/33/34) — rejected because it
  would over-represent dev (a small split) relative to train, giving a less representative
  overall sample of the corpus. Sampling from processed data instead of raw — rejected because
  the task explicitly says to sample from the RAW data (so removed duplicates and pre-fix BIO
  sentences are still reviewable), with processed_text shown alongside for comparison.
  Sample size 100 was specified directly by the task, not chosen by me.
- **Risk:** A sentence removed as a duplicate during preprocessing appears in the sample with
  `processed_text` = "(removed during preprocessing - see changes.csv)" rather than a real
  processed counterpart — this is intentional (shows the student what got removed) but could
  look like an error if not read carefully; noted here and in the sample's own column.
- **Confidence:** High on reproducibility (seed 42, deterministic proportional allocation).
  Medium on whether 100/proportional is the ideal QA sampling design in general — it satisfies
  the task's explicit instruction, not an independently derived power calculation.

## D11: Near-duplicate detection — skipped, not "none found"

- **Decision:** Did not attempt near-duplicate (fuzzy) detection beyond exact-string matching.
- **Evidence:** None to cite — this is the point. I did not run any similarity/edit-distance/
  n-gram-overlap check, so I have no observation to report either way. This is different from
  D5/D6 above, where a check WAS run and found nothing.
- **Alternatives considered:** Implementing a fuzzy-duplicate pass (e.g. normalized edit distance
  or shared n-gram threshold). Rejected for this run because the task's Stage 3 candidate-step
  list only specifies "removal of exact duplicate sentences," and building and tuning a
  similarity threshold without any specific evidence of near-duplicates would be adding an
  unrequested step without justification.
- **Risk:** If near-duplicates exist in this corpus (plausible in news-sourced text, e.g. wire
  reports republished with minor edits), they remain in the data and could inflate similarity
  between train/test or train sentences beyond the exact-match cases already found and handled.
- **Confidence:** High that this is honestly reported as "not checked" rather than misreported as
  "none found."

(Further entries added during Stage 6 as hand-off decisions are made.)
