# Test fixtures

Everything in this folder is **synthetic**. No real Rukiga, Yoruba, or
English data appears here — every `text`/`translation_en` value is a
placeholder string prefixed `TEST_CGG_TEXT_`, `TEST_YOR_TEXT_`, or
`TEST_EN_TRANSLATION_`, per the DATA SAFETY RULES in `practical2/README.md`
/ the task brief. These files exist only to exercise the pipeline's logic
(NFC normalisation, dedup, PII flags, etc.) and must never be copied into
`data/`, `release/`, or `reports/` as if they were real data.

- `raw_sample_author1.csv` / `raw_sample_author2.csv` — synthetic raw CSVs
  covering: NFC-decomposed vs. composed characters, curly quotes, a
  zero-width space, leading/trailing/doubled whitespace, an exact
  duplicate (after whitespace cleanup), a near-duplicate, a missing
  translation, fake PII-shaped strings (a placeholder email/phone —
  **not** anyone's real contact info), an English-looking Yoruba-labelled
  entry (for the language-sanity check), a translation identical to its
  source text, a very short entry, and one deliberately **conflicting
  `id`** shared between the two files with different text (to exercise
  cross-file id-conflict detection).
