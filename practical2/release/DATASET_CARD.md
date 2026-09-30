---
language:
  - cgg
  - yor
license: cc-by-4.0
multilinguality: multilingual
task_categories:
  - translation
  - text-generation
pretty_name: "Rukiga-Yoruba Short Text and Proverbs Dataset"
size_categories:
  - n<1K
---

# Dataset Card for Rukiga-Yoruba Short Text and Proverbs Dataset

## Dataset summary

This dataset pairs short original Rukiga (`cgg`) and Yoruba (`yor`) text —
everyday sentences, greetings, a market/introduction dialogue, and proverbs —
with English translations. It was created for a university data-curation
course assignment (Practical II: End-to-End Data Curation), by two student
authors each writing content in a language they speak natively. 78 entries
total: 63 Rukiga, 15 Yoruba.

## Languages and dialects

- **Rukiga** (`cgg`) — 63 entries. Region/dialect were not recorded per
  entry; the collector and the independent reviewer are both native Rukiga
  speakers, and no specific sub-dialect was distinguished during collection.
- **Yoruba** (`yor`) — 15 entries. Region/dialect were not recorded per
  entry.

English (`en`) translations accompany every entry (`translation_en`),
required for all rows.

## Dataset structure and fields

One row per entry. Full schema: `practical2/docs/SCHEMA.md` /
`practical2/docs/schema.json`. Summary:

| Field | Description |
|---|---|
| `id` | Unique entry id, e.g. `cgg-0001` |
| `language` | ISO 639-3 code: `cgg` or `yor` |
| `text` | Original-language text |
| `translation_en` | English translation (required) |
| `contributor_id` | Anonymous contributor code, never a real name (`N/A` for web-scraped entries — see below) |
| `region` | Region/locality (optional) |
| `dialect` | Dialect (optional) |
| `date_collected` | `YYYY-MM` (optional, human-collected entries) |
| `source_type` | `self-written` / `volunteer-contributed` / `proverb` / `other` / `web-scraped` |
| `domain` | Topic tag (optional) |
| `reviewed` | Whether any review layer looked at this entry |
| `reviewer_id` | Anonymous reviewer code, or blank |
| `reviewed_by_independent` | True only if reviewed by a fluent speaker who did NOT collect the entry |
| `source_url`, `site_name`, `retrieved_date`, `source_license`, `translation_source` | Required for `source_type=web-scraped`: exactly where the entry came from, when it was fetched, its license, and whether the English translation is the source site's own (`site`) or machine-translated (`machine`) |

Two per-language configs (`cgg`, `yor`) plus a combined view are provided
— see `docs/UPLOAD_GUIDE.md` for how these map to Hugging Face configs.

## How the data was collected

1. **Consented human collection (the only method actually used in this
   release).** All 78 entries are `self-written`/`proverb` — written
   directly by the two student authors, each a native or fluent speaker of
   their language (Rukiga / Yoruba respectively), in September 2026.
   Rukiga entries: a market-dialogue script, five short everyday-topic
   paragraphs (morning routine, weather, school, farming, visiting a
   friend), a set of greeting/vocabulary phrases, and 8 proverbs. Yoruba
   entries: a self-introduction/greeting dialogue, two standalone
   sentences, and 10 proverbs (2 of which were exact repeats of others and
   were automatically deduplicated to 8 unique proverbs during
   preprocessing — see below). No third-party contributors were recruited
   for either language in this release, so `docs/CONSENT_FORM.md`'s
   per-contributor consent process was not needed for these entries — both
   authors are contributing their own writing.
2. **Web-scraping from openly-licensed sources — attempted, but produced
   zero entries in this release.** The course lecturer permitted
   web-scraping with source credit as an alternative to consented human
   collection (see `DECISIONS.md` D026). This was attempted using
   `scripts/scrape_source.py` against pre-approved sources
   (africanstorybook.org, the `storybooks-uganda` mirror, and the Yoruba
   Wikipedia REST API), but the automated agent's environment could not
   reach any of those hosts, and the Rukiga content on `storybooks-uganda`
   turned out not to exist yet (listed as aspirational, not actually
   published). Per the pipeline's own rule (stop and disclose rather than
   substitute or fake data), this path was abandoned in favour of human
   collection. Full detail: `BLOCKED.md`, `DECISIONS.md` D028.

### Sources and credits (web-scraped entries)

Not applicable — this release contains no `source_type=web-scraped`
entries (see above).

## Consent and ethics

All entries in this release are self-written by the two student authors, so
individual per-contributor consent (`docs/CONSENT_FORM.md`) was not
exercised for this release — both authors chose to write and publish their
own text under the license below. `docs/CONSENT_FORM.md` and
`docs/COLLECTION_PROTOCOL.md` remain ready for use if either author later
adds entries from other contributors. No personal identifying information
about any private individual is present in the data (verified by automated
PII pattern checks plus human review — see Validation below); the two names
that appear in the Yoruba introduction dialogue ("Adé"/"Tálà") are generic
placeholder names for a teaching-style example conversation, not real
people. See `docs/ETHICS_CHECKLIST.md` for the pre-release checklist this
dataset was checked against.

## Preprocessing

Text was Unicode NFC-normalised, invisible/control characters were
stripped, whitespace was cleaned up, and curly quotes were normalised to
straight quotes. **Diacritics and tone marks were never stripped, added,
or corrected** — see `DECISIONS.md` D005/D009. Exact duplicates were
removed (logged, never silently); near-duplicates were flagged for human
review, not auto-deleted. Full details: `scripts/preprocess.py`,
`reports/preprocess_summary.md`.

Per-language results: Rukiga — 63 input rows, 0 encoding/whitespace/quote
changes needed, 0 exact duplicates. Yoruba — 17 input rows, 1 quote-style
normalisation, 2 exact duplicates removed (the two repeated proverbs
mentioned above; see `reports/duplicates_removed.csv`), 15 final entries.
0 near-duplicates flagged in either language.

## Validation

### Automatic

`scripts/validate_auto.py` checked schema conformance, required fields,
empty/short entries, duplicates (within and across languages), length
outliers, rare characters, possible PII, metadata consistency, a
heuristic language-label sanity check, diacritic consistency, and
translation sanity. See `reports/validation.md` for full results and its
**Limitations** section — several checks are heuristic hints for human
review, not verdicts, because neither this pipeline nor its authors are
fluent in both languages.

53 total flags across both languages: 19 `rare_character`, 20
`possible_pii`, 11 `diacritic_mixed_style` (Yoruba only), 2
`translation_length_ratio_outlier` (both Rukiga proverbs, caused by the
bracketed `[meaning: ...]` explanation appended to short proverb text —
expected, not an error), and 1 `language_looks_like_other_language`
(a Yoruba proverb with few diacritics, a small-sample statistical
artefact). All 20 `possible_pii` flags were individually reviewed by a
human (the independent Rukiga reviewer, and the Yoruba collector via
self-review) and confirmed to be false positives — sentence-initial
capitalisation, real proper nouns/place names ("English", "Lagos"), or the
two placeholder dialogue names — none required correction or removal.
Note: `validate_auto.py`'s own report literally still prints "PII check:
FAIL", because that specific check is a blind pattern re-scan with no
memory of human review and will re-flag the same legitimate words every
time it runs (see `DECISIONS.md` D030); `scripts/build_release.py`'s
actual release gate was fixed to check "was this flag reviewed by a
human", which every flag here now satisfies.

### Layer 1 — independent language review

- **Rukiga:** 57 of 63 entries (90.5%) were reviewed by an independent
  fluent Rukiga speaker — a family member of the collector who did not
  write any of the entries (anonymous code `R01`). Two real errors were
  found and corrected (`cgg-0017`: missing letter; `cgg-0020`: incorrect
  word — see `reports/corrections_log.csv` for both). The remaining 55
  reviewed entries were confirmed correct. 6 entries were not included in
  the review sample and have not been independently reviewed
  (`cgg-0019`, `cgg-0031`, `cgg-0032`, `cgg-0037`, `cgg-0042`, `cgg-0052`).
- **Yoruba:** **no independent fluent Yoruba speaker was recruited before
  the deadline.** All 15 entries were reviewed only by the collector
  (Author 2, who also wrote them) — recorded separately from the formal
  independent-review sheet and marked `reviewed_by_independent=false` for
  every Yoruba entry, precisely so this is never mistaken for independent
  verification. Target-language correctness for the Yoruba entries in this
  release is **not independently verified**.

### Layer 2 — cross-review and agreement

Each author was meant to review the other author's entries for
English-side issues only (translation readability, PII, metadata,
formatting) — this layer never verifies target-language correctness — with
agreement on a shared overlap set measured via percent agreement and
Cohen's kappa. **This layer was not completed before the deadline** (3 of
28 rows completed on one side, 0 of 66 on the other), so no agreement
statistic is available for this release. Rukiga's language correctness is
still independently covered via Layer 1 above; Yoruba's is not covered by
either layer.

## Intended uses

Seed or evaluation data for NLP research and tool development in Rukiga
and Yoruba (e.g. translation, language identification, or
text-normalisation tools); educational use; linguistic study of proverbs
and short-form text in these languages.

## Out-of-scope uses

This dataset is small (63 Rukiga / 15 Yoruba entries) and was collected by
two individuals, each contributing their own writing — **it is not
representative of either language as a whole** and should not be used to
make broad claims about Rukiga or Yoruba speakers, dialects not
represented here, or used as a sole training source for a production
system without awareness of these limits.

## Limitations and biases

- **Sample size and contributor-pool bias (mandatory):** this is a small,
  non-representative dataset from a single contributor per language (both
  authors); it reflects their own individual language use, not the full
  diversity of either language community. No volunteer contributors were
  recruited for this release.
- **Review coverage (mandatory):** Rukiga — 90.5% independently reviewed
  by a fluent speaker (2 real errors found and fixed), 9.5% not reviewed
  at all. Yoruba — 0% independently reviewed; all 15 entries were
  self-reviewed only by the person who wrote them, and target-language
  correctness is not independently verified. Layer 2 cross-review /
  agreement was not completed for either language.
- **Automatic checks are heuristic:** language-label sanity, diacritic
  consistency, and character-anomaly checks are dataset-derived
  heuristics, not authoritative linguistic judgements — see
  `reports/validation.md`'s Limitations section. In particular, the
  `diacritic_mixed_style` flags on 11 Yoruba entries were never resolved
  by a genuinely independent fluent-speaker judgement, only by the
  collector's own self-review.
- **Domain and content skew:** Yoruba is heavily proverb-weighted (8 of 15
  entries, 53%), with the remainder a single introduction dialogue plus
  two standalone sentences — narrower topic coverage than Rukiga, which
  spans a market dialogue, five everyday topics, greetings, and proverbs.
  Both languages come from a single contributor's vocabulary and register,
  not a cross-section of speakers.
- **Web-scraping path unused:** despite being permitted and attempted, no
  web-scraped entries are present in this release (see "How the data was
  collected" above) — all entries are self-written.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0) — proposed by
the authors for their own self-written contributions; see
`docs/CONSENT_FORM.md` for the license as it would be presented to any
future third-party contributor.

## Citation

```
Nabasa Amos and Jesulewami Kupoluyi (2026). Rukiga-Yoruba Short Text and
Proverbs Dataset. Practical II: End-to-End Data Curation (course
assignment). Unpublished/coursework dataset; final repository URL to be
added after upload.
```

## Authors and contributions

- **Nabasa Amos:** Rukiga data collection (63 entries: market dialogue,
  everyday-topic paragraphs, greetings, proverbs); pipeline development
  and maintenance; found and fixed a bug in the release gate's PII check
  (`DECISIONS.md` D030).
- **Jesulewami Kupoluyi:** Yoruba data collection (17 raw / 15 final
  entries: introduction dialogue, standalone sentences, proverbs);
  self-review of the Yoruba entries (not independent — see Layer 1 above).
- **Independent Rukiga reviewer (`R01`):** family member of Author 1, not
  otherwise identified in this repository; independent Layer 1 review of
  57 of 63 Rukiga entries, finding and specifying 2 corrections.

## Contact

- Nabasa Amos: amosnabasa4@gmail.com
- Jesulewami Kupoluyi: jesulewamikupoluyi@gmail.com
