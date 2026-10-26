> Filled in from the project record (DECISIONS.md, the dataset card). Dates were not tracked during collection and are marked as such.

# Team plan

## Roles

| Role | Person | Notes |
|---|---|---|
| Author 1 — collects Rukiga (`cgg`) | Nabasa Amos | Also does Layer 2 cross-review of Yoruba entries (English-side only). |
| Author 2 — collects Yoruba (`yor`) | Jesulewami Kupoluyi | Also does Layer 2 cross-review of Rukiga entries (English-side only). |
| Layer 1 independent reviewer — Rukiga | Family member of Author 1, fluent Rukiga speaker, did not collect any entries (real identity kept outside this repo, per `docs/COLLECTION_PROTOCOL.md` Section 4) | Anonymous code: `R01` |
| Layer 1 independent reviewer — Yoruba | **Not recruited before the deadline.** Entries were instead self-reviewed by Author 2 (the collector) — recorded separately in `reports/review/layer1_yor_selfreview.csv`, kept distinct from the official (still-empty) `layer1_yor.csv` so this is never mistaken for independent review. `reviewed_by_independent` is `false` for all Yoruba entries. | N/A — self-review, not independent |

If no independent reviewer can be recruited for a language before the
deadline, say so here rather than leaving it blank silently — the pipeline
and dataset card handle "no independent reviewer" as a documented
limitation, not an error, but only if we're honest about it.

## Contributor ID allocation

To avoid both authors accidentally reusing the same `C0xx` code:

- Author 1 (Rukiga): `C001` (the only Rukiga code used)
- Author 2 (Yoruba): `C101` (the only Yoruba code used)

(Any non-overlapping ranges work — the point is just that the two authors
agree on ranges before collecting, so codes never collide when raw CSVs
are combined by `preprocess.py`.)

## Reviewer ID allocation

- Layer 1 Rukiga reviewer: `R01`
- Layer 1 Yoruba reviewer: `R02`
- Layer 2 (Author 1 reviewing Author 2's entries): `R03` (Nabasa Amos)
- Layer 2 (Author 2 reviewing Author 1's entries): `R04` (Jesulewami Kupoluyi)

(Adjust if we recruit additional reviewers.)

## Timeline

Dates were not tracked in this repo. The record shows: collection in
September 2026 (`date_collected` 2026-09), both reviews and corrections
before release, and the licence change and re-upload in October 2026 (D033).
Not completed: Layer 2 cross-review and agreement (3 of 28 and 0 of 66 rows
filled) and any independent Yoruba review.

## Who does what (working split)

- **Recruiting contributors and obtaining consent:** each author, for their
  own language.
- **Recruiting the Layer 1 independent reviewer:** each author, for their
  own language (must be someone who did not collect the entries).
- **Running the pipeline scripts:** Nabasa Amos (pipeline development and maintenance, per the dataset card).
- **Filling the dataset card with real numbers:** Nabasa Amos.
- **Final upload to Hugging Face:** by hand, by Nabasa Amos, to the `rukiga-yoruba-datacuration` organisation (see docs/UPLOAD_GUIDE.md).

---

## CONTRIBUTIONS (template for the report / dataset card)

> Fill this in honestly once work is done — it becomes part of the
> "Authors and contributions" section of the dataset card and can be
> reused in the course report.

- **Nabasa Amos:** Rukiga data collection (63 entries), pipeline development and maintenance, fix of the release PII gate (D030). Layer 2 cross-review of Yoruba was not completed.
- **Jesulewami Kupoluyi:** Yoruba data collection (17 raw, 15 final entries) and self-review of them (not independent). Layer 2 cross-review of Rukiga was not completed.
- **Layer 1 Rukiga reviewer (R01):** Family member of Author 1, fluent Rukiga speaker — independent review of all 57 flagged/sampled Rukiga entries (real identity not disclosed in this repo).
- **Layer 1 Yoruba reviewer:** none recruited before the deadline (see the roles table).
