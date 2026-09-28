# Log

Running log of what was done, when, and with what result. Timestamps are
UTC. Written as work happens, not reconstructed afterward.

---

## 2026-09-28T11:51:00Z — Setup

- Cloned `AmosQuety/african-lang-data-practicals`, created branch
  `practical2-run` off `main` (HEAD `dc47221`, "Add README for Practical 2:
  Data Preparation"). Working only inside `practical2/`.
- Confirmed Python 3.11.15 available. Installed `pytest` 9.1.1 via
  `pip3 install --break-system-packages pytest` (no system pytest present).
  No other non-stdlib dependencies are planned (agreement/kappa computation
  will use the standard library only, per spec).

## 2026-09-28T11:53:00Z — Stage 1: layout and schema

- Created `data/raw/`, `data/processed/`, `release/`, `reports/`,
  `scripts/`, `tests/fixtures/`, `docs/` under `practical2/`.
- Added `data/raw/README.md` explaining that raw data is hand-collected and
  never pipeline-generated.
- Added `.gitkeep` placeholders for empty dirs that need to exist in git
  (`data/processed`, `release`, `reports`, `tests/fixtures`).
- Added `practical2/.gitignore`: blocks any `*contributor_map*`,
  `*reviewer_map*`, `*id_map*` file, `.env`/`HF_TOKEN*`, and normal Python
  junk (`__pycache__`, `.pytest_cache`, etc.) from ever being committed.
- Wrote `docs/schema.json` (JSON Schema draft-07) and `docs/SCHEMA.md`
  (human-readable) for the row-level schema.
- Wrote `docs/raw_template.csv` (header-only) and `docs/FILLING_GUIDE.md`.
- Committed (`34a024d`) and pushed branch `practical2-run` to origin.

## 2026-09-28T11:58:00Z — Stage 2: ethics/collection/teamwork docs

- Wrote `docs/CONSENT_FORM.md` (English consent script, contact details and
  date left as `[FILL IN]`), `docs/COLLECTION_PROTOCOL.md` (what to
  collect/avoid, anonymous ID handling, translation guidance),
  `docs/ETHICS_CHECKLIST.md` (pre-release checklist), and
  `docs/TEAM_PLAN.md` (role/ID-range/timeline template with a
  CONTRIBUTIONS section). All four are marked as drafts at the top, per
  instructions, with placeholders for names/dates/ranges the authors must
  fill in.
- Committed (`5ee20c2`) and pushed.

## 2026-09-28T12:10:00Z — Stage 3: preprocessing script

- Wrote `scripts/common.py` (shared schema constants, boolean parsing,
  text-normalisation primitives, JSONL/CSV I/O) used by every later
  pipeline script, and `scripts/preprocess.py` (combine raw CSVs → NFC →
  invisible-char strip → whitespace cleanup → quote normalisation → id
  assignment → exact-dup removal → near-dup flagging → per-language
  summary).
- Created synthetic test fixtures `tests/fixtures/raw_sample_author1.csv`
  and `raw_sample_author2.csv` (obviously-fake `TEST_LUG_TEXT_*` /
  `TEST_YOR_TEXT_*` / `TEST_EN_TRANSLATION_*` strings) covering: an
  NFC-decomposed vs. composed character, curly quotes, a zero-width space,
  irregular whitespace, an exact duplicate, a near-duplicate, a missing
  translation, fake-PII-shaped text, an English-looking Yoruba-labelled
  entry, a translation identical to its source, a very short entry, and a
  cross-file `id` conflict with differing text.
- Smoke-tested `preprocess.py` against these fixtures in `/tmp/pp_smoke`
  (outside the repo, never touching `data/`): 15 combined rows → 1 id
  conflict correctly reported and the losing row dropped, 1 exact
  duplicate removed, 1 NFC change / 1 invisible-char change / 1 whitespace
  change / 1 quote change all correctly attributed to Luganda, final 14
  entries written to a scratch `dataset.jsonl`. Output verified by eye
  (curly quotes → straight, zero-width space removed with no meaning
  change, decomposed café → composed). Near-duplicate detection code path
  did not trigger on this particular fixture pair (ratio fell just under
  the 0.90 threshold) — dedicated pytest coverage for that threshold is
  added in Stage 4e with a tighter-controlled pair. No files under
  `data/raw/` were touched; smoke-test output was in `/tmp`, not `reports/`
  or `data/processed/`, and was discarded after inspection.
- Committed (`7a17210`) and pushed.

## 2026-09-28T12:35:00Z — Stage 4a: validate_auto.py

- Wrote `scripts/validate_auto.py`: schema/required-field checks, empty/
  very-short-text, within- and cross-language duplicate detection, per-
  language length outliers (3-sigma rule), per-language rare-character
  flags (dataset's own char distribution), PII-shaped-text detection
  (email/URL/@handle/Ugandan+Nigerian+generic-international phone
  patterns/long digit runs/capitalised-token hint), region-spelling
  consistency (difflib similarity), a heuristic language-label sanity
  check (common-English-stopword fraction + per-language character-profile
  comparison), Yoruba tone-mark-vs-subdot mixed-style + non-NFC detection,
  and translation sanity (empty / identical-to-source / length-ratio
  outlier). Writes `reports/validation.md` (per-language pass/fail table,
  an explicit machine-checkable PII PASS/FAIL line for
  `build_release.py` to gate on, and a written-out Limitations section)
  and `reports/flags.csv`.
- Ran it against the Stage-3 smoke-test output
  (`/tmp/pp_smoke2/out/dataset.jsonl`, 14 synthetic entries): 26 flags
  across 8 check types, including the deliberately-planted missing
  translation, identical-translation, fake-PII strings, and the malformed
  fixture id, all correctly caught. `rare_character` fired very often on
  this fixture set specifically because the synthetic `TEST_LUG_TEXT_00N`
  markers embed digits/ASCII tokens that aren't representative of real
  Luganda/Yoruba text — expected fixture noise, not a script bug; real
  collected data won't carry that prefix. Output discarded after
  inspection (was in `/tmp`, not `reports/`).
- Committed (`3576880`) and pushed.

## 2026-09-28T12:55:00Z — Stage 4b: make_review_sheet.py

- Wrote `scripts/make_review_sheet.py`: Layer 1 (per-language, all flagged
  + reproducible seed-42 random sample of ≥max(20%, 50)) and Layer 2
  (cross-author, English-side-only review, default author assignment =
  language split unless `--contributor-map` is given, plus a shared
  reproducible overlap set drawn from both languages for agreement
  measurement). Writes CSV sheets with the exact required columns plus a
  `.NOTE.md` per sheet carrying the mandatory Layer 2
  "does-not-verify-target-language-correctness" caveat, and a
  `reports/review/README.md` overview.
- Smoke-tested against the Stage 3/4a fixture output: Layer 1 produced 9/9
  Luganda and 5/5 Yoruba rows (small fixture, so the ≥50 floor pulled in
  the whole language each time — expected at this scale); Layer 2 produced
  7 entries for author1's sheet and 10 for author2's, with a 3-entry
  overlap set present in both. Ran the script twice with identical inputs
  and diffed the output directories — byte-identical, confirming seed-42
  reproducibility. Output was in `/tmp`, discarded after inspection.
- Committed (`5b56c08`) and pushed.

## 2026-09-28T13:10:00Z — Stage 4c: compute_agreement.py

- Wrote `scripts/compute_agreement.py`: loads two completed Layer 2
  sheets, intersects their ids (the overlap set), computes percent
  agreement and Cohen's kappa (stdlib only, `collections.Counter`-based)
  over ids completed by both reviewers, lists disagreements, and reports
  ids not yet completed by both separately (not treated as
  disagreements). Report states explicitly that this is English-side
  agreement, not target-language-correctness agreement.
- Smoke-tested by hand-filling verdicts into the Stage 4b sample sheets
  (a mix of matching and one deliberately-attempted mismatch, plus one
  left incomplete): correctly identified the real 3-id overlap set
  (`id-conflict-001`, `lug-0001`, `yor-0002` — not the ids this assistant
  initially guessed, which was a useful check that the script's own
  overlap-set logic, not assumption, is authoritative), computed 100%
  agreement / kappa 1.0 on the 2 ids both reviewers had completed, and
  correctly reported the 3rd (`yor-0002`) as incomplete rather than a
  disagreement. Output discarded after inspection.
- Committed (`b5d73ee`) and pushed.

## 2026-09-28T13:25:00Z — Stage 4d: apply_corrections.py

- Wrote `scripts/apply_corrections.py`: parses the `field: value` mini-
  syntax in `reviewer_correction` (D020), applies non-conflicting
  corrections to a new `data/processed/dataset_corrected.jsonl` (original
  `dataset.jsonl` never modified, D021), logs every applied change to
  `reports/corrections_log.csv` (id, language, field, before, after,
  reviewer, layer), and routes to `reports/conflicts.csv` both (a) any
  Layer 2 correction that touches `text` (never auto-applied, always
  routed regardless of what Layer 1 does) and (b) any field where two
  sheets propose different values. Updates `reviewed` /
  `reviewed_by_independent` / `reviewer_id` per D022.
- Smoke-tested against the Stage 4b/4c sample sheets with hand-added
  corrections covering all four paths: a Layer 1 translation fix (lug-0001,
  applied), a Layer 1 text fix (lug-0002, applied — Layer 1 is allowed to
  correct text), a Layer 2 attempt to correct `text` (yor-0002 — correctly
  blocked and routed to conflicts.csv, NOT applied to the dataset), two
  Layer 2 sheets proposing different `region` corrections for the same
  overlap entry lug-0001 (correctly routed to conflicts.csv, neither
  applied), and a Layer 2 translation fill-in for a previously-empty
  translation (lug-0008, applied). Verified by reading the output JSONL
  and both report CSVs by eye — all four paths behaved exactly as
  designed, including `reviewed`/`reviewed_by_independent`/`reviewer_id`
  being set correctly (R01 for Layer-1-reviewed lug entries,
  R03/R04 for Layer-2-only entries, `reviewed_by_independent` staying
  false for Layer-2-only entries). Output discarded after inspection.
