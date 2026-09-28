# How to fill in `raw_template.csv`

> Draft for the two authors to review and adapt.

This is a short guide for filling in `docs/raw_template.csv` (or a Google
Form / spreadsheet using the same columns) while collecting entries. Full
collection rules — what to avoid, consent, anonymous IDs — are in
`docs/COLLECTION_PROTOCOL.md`. This page is just the "what goes in each
cell" quick reference.

## Using a spreadsheet

1. Open `docs/raw_template.csv` in Google Sheets / Excel / LibreOffice, or
   copy its header row into a new sheet.
2. Add one row per entry. Do not reorder or rename columns.
3. When you export back to CSV, keep UTF-8 encoding (Google Sheets does
   this by default; in Excel use "CSV UTF-8").
4. Save your file as `data/raw/raw_<language>_<author>.csv`, e.g.
   `data/raw/raw_lug_author1.csv`.

## Using a Google Form

Set up one short-answer or paragraph question per column below (skip `id`
— leave that to the pipeline), export responses to a sheet, then to CSV
with the same column order.

## Column-by-column

| Column | What to put | Example |
|---|---|---|
| `id` | **Leave blank.** Assigned automatically. | *(blank)* |
| `language` | `lug` for Luganda entries, `yor` for Yoruba entries. Lowercase, exactly as shown. | `lug` |
| `text` | The sentence, proverb, or short phrase in the original language, typed as you would normally write it (keep any diacritics/tone marks — do not remove or "correct" them). | `Akola ekyalo, akyalira mu maaso.` |
| `translation_en` | An English translation that captures the **meaning**, not a word-for-word translation. If it's a proverb with no direct English equivalent, translate the meaning/sense and you may add a short bracketed note. **Required — never leave blank.** | `He who visits the village, benefits from it later.` |
| `contributor_id` | The anonymous code assigned to the contributor (see COLLECTION_PROTOCOL.md), e.g. `C001`. **Never a name.** | `C001` |
| `region` | Region/locality, if the contributor is comfortable sharing it (optional, free text). | `Central Uganda` |
| `dialect` | Dialect, if known (optional). | *(leave blank if unsure)* |
| `date_collected` | Month you collected it, `YYYY-MM`. | `2026-10` |
| `source_type` | One of: `self-written`, `volunteer-contributed`, `proverb`, `other`. | `proverb` |
| `domain` | A short topic tag if one comes to mind (optional): `greeting`, `proverb`, `daily-life`, `family`, etc. | `proverb` |
| `reviewed` | Leave blank / `FALSE` at collection time. Filled in later during review. | *(blank)* |
| `reviewer_id` | Leave blank at collection time. | *(blank)* |
| `reviewed_by_independent` | Leave blank / `FALSE` at collection time. | *(blank)* |

## Before you submit a batch

- Check `text` and `translation_en` are both filled for every row.
- Check `language` is exactly `lug` or `yor` (not "Luganda"/"Yoruba").
- Do not include names, phone numbers, addresses, or other personal
  identifiers anywhere in `text`, `translation_en`, `region`, `dialect`, or
  `domain` — see COLLECTION_PROTOCOL.md for what to avoid.
- Save/export as UTF-8 CSV.
