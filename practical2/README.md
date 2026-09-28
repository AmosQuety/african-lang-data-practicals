# Practical 2: Data Preparation

Original bilingual (Luganda + Yoruba) short-text dataset with English
translations: collection → preprocessing → validation → two-layer human
review → dataset card → release packaging.

> **Status: pipeline scaffold.** This repo builds everything *around* the
> real data. The two authors collect data by hand (with real contributors,
> consent, and their own credentials) and do the final upload themselves —
> this pipeline never invents, scrapes or generates data, and never
> uploads anything.

## Layout

```
practical2/
├── README.md                  # this file
├── LOG.md                     # running log of what was done and when
├── DECISIONS.md               # decision record (schema, thresholds, etc.)
├── VIVA_NOTES.md               # anticipated viva questions, answered from DECISIONS.md
├── BLOCKED.md                  # only created if something can't proceed at all
├── data/
│   ├── raw/                   # our hand-collected CSVs go here (never edited by scripts)
│   └── processed/             # dataset.jsonl produced by preprocess.py
├── release/                   # final packaged dataset + dataset card (build_release.py output)
├── reports/                   # validation.md, flags.csv, agreement.md, etc.
├── scripts/                   # the pipeline (see "Running the pipeline" below)
├── tests/
│   └── fixtures/              # synthetic, obviously-fake test data ONLY
└── docs/
    ├── SCHEMA.md, schema.json # row schema
    ├── raw_template.csv, FILLING_GUIDE.md
    ├── CONSENT_FORM.md, COLLECTION_PROTOCOL.md, ETHICS_CHECKLIST.md, TEAM_PLAN.md
    └── UPLOAD_GUIDE.md
```

Full stage-by-stage instructions, requirements, and a checklist of what the
authors must still do by hand are filled in as each stage of the pipeline
is completed (see `LOG.md` for progress).
