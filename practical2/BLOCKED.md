# BLOCKED — Stage 9 (web-scraping) could not produce a passing small batch

**Status as of 2026-09-29: stopped here, as instructed, rather than
scaling up or working around this.** Nothing below affects Stages 1-6
(the human-collection pipeline: schema, ethics docs, preprocessing,
validation, two-layer review, dataset card template) — that work is
complete, tested (35/35 tests passing), and ready to use exactly as
before. This file is about the *new* web-scraping path only
(DECISIONS.md D026).

## What was supposed to happen

Per the Stage 9 instruction: investigate each approved source's real
access method, estimate volume, build `scripts/scrape_source.py`, run a
15-entries-per-language small batch through `validate_auto.py`, and
auto-continue to the full ~150-250/language target only if it passes
schema validation, has zero PII flags, and has a non-empty
`translation_en` on every row. If any check fails: stop, write this
file, do not scale up, do not attempt workarounds or alternate sources.

## What actually happened

The small batch could not be produced at all, for either language, from
any of the three pre-approved sources. Full investigation detail is in
`LOG.md`'s "Stage 9" entry; the short version:

1. **`global-asp/storybooks-uganda`** (approved PRIMARY for both
   languages) — cloned the real repo and inspected it directly. It has
   **zero Rukiga content** (Rukiga is listed on the site's own "languages
   we hope to cover" page with no story link — "some translations...are
   not yet complete") and **zero Yoruba content** (it is a Uganda-only
   project; Yoruba was never in its scope). This is true regardless of
   any access-method question — the content simply isn't there yet.

   Example: `about/languages/index.html` lists `<li>Rukiga</li>` as
   plain text (no link), right next to `<li><a href="/storybooks-uganda/
   stories/nyn/">Runyankore</a></li>` (which does have a link/content).
   Rukiga and Runyankore are related but distinct languages
   (ISO 639-3 `cgg` vs. `nyn`) — Runyankore content was **not**
   substituted for Rukiga, per the brief's explicit instruction not to
   substitute another language.

2. **`www.africanstorybook.org`** (approved PRIMARY, fallback for both
   languages) — its book catalogue is populated by client-side
   JavaScript (confirmed by reading the source of a real, working
   third-party scraper for this exact site,
   `learningequality/sushi-chef-african-storybook`, which uses a headless
   browser for exactly this reason). This assistant's sandboxed session
   cannot reach `www.africanstorybook.org` at all from shell-level code
   — direct connection attempts returned `403` from the session's own
   network egress policy, which only allows GitHub and package
   registries, not general websites. Individual books ARE downloadable
   as static EPUBs once you know a book id
   (`makeapp/data/landscape.php?id=<id>`), but discovering *which* ids
   are Rukiga or Yoruba requires browsing the live site's language
   filter, which — again — this session cannot do.

3. **`yo.wikipedia.org` REST API** (approved BACKUP for Yoruba only) —
   also unreachable from this session's shell-level code, same egress
   policy (`403` on connection).

4. **The one tool in this session that CAN reach these sites
   (`WebFetch`) was tested against known ground truth and found
   unreliable for exact text.** Asked to quote the verbatim content of a
   specific, known HTML element on a real `storybooks-uganda` page
   (`stories/nyn/0327/`, element `id="text02"`), it returned the text
   from a *different* element (`id="text03"`) instead — confirmed wrong
   by comparing against the actual page HTML (read via a direct git
   checkout of the same page). For a linguistic dataset, where the exact
   source text matters and this pipeline's whole design principle is
   "never let an unqualified/automated step alter or mis-transcribe
   language text" (see `DECISIONS.md` D005/D009 on never auto-correcting
   diacritics, and the general DATA SAFETY RULES), this was judged unsafe
   to use for collecting actual dataset entries. It remained fine, and
   was used, for the *research* in this investigation (reading
   `robots.txt`, page structure, language lists) — just not for
   harvesting text into `data/raw/`.

**Net effect:** no entries could be scraped, verified, or written to
`data/raw/raw_cgg_scraped.csv` or `data/raw/raw_yor_scraped.csv` in this
session. Both files are simply absent — not present with placeholder or
partial data.

## What's still delivered

- `scripts/scrape_source.py` is written and committed. Its
  `storybooks-uganda` code path was verified end-to-end against real,
  checked-out site data (by pointing it at Runyankore content
  temporarily, to confirm the HTML parsing itself is correct — that test
  output was discarded, never written to `data/raw/`, since Runyankore
  isn't an approved language). Its `africanstorybook.org` and
  `yo.wikipedia.org` code paths are implemented against each source's
  documented/verified request pattern (robots.txt, REST API shape, the
  EPUB download URL confirmed via the third-party scraper's source) but
  were **never run against live data** in this session, because that
  session cannot reach those hosts. The module's own docstring repeats
  this plainly so nobody mistakes "implemented" for "verified working."
- Everything else from Stage 8 (schema/docs update for the web-scraping
  fields and the language change) is complete, committed, and unaffected
  — see `DECISIONS.md` D026/D027 and the Stage 8 `LOG.md` entry.

## What an author needs to do to actually get scraped data

Run `scripts/scrape_source.py` yourself, from a machine with normal
(unrestricted) internet access — not from this sandboxed session:

1. **For africanstorybook.org:** browse the site's language filter for
   Rukiga and for Yoruba by hand (or add a headless-browser catalogue
   step — `selenium`/`pyppeteer` — to `discover_book_ids()`), collect the
   real story ids into a text file, and pass it as `--book-ids-file`.
   Before trusting any output: inspect one real downloaded EPUB's
   internal structure yourself first — `scrape_africanstorybook()`
   currently raises `NotImplementedError` at the point where a
   downloaded EPUB's paragraphs would need to be split by language,
   because that structure could not be verified without network access
   in this session, and guessing at it risked mixing English and target-
   language text together silently. Fill that part in once you can see a
   real EPUB.
2. **For yo.wikipedia.org:** collect a list of Yoruba Wikipedia article
   titles, pass them via `--yowiki-titles-file`, and wire up a real
   machine-translation backend in `translate()` (currently a stub that
   raises `NotImplementedError` — this pipeline deliberately ships no MT
   backend, since choosing one is a decision an author should make
   explicitly, not something to bundle silently).
3. Run the small-batch gate exactly as Stage 9 describes (15/language,
   or all available if fewer, through `scripts/validate_auto.py`) before
   scaling up — the same discipline this run tried to follow, just from
   an environment that can actually reach the sources.
4. **If Rukiga volume still comes up short** even once africanstorybook.org
   is reachable (this is plausible — `storybooks-uganda` already showed
   Rukiga is one of the less-covered languages on the broader ASB
   project too), the brief is explicit: do not substitute another
   language, disclose the real number honestly in the dataset card and
   `LOG.md`/`VIVA_NOTES.md`, same as would apply to a human-collection
   shortfall.

## What this does NOT block

- The consented human-collection path (Stages 1-6) is complete and ready
  to use right now, for both Rukiga and Yoruba, independent of any of the
  above.
- `release/DATASET_CARD_TEMPLATE.md` already documents both sourcing
  methods and has a "Sources and credits (web-scraped entries)" section
  ready to fill in once real scraped data exists.
