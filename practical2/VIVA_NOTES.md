# Viva notes

Anticipated questions a lecturer might ask, answered only from
`DECISIONS.md` and the other docs in this repo — not from general
knowledge beyond what's recorded there. Where the honest answer is
"default" or "not sure," that's stated rather than invented.

## Why two languages?

Rukiga and Yoruba, one per author, so the pair could split collection
work along a language neither of them shares — this is recorded as the
project's starting configuration (see the task brief's CONFIG section and
`docs/TEAM_PLAN.md`), not something this pipeline chose. What the
pipeline *did* have to design around, because of that choice, is that
**neither author can verify the other's language** — this drives several
downstream decisions: `translation_en` being required on every entry
(D003), the two-layer review design (Layer 1 independent-speaker review
vs. Layer 2 English-side-only cross-review), and the heuristic (not
authoritative) language-label sanity check in validation (D014).

## Why Rukiga instead of Luganda, and why web-scraping?

Both changes came from the same 2026-09-29 instruction and are recorded
together in `DECISIONS.md` D026/D027, additive/corrective to the earlier
stages, not a restart. Two separate decisions:

- **Scope: web-scraping permitted.** The course lecturer explicitly
  approved sourcing entries by scraping openly-licensed websites (with
  attribution) as an alternative to consented human collection, given
  time constraints. `docs/COLLECTION_PROTOCOL.md` now documents both
  paths; human-collected `source_type`s remain fully valid and unremoved.
- **Language: Luganda → Rukiga (`cgg`).** Author 1 is a native Rukiga
  speaker, which was not true for Luganda. That matters concretely: it
  means Author 1 can genuinely judge whether scraped or collected text is
  actually Rukiga (not just labelled as such — a real check on one
  candidate source turned up mislabeled Dutch content, which is exactly
  the failure mode a non-speaker author cannot catch) and can recruit an
  independent fluent Rukiga reviewer for Layer 1, neither of which was
  possible when the language was one nobody on the team spoke. Yoruba
  (Author 2) is unchanged.
- **Honest volume caveat:** unlike Yoruba, Rukiga has no Wikipedia or
  Wiktionary backup source available (checked and confirmed absent), so
  its approved source list is narrower. If the ~150-250/language target
  isn't reached for Rukiga, that's disclosed plainly in the dataset card
  and `LOG.md` rather than papered over or substituted with another
  language — see D026/D027 and the volume-estimate entry in `LOG.md`.

## Why these preprocessing steps (NFC, invisible-char strip, whitespace,
## quote normalisation, exact-dup removal, near-dup flagging)?

Each was explicitly requested in the assignment brief's Stage 3, in that
order. The design choices *within* each step are in `DECISIONS.md`:
- Curly-vs-straight quote normalisation only, not touching phonemic
  apostrophes or diacritics: D005.
- What counts as "invisible" (Unicode categories Cf and Cc, excluding
  combining marks): D009.
- Exact-duplicate key = (language, normalised text), not raw text or
  translation: D009.
- Near-duplicate flag threshold (0.90 SequenceMatcher ratio, flag only,
  never delete): D006.

## Why never auto-correct diacritics?

This was an explicit, non-negotiable rule in the assignment brief: "NEVER
strip, add, or 'correct' diacritics or tone marks automatically," because
Yoruba text may legitimately appear with full tone marks, subdots only,
or none, and Rukiga has its own conventions this pipeline is not
qualified to judge (see D005, D009, D015). The pipeline enforces this by
only ever re-encoding via Unicode NFC normalisation (which changes how a
diacritic is *stored*, never whether it's present) and by treating any
apparent diacritic inconsistency as a **flag for a human fluent reviewer**
(`reports/validation.md`'s diacritic-consistency section), never an
automatic fix. This is tested directly in `tests/test_common.py`
(`test_nfc_never_strips_combining_marks`, and the decomposed-vs-composed
café test proving NFC only changes encoding).

## Why flag rather than delete?

Two explicit rules drove this: "near-duplicate FLAGGING (do not
auto-delete)" and "exact duplicate removal... never silently" for
preprocessing (D006), and for validation, "Flags are for a human to
review; do not auto-delete or auto-edit on flags" (see
`reports/validation.md`'s Limitations section, generated every run). More
generally, this pipeline is not fluent in Rukiga or Yoruba, so almost
every content-level judgement it makes is a statistical or pattern-based
heuristic (rare characters, PII shapes, language-label sanity, diacritic
mixing) — heuristics are useful for triage, not safe as unattended
deletion criteria. The only things ever removed automatically are exact
duplicates (logged) and rows whose `id` collides across raw files with
different content (the losing row is skipped, also logged) — both are
mechanical, not judgement calls.

## How were consent and anonymity handled?

`docs/CONSENT_FORM.md` (read/explained to each contributor in their own
language before they contribute) and `docs/COLLECTION_PROTOCOL.md`
(anonymous `contributor_id`/`reviewer_id` codes, never names, in any data
file; any code-to-identity mapping kept outside the repo — see D004).
This is enforced technically, not just by instruction: `.gitignore` blocks
any `*contributor_map*`/`*reviewer_map*`/`*id_map*` file from ever being
committed, and `scripts/make_review_sheet.py`'s `--contributor-map`
argument reads such a file only from a path the user supplies, never
storing or hardcoding one. The honest limitation: this pipeline cannot
verify a human actually followed the consent protocol — that's on the
authors, checked via `docs/ETHICS_CHECKLIST.md` before release.

## How was validation designed?

Around one constraint: this pipeline is not fluent in Rukiga or Yoruba,
so every check beyond pure schema/format validation is either (a) purely
mechanical (duplicates, PII regex patterns, length/character statistics
computed from the dataset's own distribution) or (b) an explicitly-labelled
heuristic hint for a human reviewer (language-label sanity, diacritic
mixed-style). `reports/validation.md` states this in a dedicated
Limitations section every time it's generated, and none of the
thresholds chosen (D010-D015) claim to be empirically validated — they're
documented defaults, most rated "Medium" or lower confidence, deliberately.

## Why two review layers, and what can/can't each verify?

- **Layer 1 (independent language review):** a fluent speaker of the
  language who did *not* collect the entries — the only layer that can
  judge target-language correctness. If no independent reviewer exists
  for a language, `reviewed_by_independent` stays `false` for those
  entries and the dataset card must say so as a mandatory limitation (see
  `docs/SCHEMA.md`, `release/DATASET_CARD_TEMPLATE.md`).
- **Layer 2 (cross-review between the two authors):** each author reviews
  the *other's* entries, but explicitly and only for what they can judge
  without reading the source language — does the English translation
  read sensibly, PII, metadata, formatting, flagged items. Every Layer 2
  sheet states at the top that it does not verify target-language
  correctness (`scripts/make_review_sheet.py`), and
  `scripts/apply_corrections.py` mechanically enforces this: a Layer 2
  correction to the `text` field is never auto-applied, it's always
  routed to `reports/conflicts.csv` for the language's independent
  reviewer or original collector to decide (D020-D022).
- **The shared overlap set:** both authors also review a reproducible
  (seed 42) shared subset drawn from both languages, purely so there's
  something to measure agreement on — without it, the two authors'
  Layer 2 sheets (one all-Yoruba, one all-Rukiga) would never share any
  ids (D017).

## How was agreement measured?

Percent agreement and Cohen's kappa (`scripts/compute_agreement.py`,
standard-library-only, no scipy/sklearn), computed only over overlap-set
ids where *both* reviewers filled in a verdict — an incomplete pair is
reported separately, not treated as either agreement or disagreement.
The report states explicitly that this measures agreement on Layer 2's
English-side judgement, **not** target-language correctness (that's
Layer 1's job, and Layer 1 has only one reviewer per language, so there's
no second rater to compute agreement against). The verdict vocabulary
(`ok`/`needs_correction`/`reject`) is this pipeline's own default, not
specified in the assignment brief — see D019.

## Why this license?

CC BY 4.0, and explicitly marked "proposed, to be confirmed by the
authors" everywhere it appears (`docs/CONSENT_FORM.md`,
`release/DATASET_CARD_TEMPLATE.md`, `release/LICENSE`'s generated notice)
— because the task brief itself only proposes this license pending
confirmation, and this pipeline never finalises a legal decision on the
authors' behalf (see the GOAL section of the brief and D025 for why the
LICENSE file links to the canonical CC text rather than vendoring it).

## How was work split?

See `docs/TEAM_PLAN.md`'s role table and CONTRIBUTIONS template — Author
1 (Nabasa Amos) collects Rukiga, Author 2 (Jesulewami Kupoluyi) collects
Yoruba, each also does Layer 2 cross-review of the other's language. This
is also the *default* assumption `scripts/make_review_sheet.py` uses to
assign Layer 2 reviewers when no `--contributor-map` file is given
(D016) — correct for this specific two-author/two-language project,
explicitly not assumed to generalise.

## What are the limitations?

Stated in full in `release/DATASET_CARD_TEMPLATE.md`'s "Limitations and
biases" section (mandatory paragraphs on review coverage and on small
sample size / contributor-pool bias), and in `reports/validation.md`'s
generated Limitations section. In short: this is a small
(150-250-entries-per-language target), non-representative dataset from a
limited contributor pool known to the authors; several validation checks
are heuristic hints, not verdicts, because this pipeline cannot read
either language; and any language without a recruited independent
reviewer has target-language correctness that is not independently
verified — the dataset card must say so plainly rather than soften it.
