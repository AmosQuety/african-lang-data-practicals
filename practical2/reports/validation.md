# Automated validation report

Total entries: 78. Languages present: cgg, yor.

**PII check: FAIL** (20 possible-PII item(s) flagged in reports/flags.csv). `scripts/build_release.py` refuses to run while this is FAIL.

## Checks per language

| Check | cgg | yor | Total |
|---|---|---|---|
| `diacritic_mixed_style` | 0 | 11 | 11 |
| `language_looks_like_other_language` | 0 | 1 | 1 |
| `possible_pii` | 15 | 5 | 20 |
| `rare_character` | 10 | 9 | 19 |
| `translation_length_ratio_outlier` | 2 | 0 | 2 |

## Diacritic consistency per language

| Language | Entries with tone/subdot marks | Entries with none | % with marks | Mixed-style flags | Non-NFC entries |
|---|---|---|---|---|---|
| Rukiga | 0 | 63 | 0.0% | 0 | 0 |
| Yoruba | 14 | 1 | 93.3% | 11 | 0 |

## Limitations (read before trusting any flag above)

- **Language-label sanity** (`language_looks_like_english`, `language_looks_like_other_language`): both Rukiga and Yoruba use Latin script, so this cannot be verified by script alone — the check only compares an entry's characters/words against this dataset's own character profile and a generic list of common English function words. It is a hint for a human reviewer, not a verdict, and can both over- and under-flag.
- **Personal-name detection**: Yoruba and Rukiga personal names cannot be reliably detected automatically. The `capitalised_token` PII hint only flags a capitalised word that isn't at the start of the text — most such flags will be false positives (proper nouns, sentence-internal capitalisation) and most real names will NOT be flagged unless capitalised unusually. Human review is required for any name-related judgement.
- **Rare-character / length-outlier checks** are computed from this dataset's own distribution, which is small (150-250 entries per language target) — with few entries, thresholds are noisy and may flag legitimate variation as anomalous.
- **Diacritic mixed-style check** is a coarse heuristic based on a small hardcoded set of Yoruba tone-mark and subdot code points; it does not encode real Yoruba orthographic rules and needs a fluent reviewer to confirm.
- **PII patterns** (email/phone/URL/@handle/long-digit-run) catch only known shapes; they cannot catch identifying information phrased in prose (e.g. "my brother who lives on X street").

Flags are written to `reports/flags.csv` (columns: id, language, check, detail) for a human reviewer to work through — see `scripts/make_review_sheet.py`. Nothing is auto-deleted or auto-edited based on a flag.
