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
