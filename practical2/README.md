# Practical 2: Data Preparation

Original bilingual (Rukiga + Yoruba) short-text dataset with English
translations: collection → preprocessing → validation → two-layer human
review → dataset card → release packaging.

> **This repo builds everything *around* the real data.** The two authors
> (Nabasa Amos and Jesulewami Kupoluyi) collect data by hand — with real
> contributors, consent, and their own credentials — or, as of 2026-09-29
> (see `DECISIONS.md` D026), source it by scraping openly-licensed
> websites with attribution, using `scripts/scrape_source.py`. Either way
> this pipeline never invents data, and never uploads anything (see
> `DEFINITION OF DONE` at the bottom and `LOG.md` for what was actually
> run and when).

## Layout

```
practical2/
├── README.md                  # this file
├── LOG.md                     # running log of what was done and when
├── DECISIONS.md               # decision record (schema, thresholds, etc.)
├── VIVA_NOTES.md               # anticipated viva questions, answered from DECISIONS.md
├── requirements.txt            # pytest only — the pipeline itself is stdlib
├── data/
│   ├── raw/                   # our hand-collected CSVs go here (never edited by scripts)
│   └── processed/             # dataset.jsonl / dataset_corrected.jsonl (pipeline output)
├── release/                   # final packaged dataset + dataset card (build_release.py output)
│   └── DATASET_CARD_TEMPLATE.md   # the only file checked in here; everything else is generated
├── reports/                   # validation.md, flags.csv, agreement.md, review/, etc. (all generated)
├── scripts/                   # the pipeline — see "Running the pipeline" below
├── tests/
│   ├── fixtures/              # synthetic, obviously-fake test data ONLY
│   └── test_*.py              # pytest suite (35 tests)
└── docs/
    ├── SCHEMA.md, schema.json         # row schema
    ├── raw_template.csv, FILLING_GUIDE.md
    ├── CONSENT_FORM.md, COLLECTION_PROTOCOL.md, ETHICS_CHECKLIST.md, TEAM_PLAN.md
    └── UPLOAD_GUIDE.md
```

`data/processed/`, `reports/`, and `release/` (other than the template)
are pipeline **output** — empty in this repo until you run the scripts
against real data. Nothing under `data/raw/` is ever written by a script.

## Setup

```bash
cd practical2
pip install -r requirements.txt   # only needed to run the test suite
python3 -m pytest tests/          # 35 tests, should all pass
```

## Running the pipeline, in order

Once both authors have collected data (see `docs/COLLECTION_PROTOCOL.md`
and `docs/FILLING_GUIDE.md`) and placed their CSV file(s) in
`data/raw/` (e.g. `data/raw/raw_cgg_author1.csv`,
`data/raw/raw_yor_author2.csv`; web-scraped entries go in separate
`data/raw/raw_<lang>_scraped.csv` files — see `scripts/scrape_source.py`):

```bash
# 1. Combine + clean raw CSVs -> data/processed/dataset.jsonl
python3 scripts/preprocess.py

# 2. Automated checks -> reports/validation.md, reports/flags.csv
python3 scripts/validate_auto.py

# 3. Build the two-layer review sheets -> reports/review/
python3 scripts/make_review_sheet.py
#   (optionally: --contributor-map /path/to/local/mapping.csv — never commit that file)

# --- human step: both reviewers fill in reviewer_verdict / reviewer_correction /
#     reviewer_notes in reports/review/*.csv (see reports/review/README.md
#     and each sheet's .NOTE.md for what's expected) ---

# 4. Agreement on the Layer 2 overlap set -> reports/agreement.md
python3 scripts/compute_agreement.py

# 5. Apply corrections -> data/processed/dataset_corrected.jsonl,
#    reports/corrections_log.csv, reports/conflicts.csv
python3 scripts/apply_corrections.py

# --- human step: resolve anything in reports/conflicts.csv, then
#     re-run step 5 after editing the review sheets if needed ---

# 6. Print real per-language numbers to paste into the dataset card
python3 scripts/fill_card_stats.py

# --- human step: copy release/DATASET_CARD_TEMPLATE.md to a working copy,
#     paste in the fill_card_stats.py numbers and everything else marked
#     [FILL IN], go through docs/ETHICS_CHECKLIST.md ---

# 7. Build the release (refuses to run until PII check passes, conflicts
#    are resolved, and the card has no [FILL IN] left)
python3 scripts/build_release.py --card path/to/your/filled_card.md

# --- human step: upload release/ by hand — see docs/UPLOAD_GUIDE.md.
#     scripts/upload_to_hf.py exists but must be run manually, never from
#     an unattended session, with HF_TOKEN set in your own shell. ---
```

Every script also takes `--help` / explicit path flags — see each
script's module docstring for details and defaults.

## What we (the authors) still have to do ourselves

This pipeline cannot do any of the following — they involve real people,
consent, and our own credentials:

- [ ] Recruit contributors, obtain and record consent (`docs/CONSENT_FORM.md`,
      `docs/COLLECTION_PROTOCOL.md`) — **Author 1: Rukiga, Author 2: Yoruba**
      (human collection); or source via approved web-scraping
      (`docs/COLLECTION_PROTOCOL.md`'s scraping note, `DECISIONS.md` D026)
- [ ] Actually collect ~150-250 entries per language (target, not a hard
      requirement — see `DECISIONS.md` D026/D027) and fill in the raw
      CSVs (`docs/FILLING_GUIDE.md`)
- [ ] Recruit an independent fluent-speaker reviewer per language (Layer 1)
      — see `docs/TEAM_PLAN.md`; if none is found, that's OK, but it must
      be stated honestly in the dataset card's limitations
- [ ] Complete the Layer 1 and Layer 2 review sheets by hand
- [ ] Discuss and resolve any disagreements (`reports/agreement.md`) and
      conflicts (`reports/conflicts.csv`)
- [ ] Fill in the dataset card with real facts (`release/DATASET_CARD_TEMPLATE.md`
      + `scripts/fill_card_stats.py` output) — never invent numbers
- [ ] Go through `docs/ETHICS_CHECKLIST.md` together before release
- [ ] Confirm the license (currently proposed: CC BY 4.0)
- [ ] Run the actual upload by hand (`docs/UPLOAD_GUIDE.md`), with our own
      Hugging Face account/organisation and token

## Design decisions and limitations

Every choice that could reasonably have gone another way — schema fields,
thresholds, how duplicates/PII/diacritics are handled, how review layers
work, defaults used where the assignment didn't specify something — is in
`DECISIONS.md`, written as the choices were made, including confidence
levels and what could go wrong. `reports/validation.md` (once generated)
has its own **Limitations** section on what the automated checks can and
can't actually tell you, since this pipeline is not fluent in either
language.

## Definition of done (for this pipeline-building work)

Layout and two-language schema documented; consent form, protocol, ethics
checklist and team plan drafted; preprocess, validate, review-sheet (both
layers), agreement, corrections, stats, build and upload scripts present
and tested on synthetic fixtures; dataset card template with only
placeholders for our facts and a mandatory review-coverage limitation;
`DECISIONS.md` and `VIVA_NOTES.md` complete; `LOG.md` complete;
`data/raw`, `data/processed`, `release/` and `reports/` contain no fake
data; no name-to-ID mapping file committed; everything pushed to branch
`practical2-run`. **Nothing uploaded anywhere.** See `LOG.md` for the
full end-to-end confirmation run.
