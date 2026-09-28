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
