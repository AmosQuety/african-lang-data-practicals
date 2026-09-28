# Dataset schema

> Draft for the two authors to review and adapt. Follow our course's data
> management / ethics guidance where it differs from this document.

This is the row-level schema for the Practical 2 dataset. The machine-readable
version is `practical2/docs/schema.json` (JSON Schema draft-07); the
pipeline (`scripts/preprocess.py`, `scripts/validate_auto.py`) validates
every processed row against it. `data/processed/dataset.jsonl` is one JSON
object per line, one object per field below.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Stable unique id, e.g. `lug-0001`. Assigned during preprocessing if not already present in raw data. |
| `language` | string (ISO 639-3) | yes | `lug` (Luganda) or `yor` (Yoruba) only. |
| `text` | string | yes | The original-language text. Never empty. |
| `translation_en` | string | yes | English translation. **Required for every entry** — see DECISIONS.md. |
| `contributor_id` | string | yes | Anonymous code (`C001`, `C002`, ...). Never a real name. |
| `region` | string | optional | Free-text region/locality. |
| `dialect` | string | optional | Dialect label if known. |
| `date_collected` | string (`YYYY-MM`) | optional | Month of collection. |
| `source_type` | enum | yes | One of `self-written`, `volunteer-contributed`, `proverb`, `other`. |
| `domain` | string | optional | Topic/theme tag, e.g. `greetings`, `proverb`, `daily-life`. |
| `reviewed` | boolean | yes | `true` once any review layer (1 or 2) has looked at the entry. |
| `reviewer_id` | string or blank | optional | Anonymous reviewer code (`R01`, `R02`, ...), blank if unreviewed. |
| `reviewed_by_independent` | boolean | yes | `true` **only** if reviewed by a fluent speaker of that language who did **not** collect the entry (Layer 1). Otherwise `false`. |

## Why these fields (see DECISIONS.md for full entries)

- `translation_en` is required, not optional, because the assignment scope
  is text-only bilingual data and neither author can verify the other's
  language — the English gloss is the only thing both authors, and any
  external reviewer, can check.
- `contributor_id` / `reviewer_id` are anonymous codes, never names, per the
  DATA SAFETY RULES. Any file that maps a code to a real person must not be
  committed (see `.gitignore` and `docs/COLLECTION_PROTOCOL.md`).
- `reviewed_by_independent` is a separate boolean from `reviewed` because a
  Layer 2 (cross-author) review can mark `reviewed = true` while never
  verifying target-language correctness. Downstream reporting and the
  dataset card must be able to tell the two apart.
- `region` and `dialect` are optional because we cannot guarantee every
  contributor will supply them, and forcing them would either block valid
  entries or invite made-up values.

## Raw vs. processed

Raw CSVs in `data/raw/` may have a slightly looser shape (see
`docs/raw_template.csv` and `docs/COLLECTION_PROTOCOL.md`) — for example,
`id` may be blank and get assigned during preprocessing, and boolean fields
may arrive as `TRUE`/`FALSE`/`yes`/`no`/blank. `scripts/preprocess.py`
normalises raw rows into the strict schema above before writing
`data/processed/dataset.jsonl`.
