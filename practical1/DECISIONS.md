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

(Further entries added during Stage 2/3/4 as profiling and preprocessing decisions are made.)
