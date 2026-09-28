> **DRAFT — template for the two authors to fill in and adapt.**

# Team plan

## Roles

| Role | Person | Notes |
|---|---|---|
| Author 1 — collects Rukiga (`cgg`) | Nabasa Amos | Also does Layer 2 cross-review of Yoruba entries (English-side only). |
| Author 2 — collects Yoruba (`yor`) | Jesulewami Kupoluyi | Also does Layer 2 cross-review of Rukiga entries (English-side only). |
| Layer 1 independent reviewer — Rukiga | [FILL IN — a fluent Rukiga speaker who did NOT collect the entries; Author 1 is a native Rukiga speaker but cannot review their own collected entries independently — this must be someone else, e.g. a family member/friend] | Anonymous code: `R0_ [FILL IN]` |
| Layer 1 independent reviewer — Yoruba | [FILL IN — a fluent Yoruba speaker who did NOT collect the entries] | Anonymous code: `R0_ [FILL IN]` |

If no independent reviewer can be recruited for a language before the
deadline, say so here rather than leaving it blank silently — the pipeline
and dataset card handle "no independent reviewer" as a documented
limitation, not an error, but only if we're honest about it.

## Contributor ID allocation

To avoid both authors accidentally reusing the same `C0xx` code:

- Author 1 (Rukiga): `C001`–`C0[FILL IN — e.g. 099]`
- Author 2 (Yoruba): `C1[FILL IN — e.g. 00]`–`C1[FILL IN]`

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

| Milestone | Target date | Owner |
|---|---|---|
| Collection complete (both languages, 150–250 entries each) | [FILL IN] | Both |
| Preprocessing + auto-validation run | [FILL IN] | [FILL IN] |
| Layer 1 independent review complete | [FILL IN] | Layer 1 reviewers |
| Layer 2 cross-review + overlap complete | [FILL IN] | Both authors |
| Agreement computed, disagreements discussed | [FILL IN] | Both |
| Corrections applied, conflicts resolved | [FILL IN] | Both |
| Dataset card filled in, release built | [FILL IN] | [FILL IN] |
| Upload (by hand, by an author, with their own credentials) | [FILL IN] | [FILL IN] |

## Who does what (working split)

- **Recruiting contributors and obtaining consent:** each author, for their
  own language.
- **Recruiting the Layer 1 independent reviewer:** each author, for their
  own language (must be someone who did not collect the entries).
- **Running the pipeline scripts:** [FILL IN — can be either/both; the
  scripts are the same regardless of who runs them].
- **Filling the dataset card with real numbers:** [FILL IN].
- **Final upload to Hugging Face:** [FILL IN — see docs/UPLOAD_GUIDE.md for
  under whose account / an organisation, and how to add the other author
  as a collaborator].

---

## CONTRIBUTIONS (template for the report / dataset card)

> Fill this in honestly once work is done — it becomes part of the
> "Authors and contributions" section of the dataset card and can be
> reused in the course report.

- **Nabasa Amos:** [FILL IN — e.g. Rukiga data collection (N entries),
  pipeline development, Layer 2 cross-review of Yoruba entries, ...]
- **Jesulewami Kupoluyi:** [FILL IN — e.g. Yoruba data collection (N
  entries), Layer 2 cross-review of Rukiga entries, ...]
- **Layer 1 Rukiga reviewer:** [FILL IN name/role or "to be confirmed"]
- **Layer 1 Yoruba reviewer:** [FILL IN name/role or "to be confirmed"]
