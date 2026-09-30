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
- Committed (`819eafe`) and pushed.

## 2026-09-28T13:45:00Z — Stage 4e: unit tests

- Wrote `tests/conftest.py` (adds `scripts/` to `sys.path`) and five test
  modules, all using only synthetic `TEST_*`/Unicode-escape data (no real
  Luganda/Yoruba/English, matching `tests/fixtures/README.md`):
  - `test_common.py` — NFC-normalises-decomposed-to-composed-without-
    changing-meaning (decomposed vs. precomposed café-style test),
    NFC-never-strips-combining-marks, invisible-char stripping vs.
    combining-mark preservation, quote normalisation (curly touched,
    phonemic modifier-apostrophe untouched), whitespace normalisation,
    boolean parsing (including the "flase"-typo anomaly path).
  - `test_preprocess.py` — id assignment (sequential + collision
    avoidance), exact-duplicate removal, near-duplicate flagging
    (similar-but-not-identical is flagged, very-different is not),
    quote/whitespace normalisation logging, cross-file id-conflict
    detection (using the real `tests/fixtures/raw_sample_author*.csv`
    files), and a full end-to-end run of `preprocess.main()` against the
    fixtures directory into a pytest `tmp_path`.
  - `test_validate.py` — required-field/schema checks, empty/very-short
    text, within- and cross-language duplicates, PII patterns (email,
    Ugandan phone, Nigerian phone), translation sanity (empty/identical/
    ratio outlier), length outliers, and the non-NFC diacritic check.
  - `test_agreement.py` — Cohen's kappa: perfect agreement = 1.0,
    chance-level agreement = 0.0 (hand-verified against the formula),
    single-category-all-agree = 1.0, empty input = None.
  - `test_corrections.py` — the `field: value` mini-syntax parser, and
    three full `apply_corrections.main()` integration cases in
    `tmp_path`: a Layer 2 text correction is blocked and routed to
    conflicts (never applied), two conflicting Layer 2 metadata
    corrections are routed to conflicts (neither applied), and a Layer 1
    text correction IS applied and correctly sets
    `reviewed`/`reviewed_by_independent`/`reviewer_id`.
- Added `requirements.txt` (pytest only — the pipeline itself is stdlib).
- Ran `python3 -m pytest tests/ -v`: 35 tests, **1 initial failure**
  (`test_normalise_whitespace_trims_and_collapses` — the test's own
  expected string was wrong: it expected a leading space to survive after
  a line break, but `normalise_whitespace` correctly strips each line
  individually, which is the intended behaviour per Stage 3's spec
  ("trim, collapse runs of spaces, normalise line breaks"); fixed the test
  expectation, not the implementation). Re-ran: **35/35 passed.**
- Committed (`042893f`) and pushed.

## 2026-09-28T14:05:00Z — Stage 5: dataset card and release packaging

- Wrote `release/DATASET_CARD_TEMPLATE.md` (HF dataset-card YAML front
  matter + all required sections; every real fact about our data is a
  `[FILL IN]` placeholder, mandatory review-coverage and small-sample
  limitations included as required text).
- Wrote `scripts/fill_card_stats.py` (prints per-language entry count,
  length stats, unique tokens, diacritic-mark share, field completeness,
  contributor count, reviewed/independently-reviewed share — prefers
  `dataset_corrected.jsonl`, falls back to `dataset.jsonl`).
- Wrote `scripts/build_release.py` (refuses to run on PII-check FAIL/
  missing, unresolved `reports/conflicts.csv` rows, or any `[FILL IN`
  left in the card; on success assembles combined + per-language
  `release/{lug,yor}/` files, copies the card to `release/README.md`,
  and writes a `release/LICENSE` notice marked proposed).
- Wrote `scripts/upload_to_hf.py` (huggingface_hub-based, reads
  `HF_TOKEN` from the environment only, refuses without it; loud
  "do not run this unattended" docstring) and `docs/UPLOAD_GUIDE.md`
  (Hugging Face primary steps incl. org/collaborator setup, plus
  alternative steps for GitHub Releases, Zenodo, and Kaggle). **Per the
  task brief, `upload_to_hf.py` was never executed** — only syntax-checked
  (`python3 -m py_compile`).
- Smoke-tested `fill_card_stats.py` against the Stage 4 corrected fixture
  dataset — output looked sane (counts, length stats, review-share
  percentages all matched the fixture's known composition).
- Smoke-tested `build_release.py`'s three refusal gates independently: (1)
  missing `validation.md` → refused; (2) `validation.md` present but PII
  check FAIL (the real Stage 4a fixture output, which has 3 planted PII
  flags) → refused; unresolved `conflicts.csv` rows from the Stage 4d
  smoke test and the unfilled real `DATASET_CARD_TEMPLATE.md` were
  correctly flagged simultaneously in both runs (all three checks run
  before failing, not just the first). Then tested the success path with
  a synthetic PASS validation report, an empty conflicts file, and a copy
  of the card with placeholders replaced by obviously-fake filler text —
  build succeeded, producing the expected `release/` layout (combined +
  per-language jsonl/csv, README.md, LICENSE). All smoke-test output was
  in `/tmp`, discarded after inspection; nothing was written to the
  repo's real `release/` directory during testing.
- Committed (`8c814cf`) and pushed.

## 2026-09-28T14:20:00Z — Stage 6: hand-off — full end-to-end run and final docs

- Ran the complete pipeline, in order, against the real default paths
  (`data/raw`, `data/processed`, `reports/`), using ONLY the synthetic
  fixtures (`tests/fixtures/raw_sample_author1.csv`,
  `raw_sample_author2.csv`) as `--raw-dir` input to `preprocess.py`:
  1. `preprocess.py --raw-dir tests/fixtures` → 14 entries.
  2. `validate_auto.py` → 26 flags, 3 PII flags (PII check: FAIL, as
     expected — the fixtures deliberately contain fake PII strings).
  3. `make_review_sheet.py` → Layer 1 (9 lug / 5 yor), Layer 2 (7 / 10),
     3-entry overlap set (`lug-0001`, `id-conflict-001`, `yor-0002`).
  4. Hand-filled all four review sheets with verdicts/corrections,
     including one deliberate Layer 1↔Layer 2 disagreement (`yor-0002`:
     Layer 2 author1 says `needs_correction`, author2 says `ok`) and one
     deliberate improper Layer 2 text-field correction attempt.
  5. `compute_agreement.py` → overlap 3/3 completed, 66.7% agreement,
     Cohen's kappa 0.400 ("fair"), 1 disagreement listed (`yor-0002`) —
     matches the deliberately-planted disagreement exactly.
  6. `apply_corrections.py` → 3 corrections applied, 1 conflict
     (the planted improper Layer 2 text edit on `yor-0002`, correctly
     blocked and routed to `reports/conflicts.csv`, not applied).
  7. `fill_card_stats.py` → sane per-language numbers matching the known
     fixture composition (9 lug / 5 yor, review shares reflecting exactly
     which sheets were filled in).
  8. `build_release.py` (real card, real reports) → **correctly refused**,
     citing all three gates simultaneously: PII check FAIL, 1 unresolved
     conflict, 20 `[FILL IN]` placeholders remaining in the real,
     never-filled `release/DATASET_CARD_TEMPLATE.md`. This is the correct
     and expected outcome for this dry run — Stage 5's own smoke test
     (see above) already separately confirmed the success path works when
     given a genuinely clean, filled card and passing reports.
  - Re-ran `python3 -m pytest tests/ -q`: **35/35 passed.**
- **Cleanup:** deleted every file `preprocess.py`/`validate_auto.py`/
  `make_review_sheet.py`/`compute_agreement.py`/`apply_corrections.py`/
  `fill_card_stats.py` wrote under `data/processed/` and `reports/`
  during this run, restored empty `.gitkeep` placeholders in both, and
  confirmed via `git status` that nothing new was left staged or
  untracked (these directories are exactly as they were after Stage 1,
  since all pipeline output there is gitignored-equivalent by convention
  — nothing under `data/processed/` or `reports/` is meant to be
  committed as part of this pipeline-building work). `release/` was
  never written to by this run (build_release.py refused before writing
  anything) and still contains only the checked-in
  `DATASET_CARD_TEMPLATE.md`. Confirmed no fixture data remains in
  `data/`, `release/`, or `reports/`.
- Wrote the final `README.md` (full layout, setup, the exact
  ordered pipeline commands demonstrated above, and an explicit checklist
  of what the two authors must still do by hand) and `VIVA_NOTES.md`
  (anticipated questions, each answered only from `DECISIONS.md` and the
  docs already in this repo, with "default/not sure" stated honestly
  where that's the true answer — e.g. the review-verdict vocabulary and
  the author-assignment default are both flagged as this pipeline's own
  conventions, not requirements from the assignment brief).

## 2026-09-29 — Stage 8: scope change (web-scraping) + language change (Luganda → Rukiga)

- Received a new authoritative instruction (attachment) permitting
  web-scraping from openly-licensed sites as an alternative to human
  collection (lecturer-approved), and changing Author 1's language from
  Luganda to Rukiga (`cgg`) — Author 1 is a native Rukiga speaker. Both
  changes recorded in `DECISIONS.md` D026/D027, explicitly additive to
  Stages 1-6, not a restart.
- Updated `scripts/common.py`: `LANGUAGES`/`LANGUAGE_NAMES` lug→cgg,
  `ALL_FIELDS` extended with `source_url`, `site_name`, `retrieved_date`,
  `source_license`, `translation_source`; added `WEB_SCRAPE_REQUIRED_FIELDS`,
  `TRANSLATION_SOURCES`, `CONTRIBUTOR_ID_NA`; `SOURCE_TYPES` extended with
  `"web-scraped"`.
- Updated `scripts/validate_auto.py`'s `check_schema_and_required` to be
  conditional on `source_type`: web-scraped rows require the 5 new
  fields and do not get flagged for missing `contributor_id`;
  human-collected rows are unchanged (still require `contributor_id`).
  `translation_source` validated against its enum when present.
- Swept Luganda/lug → Rukiga/cgg across `scripts/*.py`, `tests/*.py`,
  `tests/fixtures/*`, and `docs/*.md` (including `schema.json`,
  `raw_template.csv`). Historical entries already in `LOG.md` and
  `DECISIONS.md` from earlier stages were deliberately left unchanged —
  they are append-only records of what was true at the time, not living
  documentation.
- Two-pass grep used to avoid missing references: a word-boundary pass
  (`\blug\b`) followed by a broader substring pass, which caught one bug
  the first pass missed — `scripts/apply_corrections.py` had a hardcoded
  `layer1_lug` sheet name (no word boundary between `_` and `lug`) that
  would have silently broken Layer 1 review lookups for `cgg`. Fixed by
  deriving the `sheets` dict from `common.LANGUAGES` dynamically instead
  of hardcoding language codes, which also future-proofs against this
  class of bug recurring.
- Deliberately did NOT fabricate an example Rukiga sentence in
  `docs/FILLING_GUIDE.md` (it previously had an invented Luganda
  example) — replaced with a note explaining why no example is given,
  consistent with this project's data-integrity stance even for
  documentation.
- Updated `release/DATASET_CARD_TEMPLATE.md`: language list, fields
  table (added the 5 new fields + contributor_id N/A note), split "How
  the data was collected" into human-collection and web-scraping
  methods, added a new "Sources and credits (web-scraped entries)"
  `[FILL IN]` scaffold subsection, rewrote "Consent and ethics" to
  distinguish consent-based (human) from attribution/license-based
  (scraped) provenance, and swept remaining Luganda mentions.
- Updated `README.md` and `VIVA_NOTES.md` (living docs) for the language
  change and to mention the web-scraping path; `DECISIONS.md`/`LOG.md`
  entries from earlier stages left untouched as historical record.
- Re-ran `python3 -m pytest tests/ -q`: all 35 tests pass after the
  rename and schema-logic changes (3 failures during the rename were
  fixed along the way — two were fixture literals needing `lug`→`cgg`,
  one was the `apply_corrections.py` sheets-dict bug above).
- Next: Stage 9 — investigate africanstorybook.org's access method
  (JSON/API vs. JS-rendering) before writing any scraper code, per the
  new instruction's technical caveat.

## 2026-09-29 — Stage 9: technical investigation, volume estimate, self-check gate — BLOCKED

Per the brief: investigate real data-access method for each approved
source BEFORE building a scraper, do a volume estimate, then build
`scripts/scrape_source.py`, run a 15-entries/language small batch through
`validate_auto.py`, and only auto-continue to the full target if it
passes cleanly. Findings below explain why this run stops at the small-
batch gate rather than continuing, per Stage 9's own instruction ("If any
check fails... STOP, do not scale up... write BLOCKED.md").

### Investigation: `global-asp/storybooks-uganda`

Cloned the public repo directly (`git clone --depth 1
https://github.com/global-asp/storybooks-uganda`) rather than fetching
the live site, since it is a static GitHub Pages site and the repo itself
is the ground truth. Findings:

- **Static HTML, not JS-rendered.** Story pages
  (`stories/<langcode>/<id>/index.html`) contain the local-language text,
  English, and Swahili directly in the HTML (`<div class="... def">`,
  `<div class="... l1">`, `<div class="... l2">` respectively), with a
  per-story human translator credited (e.g. "Translated by Julius
  Tusiime" on `stories/nyn/0327/index.html`). No browser or JS execution
  needed to read a story once you have its path.
- **No Rukiga content exists on this site.** The directory listing under
  `stories/` has no `cgg`/`kiga` folder. `about/languages/index.html`
  explicitly lists "Rukiga" among languages the project *hopes* to cover,
  with **no link** next to it (unlike "Runyankore", which does have a
  linked `stories/nyn/` folder) — the page states outright: "Please note
  that some translations and recordings are not yet complete... We are
  always looking for translators!" Runyankore (`nyn`) is a closely
  related but ISO-639-3-distinct language (`nyn` vs. Rukiga's `cgg`) and
  was NOT substituted for Rukiga, per the brief's explicit "do NOT
  substitute another language" rule — Runyankore content was used only
  to verify the *parser* works correctly against real markup (see below),
  never harvested into `data/raw/`.
- **No Yoruba content exists on this site** — it is a Uganda-specific
  project (confirmed: no `yor` directory, no mention of Yoruba anywhere
  in the repo).
- **Net result: this source contributes 0 entries for both target
  languages**, despite being named PRIMARY for both in the brief. This
  is disclosed here rather than worked around.
- The scraper's HTML-parsing logic (`scripts/scrape_source.py`'s
  `_parse_storybooks_uganda_story`) was still verified end-to-end against
  this real, checked-out site by temporarily pointing it at the `nyn`
  (Runyankore) directory, which does have real content: it correctly
  extracted the exact local-language/English text pairs verbatim,
  matching the raw HTML byte-for-byte (e.g. "Enjojo emwe neza kunywa
  ameizi." / "One elephant is going to drink water." from
  `stories/nyn/0327/`). This confirms the parser itself is sound; the
  blocker is purely lack of Rukiga/Yoruba content on this specific site,
  not a scraping-technique problem. This test output was never written
  to `data/raw/` (Runyankore is not an approved language for this
  project).

### Investigation: `www.africanstorybook.org`

- `robots.txt` is effectively open (`User-agent: *` with no Disallow
  rules), and the homepage claims "260 Languages, ~5470 Storybooks."
- **The book catalogue needs a JS-executing browser.** Individual story
  pages (`reader.php?id=<id>`) redirect to a JS viewer
  (`newviewer/index.php?id=<id>...`) and the site's own catalogue-listing
  variables (`bookItemsAppr`, `languages`) are populated by client-side
  JavaScript after page load, not present in the static HTML or in any
  discoverable JSON/API endpoint. This was confirmed conclusively by
  reading the source of a real, working third-party scraper for this
  exact site — `learningequality/sushi-chef-african-storybook` (public
  GitHub repo, cloned to inspect `chef.py`) — which uses `pyppeteer`
  (headless Chrome) specifically to run
  `driver.execute_script("return bookItemsAppr;")` and
  `driver.execute_script("return languages;")` to get the catalogue.
- **Individual books ARE downloadable without a browser once you know
  the book id**: `GET /makeapp/data/landscape.php?id=<id>` returns a
  static EPUB file (confirmed in the same third-party scraper's code,
  `download_epub_book()`), which is just a zip of XHTML pages — normal
  parsing, no JS needed for that step.
- **Rukiga-specific volume could not be checked.** Without either a
  headless browser or a hand-collected list of Rukiga book ids (both
  require actually browsing the live site's language filter), there was
  no way to determine how many genuine Rukiga stories exist here, if any.

### Investigation: `yo.wikipedia.org` REST API

Per the brief: REST API only (`/api/rest_v1/`), never HTML crawling,
descriptive User-Agent required — `scripts/scrape_source.py` implements
exactly this (`YOWIKI_API_BASE`, `USER_AGENT` constant naming the project
and a contact email) and reuses the pipeline's own PII regexes to filter
extracted sentences before they're kept, matching the same discipline as
every other source in this script.

### The actual blocker: this session's own network sandbox

None of the three approved sources' live sites could be reached from
shell-level code in this assistant's sandboxed session — confirmed via
direct `curl` attempts (`africanstorybook.org`, `global-asp.github.io`,
`yo.wikipedia.org` all returned `CONNECT tunnel failed, response 403`)
and the sandbox's own proxy documentation, which states plainly: "The
destination host is not allowed by your organization's egress policy for
this session. Do not retry or route around it — report the blocked
host." Only two kinds of hosts are reachable from shell code here:
GitHub (used above, via `git clone`, for the two public repos inspected)
and language package registries (pypi/npm) — not general websites.

The `WebFetch` tool (a separate, non-shell tool available in this
session) CAN reach these sites, so it was used throughout this
investigation for research (reading `robots.txt`, page structure,
language lists). But it was also tested directly against ground truth
for exact-text fidelity, since verbatim text is what a linguistic
dataset actually needs: asked to quote the exact text of
`stories/nyn/0327/`'s `id="text02"` element, it returned the text from a
*different* element (`id="text03"`, "Entureje ibiiri..." instead of the
correct "Enjojo emwe...") — confirmed wrong against the same page's real
HTML (read via the git checkout). `WebFetch` runs page content through a
summarization model before returning it, which is appropriate for
research questions but not safe for collecting exact source text, so it
was not used to harvest any dataset entries, per this project's
DATA SAFETY RULES/data-integrity stance (no pipeline step is allowed to
silently alter or mis-transcribe target-language text).

### Volume estimate

Given the above: `global-asp/storybooks-uganda` = 0 for both languages
(confirmed, content doesn't exist). `africanstorybook.org` and
`yo.wikipedia.org` = **could not be estimated**, since estimating
requires actually browsing/querying the live sites, which this session
cannot do at the shell/script level, and cannot do reliably at all via
`WebFetch` (fidelity issue above). No volume estimate below 50 is being
reported here as a "disclosed low count" — the honest status is that the
volume is **unknown**, not low, because the check itself couldn't run.

### Self-check gate outcome: BLOCKED

Per Stage 9's instruction, this is treated as a failed self-check gate:
no small batch could be produced or validated for either language from
any approved source, so this run does **not** scale up and does **not**
attempt a workaround (no proxy bypass, no alternate/unapproved source,
no substituting Runyankore for Rukiga). See `practical2/BLOCKED.md` for
the explanation written for the authors, with the concrete example
above. `scripts/scrape_source.py` is still written and committed — its
storybooks-uganda path was verified end-to-end against real data (module
docstring explains exactly what was and wasn't verified); its
africanstorybook.org and yo.wikipedia.org paths are implemented per each
source's documented/verified access pattern but were never executed
against live data, and are clearly marked as such for an author running
this on a machine with normal (unrestricted) internet access.

This does not affect Stages 1-6 (the human-collection pipeline), which
remains fully built, tested, and unaffected by this blocker.
