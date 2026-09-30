# Preprocessing summary

Raw files read: 2 (raw_cgg_author1.csv, raw_yor_author2.csv)

## Per-language counts

| Language | Input rows | NFC changed | Invisible-char changed | Whitespace changed | Quotes changed | Exact duplicates removed | Near-duplicates flagged | Final entries |
|---|---|---|---|---|---|---|---|---|
| Rukiga (`cgg`) | 63 | 0 | 0 | 0 | 0 | 0 | 0 | 63 |
| Yoruba (`yor`) | 17 | 0 | 0 | 0 | 1 | 2 | 0 | 15 |

NFC-normalisation counts are reported separately per the task brief, since diacritic/combining-mark encoding inconsistency is a common source of silent duplicates and mismatches (see DECISIONS.md D005).

Near-duplicates are **flagged only, never auto-deleted** — see reports/near_duplicates.csv and DECISIONS.md D006.
