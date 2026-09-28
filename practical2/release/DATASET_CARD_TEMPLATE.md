---
language:
  - cgg
  - yor
license: cc-by-4.0
license_name: "Creative Commons Attribution 4.0 International (proposed — to be confirmed by the authors)"
multilinguality: multilingual
task_categories:
  - translation
  - text-generation
pretty_name: "[FILL IN — dataset display name]"
size_categories:
  - n<1K
---

> **This is a template.** Every fact about OUR data below is a `[FILL IN]`
> placeholder — do not invent numbers. Run `scripts/fill_card_stats.py`
> against the final dataset and paste its output in. This banner and the
> instructions in brackets should be removed from the final published
> card; `scripts/build_release.py` refuses to build the release while any
> `[FILL IN]` remains.

# Dataset Card for [FILL IN — dataset name]

## Dataset summary

[FILL IN — 2-3 sentences: what this dataset is, the two languages, that it
pairs short Rukiga and Yoruba text with English translations, and why it
was created (university course assignment producing an original
bilingual text dataset, sourced from a mix of consented human collection
and openly-licensed web sources — see "How the data was collected"
below).]

## Languages and dialects

- **Rukiga** (`cgg`) — [FILL IN: dialect(s) represented, region(s), entry
  count]
- **Yoruba** (`yor`) — [FILL IN: dialect(s) represented, region(s), entry
  count]

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

This dataset combines two sourcing methods:

1. **Consented human collection** — entries with `source_type` in
   `self-written`/`volunteer-contributed`/`proverb`/`other`. [FILL IN: who
   collected it (anonymised — refer to "two student collectors," not
   names, unless the authors decide otherwise — see docs/TEAM_PLAN.md's
   CONTRIBUTIONS template), how many contributors per language, what
   venues/contexts, over what time period. Summarise
   `docs/COLLECTION_PROTOCOL.md` rather than duplicating it.]
2. **Web-scraping from openly-licensed sources** — entries with
   `source_type=web-scraped`, permitted by the course lecturer as an
   alternative given time constraints (see `DECISIONS.md` D026).
   [FILL IN: `scripts/scrape_source.py`'s method summary and the **Sources
   and credits** subsection below, once populated.]

### Sources and credits (web-scraped entries)

[FILL IN once scraping is complete — one entry per site actually used, in
this form: site name, source URL pattern, license, and roughly how many
entries came from it. Example shape (delete once real credits are
filled in):
`[FILL IN site_name] — [FILL IN source URL pattern] — [FILL IN license] —
[FILL IN entry count]`.]

## Consent and ethics

Human-collected contributors gave informed consent (see
`docs/CONSENT_FORM.md`, explained to each contributor in their own
language before they contributed) to their text being published openly
under the license below, with no personal identifying information
retained. Web-scraped entries carry no personal data by construction (see
`docs/COLLECTION_PROTOCOL.md`'s note on the scraping path and
`scripts/scrape_source.py`'s PII-stripping step) and are credited to
their source site and license instead of a consent record. See
`docs/ETHICS_CHECKLIST.md` for the pre-release checklist this dataset was
checked against.

[FILL IN: any project-specific ethics notes, e.g. institutional approval
if applicable.]

## Preprocessing

Text was Unicode NFC-normalised, invisible/control characters were
stripped, whitespace was cleaned up, and curly quotes were normalised to
straight quotes. **Diacritics and tone marks were never stripped, added,
or corrected** — see `DECISIONS.md` D005/D009. Exact duplicates were
removed (logged, never silently); near-duplicates were flagged for human
review, not auto-deleted. Full details: `scripts/preprocess.py`,
`reports/preprocess_summary.md`.

[FILL IN: `scripts/fill_card_stats.py` output — per-language NFC-change
counts, duplicate counts.]

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

[FILL IN: validation.md summary — flag counts, PII check result (must be
PASS before release).]

### Layer 1 — independent language review

[FILL IN per language: was an independent fluent-speaker reviewer found?
If yes, coverage (entries reviewed / total) and how they were recruited.
If NO independent reviewer was available for a language, say so plainly
here — see the mandatory limitation below.]

### Layer 2 — cross-review and agreement

Each author reviewed the other author's entries for English-side issues
only (translation readability, PII, metadata, formatting) — **this layer
never verifies target-language correctness**. Agreement between the two
authors on a shared overlap set was measured with percent agreement and
Cohen's kappa. [FILL IN: `reports/agreement.md` numbers.]

## Intended uses

[FILL IN, but suggested starting points: NLP research and tool
development for Rukiga and Yoruba (e.g. as seed/evaluation data for
translation, language identification, or text-normalisation tools);
educational use; linguistic study of proverbs/short-form text in these
languages.]

## Out-of-scope uses

This dataset is small (150-250 entries/language target) and was collected
by two individuals from a limited contributor pool — **it is not
representative of either language as a whole** and should not be used to
make broad claims about Rukiga or Yoruba speakers, dialects not
represented here, or used as a sole training source for a production
system without awareness of these limits.

## Limitations and biases

- **Sample size and contributor-pool bias (mandatory):** this is a small,
  non-representative dataset from a limited number of contributors known
  to the authors; it reflects their networks' language use, not the full
  diversity of either language community.
- **Review coverage (mandatory):** [FILL IN per language — state plainly
  whether each language had an independent fluent-speaker reviewer
  (Layer 1) or only English-side cross-review (Layer 2), or no review.
  Example wording if no independent reviewer was found for a language:
  "Yoruba entries in this release have NOT been reviewed by an
  independent fluent Yoruba speaker who did not collect them; only
  English-side cross-review (Layer 2) and automatic checks were applied.
  Target-language correctness for these entries is not independently
  verified."]
- **Automatic checks are heuristic:** language-label sanity, diacritic
  consistency, and character-anomaly checks are dataset-derived
  heuristics, not authoritative linguistic judgements — see
  `reports/validation.md`'s Limitations section.
- [FILL IN: any further limitations noticed during review, e.g. domain
  skew (mostly proverbs vs. mostly conversational), regional skew.]

## License

[FILL IN once confirmed — currently proposed: Creative Commons
Attribution 4.0 International (CC BY 4.0). See `docs/CONSENT_FORM.md` for
the license as presented to contributors.]

## Citation

```
[FILL IN — BibTeX or plain citation once authors/date/venue are final]
```

## Authors and contributions

See `docs/TEAM_PLAN.md`'s CONTRIBUTIONS section. [FILL IN final text once
work is complete: "to be confirmed by the authors" until then.]

## Contact

[FILL IN — see docs/CONSENT_FORM.md contact details]
