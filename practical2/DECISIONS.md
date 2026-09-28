# Decision record

Every choice below could reasonably have gone another way. Entries are
added as decisions are made, not reconstructed at the end. Confidence is
this assistant's confidence, for the authors to check.

---

### D001 — Working branch and scope boundary

- **Decision:** Do all work on branch `practical2-run`, touching only files
  under `practical2/`. Never modify `practical1/` or any top-level
  `scripts/` folder. Never push to `main`.
- **Evidence or reasoning:** Explicit instruction in the task brief ("Work
  ONLY inside practical2/ ... Never push to main").
- **Alternatives considered:** None — this is a hard constraint, not a
  judgment call.
- **Risk:** Low; violating it would corrupt `practical1`'s history or
  main.
- **Confidence:** High.

### D002 — `id` format

- **Decision:** Entry ids are `<lang>-<4-digit-zero-padded-sequence>`, e.g.
  `lug-0001`, `yor-0142`, assigned in the order entries are encountered
  during preprocessing (stable within one preprocessing run, re-derived
  from scratch each run rather than persisted separately).
- **Evidence or reasoning:** The assignment gives no id format, only that
  `id` is a required field. A predictable, sortable, human-readable id
  scoped by language avoids collisions between the two authors' raw files
  and makes it obvious which language an id belongs to at a glance.
- **Alternatives considered:** (1) UUIDs — rejected, not human-friendly for
  a small 300–500 row dataset reviewers will eyeball in spreadsheets. (2)
  Global sequence ignoring language (`0001`, `0002`, ...) — rejected,
  harder to scan and to keep stable if one language's raw file grows before
  the other's.
- **Risk:** If ids are re-derived on every preprocessing run from raw file
  row order, and raw files are edited (rows inserted/reordered) between
  runs, ids for existing entries could shift, which would break any
  external reference to an id (e.g. in-progress review sheets). Mitigated
  by: once raw data collection is finalized, ids should be treated as
  stable and raw files should only have rows appended, not reordered.
  Documented here so it is not a silent trap.
- **Confidence:** Medium — reasonable default, but the id-stability caveat
  is a real operational risk the authors should be aware of.

### D003 — `translation_en` is required, not optional

- **Decision:** Every entry must have a non-empty `translation_en`, enforced
  in the schema and by validation.
- **Evidence or reasoning:** Explicit requirement in the task brief: "Every
  entry MUST have an English translation (translation_en is REQUIRED)."
  Also load-bearing for the rest of the design: "Neither author reads the
  other's language... The design must never assume they can verify each
  other's language correctness" — the English gloss is the only channel
  both authors (and Layer 2 cross-review) can use to sanity-check entries
  they cannot read.
- **Alternatives considered:** Making it optional with a `null` allowed for
  proverbs with "no real equivalent" — rejected because the brief already
  anticipates that case ("note when a proverb has no direct equivalent")
  and expects a translation *with a note*, not an absent translation.
- **Risk:** Could slow down collection if a contributor is unsure how to
  translate a proverb. Mitigated by `COLLECTION_PROTOCOL.md` guidance to
  translate meaning, not words, and note when there's no direct equivalent.
- **Confidence:** High — directly quoted requirement.

### D004 — Anonymous IDs never mapped in-repo

- **Decision:** `contributor_id` (`C0xx`) and `reviewer_id` (`R0x`) are
  opaque codes. Any file mapping a code to a real person's identity must
  never be created inside the repo; scripts that need such a mapping (e.g.
  Layer 2 cross-review, which needs to know which author collected which
  entries) accept a path to a local mapping file as a CLI argument, and
  that filename pattern (`*contributor_map*`, `*reviewer_map*`, `*id_map*`)
  is git-ignored.
- **Evidence or reasoning:** Explicit DATA SAFETY RULE: "Any file that maps
  anonymous IDs to real people ... must NOT be created or committed ... it
  must read it from a local file path passed as an argument."
- **Alternatives considered:** Storing the mapping encrypted in-repo —
  rejected, adds key-management complexity for no benefit when "don't
  commit it at all" is simpler and was explicitly requested.
- **Risk:** If an author names their local mapping file something outside
  the gitignore patterns, it could be accidentally committed. Mitigated by
  documenting the required naming convention in `COLLECTION_PROTOCOL.md`
  and `TEAM_PLAN.md`, and by `build_release.py` refusing to package
  anything outside `release/`.
- **Confidence:** High.

### D005 — Quote/apostrophe normalisation vs. diacritics

- **Decision:** Preprocessing normalises curly quotes/apostrophes
  (`’ ‘ “ ”`) to their straight ASCII equivalents (`'`, `"`) for
  consistency, but never touches combining diacritical marks, tone marks,
  or subdots — those are only ever re-encoded (not added/removed/changed)
  by NFC normalisation.
- **Evidence or reasoning:** Explicit instruction: "both languages may use
  apostrophes or diacritics meaningfully, so do NOT remove them; normalise
  curly vs straight only, and record this decision in DECISIONS.md" and the
  separate diacritics rule: "NEVER strip, add, or 'correct' diacritics or
  tone marks automatically... Only NFC normalisation may change how a
  diacritic is encoded."
- **Alternatives considered:** Leaving curly quotes as-is (no
  normalisation) — rejected, curly-vs-straight is a pure encoding
  inconsistency (not a meaningful linguistic distinction in either
  language, based on general orthographic knowledge, not confirmed by a
  fluent speaker) and normalising it reduces noise in downstream duplicate
  detection.
- **Risk:** If in fact either language does use curly vs. straight
  apostrophes meaningfully (unlikely, but this assistant is not a fluent
  speaker of either language), this normalisation would be wrong.
  Flagged for the independent language reviewers to confirm.
- **Confidence:** Medium — the quote-normalisation default is standard
  practice, but not confirmed against Luganda/Yoruba orthographic
  authorities.

### D006 — Near-duplicate flagging, not deletion

- **Decision:** Preprocessing only flags near-duplicates (does not delete),
  writing them to a report for human review; only exact duplicates are
  auto-removed (first occurrence kept, removed ones logged).
- **Evidence or reasoning:** Explicit instruction: "Optional near-duplicate
  FLAGGING (do not auto-delete)" and "Exact duplicate removal... never
  silently."
- **Alternatives considered:** Auto-deleting near-duplicates above a
  similarity threshold — rejected, explicitly disallowed, and risky because
  two genuinely different short proverbs can be very similar strings.
- **Risk:** Near-duplicate detection (this pipeline uses a simple
  normalised-text similarity ratio via `difflib.SequenceMatcher`, threshold
  0.90, computed per language) may both over-flag (benign near-duplicates)
  and under-flag (semantically identical but textually distant entries,
  which cannot be caught by string similarity alone).
- **Confidence:** Medium — threshold is a reasonable default, not
  empirically tuned on this dataset (which doesn't exist yet).

### D007 — Consent form leaves age/consent threshold to course guidance

- **Decision:** `CONSENT_FORM.md` does not set a specific minimum age or
  guardian-consent rule; it flags this explicitly as `[FILL IN — confirm
  age/consent requirements with course guidance]` rather than guessing one.
- **Evidence or reasoning:** The brief doesn't specify a threshold, and this
  is exactly the kind of institution-specific ethics rule the top-level
  instruction says to leave to "our course's ethics guidance where it
  differs." Guessing a number here (e.g. "18+") could be wrong for the
  course's actual policy and would be presented with false confidence.
- **Alternatives considered:** Defaulting to "contributors must be 18+" —
  rejected as an invented rule with no basis in the assignment text.
- **Risk:** If left unfilled, collection could start without a clear
  consent-age policy. Flagged prominently in `CONSENT_FORM.md` and
  `ETHICS_CHECKLIST.md` so it isn't missed.
- **Confidence:** High that leaving it as a placeholder is correct; the
  actual answer is out of scope for this assistant to decide.

### D008 — Reviewer ID allocation is a proposed default, not fixed

- **Decision:** `TEAM_PLAN.md` proposes `R01`/`R02` for the two Layer 1
  independent reviewers and `R03`/`R04` for the two authors acting as
  Layer 2 cross-reviewers, but this is a suggested default the authors can
  change.
- **Evidence or reasoning:** Nothing in the brief mandates specific codes;
  a concrete starting proposal is more useful to fill in than an empty
  template, and scripts (`make_review_sheet.py`, `compute_agreement.py`)
  don't hardcode these values — they read whatever `reviewer_id` appears in
  the sheets.
- **Alternatives considered:** Leaving reviewer IDs entirely as `[FILL IN]`
  with no example — rejected, a worked example makes the template easier
  to use correctly.
- **Risk:** None beyond the authors needing to actually update it if they
  recruit different reviewers.
- **Confidence:** High.

### D009 — Exact-duplicate key, invisible-character definition, blank booleans

- **Decision (dup key):** Two entries are an "exact duplicate" if they have
  the same `language` and the same `text` *after* normalisation (NFC,
  invisible-char strip, whitespace cleanup, quote normalisation) — not
  compared on raw/unprocessed text, and not on `translation_en`.
- **Evidence or reasoning:** The brief lists "Exact duplicate removal" as
  step (e) of preprocessing, after steps (a)-(d), implying it runs on
  already-cleaned text; comparing raw text would miss duplicates that only
  differ in whitespace/quote style, which is exactly the kind of
  inconsistency this pipeline is meant to catch.
- **Alternatives considered:** Also requiring `translation_en` to match —
  rejected: two contributors could submit the same source text with
  slightly different (both valid) English glosses, and we want to catch
  the source-text duplicate regardless.
- **Risk:** Two genuinely different entries that normalise to identical
  text (rare for real sentences) would be incorrectly merged. Mitigated by
  always logging removed rows to `reports/duplicates_removed.csv` for
  human review, never deleting silently.
- **Confidence:** Medium — reasonable reading of "duplicate," not
  contradicted by the brief, but not spelled out explicitly either.

- **Decision (invisible chars):** "Invisible/control/zero-width characters"
  = Unicode general categories `Cf` (format characters: zero-width
  space/joiner/non-joiner, left-to-right/right-to-left marks, byte-order
  mark, etc.) and `Cc` (control characters) other than `\t`/`\n`/`\r`
  (handled separately by whitespace cleanup). Combining marks (`Mn`/`Mc`),
  which carry diacritic/tone information, are never touched by this step.
- **Evidence or reasoning:** This is the standard Unicode-category
  definition of "invisible" formatting/control characters, and explicitly
  excludes combining marks to satisfy the separate, stronger diacritics
  rule ("NEVER strip, add, or 'correct' diacritics or tone marks
  automatically").
- **Alternatives considered:** A hand-maintained list of specific
  characters (e.g. just `U+200B`, `U+FEFF`) — rejected as more fragile;
  category-based matching catches the whole class without needing to
  enumerate every zero-width variant.
- **Risk:** Very low — these categories are well-defined and stable.
- **Confidence:** High.

- **Decision (blank booleans):** At collection time, `reviewed` and
  `reviewed_by_independent` are normally left blank; preprocessing treats a
  blank/unrecognised value for these two fields as `False`, not as a
  validation error.
- **Evidence or reasoning:** `FILLING_GUIDE.md` tells contributors/authors
  to leave these blank when submitting raw collection data (they're filled
  in during the review stages, not at collection). A dataset entry that
  hasn't been reviewed yet is, factually, not reviewed.
- **Alternatives considered:** Requiring these fields to be explicitly
  `TRUE`/`FALSE` and treating blank as invalid — rejected, would force
  every contributor to type `FALSE` for two fields they can't meaningfully
  fill in yet, for no safety benefit (the default is transparent and
  correct: "not yet reviewed").
- **Risk:** If a raw file has a genuine typo in one of these columns (e.g.
  `"flase"`), it silently becomes `False` rather than raising an error.
  Mitigated by `preprocess.py` itself: any raw value that isn't blank and
  isn't a recognised true/false spelling is logged to
  `reports/boolean_anomalies.csv` (not silently dropped), so a human can
  check whether it should have been `True`.
- **Confidence:** Medium — a reasonable default, but the silent-fallback
  risk above is real and is why Stage 4 must flag unrecognised raw values
  rather than trust this default blindly.

### D010 — Length outlier rule and "very short" threshold

- **Decision:** "Very short" = text under 3 characters (a separate,
  always-on check). Length outliers use the standard-deviation rule only
  (flag if `|length - mean| > 3 * population_stddev`, computed per
  language), not the percentile rule — the brief offers both as examples
  ("such as ... or ...").
- **Evidence or reasoning:** The brief explicitly allows picking one
  concrete rule ("flag by a clearly stated rule such as outside the
  1st-99th percentile or more than 3 standard deviations"). At the target
  scale (150-250 entries/language) a percentile-based rule would flag
  exactly ~1-2 entries at each tail almost by construction regardless of
  whether they're actually unusual, which is a worse signal than a
  distribution-shape-aware std-dev rule at this sample size.
- **Alternatives considered:** 1st-99th percentile — rejected for the
  small-sample reason above. Both rules simultaneously — rejected as
  needless complexity; one clearly stated rule is what's asked for.
- **Risk:** With few entries, `stddev` itself is noisy, and 3-sigma may
  flag nothing at all in a small, fairly uniform dataset (which is
  arguably correct) or over-flag if one contributor writes unusually long
  entries.
- **Confidence:** Medium — a defensible default, not empirically tuned.

### D011 — Translation length-ratio outlier bounds

- **Decision:** Flag `translation_en` when `len(translation)/len(text)` is
  outside `[0.15, 6.0]`, a fixed heuristic range rather than a statistical
  one.
- **Evidence or reasoning:** The brief asks for "very large length-ratio
  outliers between text and translation" without a formula. A fixed range
  is simpler and more interpretable for a check whose real purpose is
  catching gross errors (empty-ish translations, or a translation that's
  actually a paragraph of notes) rather than modelling a "normal" ratio
  distribution, which for short proverbs-vs-English-gloss data doesn't
  have an obviously meaningful mean/stddev shape.
- **Alternatives considered:** Per-language statistical ratio-outlier
  detection (same std-dev approach as D010) — rejected as overkill for a
  sanity check whose failure mode (very large or very small ratio) is
  already well captured by fixed, generous bounds; a statistical version
  is added later only if real data shows the fixed bounds misbehaving.
- **Risk:** A legitimately terse translation of a long proverb, or a
  translation that includes a long bracketed explanatory note (explicitly
  encouraged by `COLLECTION_PROTOCOL.md` for proverbs with no direct
  equivalent), could trip this. It's a flag, not a rejection, so a human
  resolves it.
- **Confidence:** Medium.

### D012 — Rare-character threshold

- **Decision:** Within each language, a character is "rare" if it appears
  in 2 or fewer entries dataset-wide (excluding whitespace); any entry
  containing such a character is flagged.
- **Evidence or reasoning:** "The rare-character rule must use each
  language's OWN character distribution" — built here from the dataset
  itself (there is no external reference corpus available/permitted per
  NETWORK RULES). A small absolute-count threshold, rather than a
  percentage, behaves more sensibly at the 150-250-entries-per-language
  target size than a percentage would.
- **Alternatives considered:** A frequency-percentage threshold (e.g.
  "<0.5% of entries") — rejected, at ~200 entries that's <1 entry, making
  it nearly equivalent to but less transparent than a small fixed count.
- **Risk:** Real, legitimate letters that are simply infrequent in a small
  dataset (e.g. a rarely-used Luganda or Yoruba letter/diacritic
  combination) will be flagged even though they're correct. This is
  explicitly expected and stated in validation.md's limitations section.
- **Confidence:** Medium — reasonable given the constraint of having no
  external reference corpus.

### D013 — Region-spelling-inconsistency threshold

- **Decision:** Two distinct (case-insensitively different) region strings
  are flagged as possibly-inconsistent spellings if their
  `difflib.SequenceMatcher` ratio is `>= 0.82`.
- **Evidence or reasoning:** No formula given in the brief for "consistency
  of metadata values (e.g. ... region spellings)"; a string-similarity
  ratio is a standard, dependency-free (stdlib `difflib`) way to catch
  near-duplicate free-text values like "Kampala" vs "Kampala " vs "kampala
  region" without a hardcoded region gazetteer, which isn't available.
- **Alternatives considered:** Exact case-insensitive match only —
  rejected, misses whitespace/typo variants which are the actual failure
  mode this check is meant to catch. A hardcoded list of valid Ugandan and
  Nigerian regions — rejected as out of scope to source/maintain reliably.
- **Risk:** 0.82 is an untuned threshold; could both over-flag genuinely
  different nearby place names and under-flag very different misspellings
  of the same place.
- **Confidence:** Low-medium — this is the least evidence-backed threshold
  in the pipeline; flagged here for the authors to sanity-check once real
  region values exist.

### D014 — "Looks like English" stopword-fraction threshold

- **Decision:** An entry is flagged `language_looks_like_english` if 50%+
  of its alphabetic words are in a small hardcoded list of ~35 common
  English function words (the/a/is/of/...), and it has at least 3 words.
- **Evidence or reasoning:** No formula given; function words are
  deliberately chosen (rather than a full English dictionary, which risks
  false negatives on Luganda/Yoruba entries that happen to contain
  English-loanword content words) because they're near-universal in
  English sentences and vanishingly unlikely to appear at high density in
  genuine Luganda/Yoruba text by chance.
- **Alternatives considered:** A full English-word-frequency dictionary —
  rejected as a heavier dependency (would need an external wordlist) for
  marginal gain over a small stopword list at this task's precision needs
  (this is explicitly a hint, not a verdict).
- **Risk:** Short entries or ones embedding an English loanword phrase
  could trip this; entries under 3 words are exempted specifically because
  the fraction is too noisy at that length. Explicitly documented as a
  heuristic in validation.md.
- **Confidence:** Medium.

### D015 — Diacritic "mixed style" heuristic is Yoruba-specific and coarse

- **Decision:** The `diacritic_mixed_style` flag only fires for Yoruba
  entries that contain both a combining tone-mark character (grave/acute/
  circumflex, U+0300-U+0302) and a subdot character (ẹ ọ ṣ and their
  uppercase forms, or combining dot-below U+0323) in the same entry. It is
  not applied to Luganda, which (to this assistant's non-fluent knowledge)
  does not have an equivalent tone-mark-vs-subdot orthographic split.
- **Evidence or reasoning:** The brief specifically calls out that "Yoruba
  text may legitimately appear with full tone marks, with subdots only, or
  with none" — implying the mixed-style concern is about a single entry
  inconsistently combining conventions, which this narrowly targets.
- **Alternatives considered:** Applying the same check to Luganda —
  rejected without evidence Luganda has an analogous convention split;
  doing so could generate meaningless flags. Left as a documented gap
  rather than guessed at.
- **Risk:** This is a coarse proxy, not a real orthographic rule engine; it
  can miss genuine inconsistencies and can false-positive on legitimate
  text. Explicitly flagged as needing a fluent reviewer in validation.md.
- **Confidence:** Low — this assistant is not a fluent Yoruba or Luganda
  speaker; the independent language reviewers are the real check here.

### D016 — Default author assignment for Layer 2 cross-review

- **Decision:** `make_review_sheet.py` needs to know which author collected
  which entry to build "each author reviews the OTHER author's entries."
  Without a `--contributor-map` file, it defaults to: all Luganda entries
  belong to Author 1, all Yoruba entries belong to Author 2.
- **Evidence or reasoning:** This matches this specific project's actual
  design (one author per language, stated in the task brief's CONFIG
  section and `docs/TEAM_PLAN.md`), so it's a safe default that needs no
  extra file for the common case, while the `--contributor-map` CLI
  argument (a local, gitignored file) is still supported for correctness
  if that assumption ever stops holding.
- **Alternatives considered:** Requiring `--contributor-map` always —
  rejected as needless friction for a two-author/two-language project
  where the mapping is definitionally the language split.
- **Risk:** If the project ever adds a contributor who collects entries in
  a language they're not "the author of" (e.g. a helper), the default
  would misattribute those entries for cross-review purposes. Mitigated:
  documented in the script's docstring and `reports/review/README.md`,
  and overridable via `--contributor-map`.
- **Confidence:** High for this project's current design; explicitly a
  simplifying assumption, stated as such.

### D017 — Overlap-set size formula

- **Decision:** Overlap set size = `min(30, round(0.20 * total_entries))`,
  clipped to at least 1 and to the dataset size.
- **Evidence or reasoning:** The brief's exact wording is "at least 30
  entries (or 20% of the dataset, whichever is smaller, drawn from both
  languages)" — read as: the required minimum size is the SMALLER of 30
  and 20% of the dataset (so a small dataset isn't forced into an
  oversized overlap set, but a big dataset isn't left with a trivially
  small one either).
- **Alternatives considered:** `max(30, 20%)` — rejected, contradicts
  "whichever is smaller" explicitly in the text. A flat 30 regardless of
  dataset size — rejected, brief explicitly ties it to dataset size.
- **Risk:** At the target size (300-500 entries total across both
  languages), 20% is 60-100, so `min(30, 60-100) = 30` — the overlap set
  will typically just be 30 regardless of exact final size, which matches
  a plain reading of "at least 30."
- **Confidence:** Medium — the sentence is compact enough to admit more
  than one parsing; this is the most literal one.

### D018 — Layer 1 sample: union of flagged + random sample, not exclusive

- **Decision:** The Layer 1 random sample (seed 42, size
  `max(20% of language, 50)`) is drawn from the FULL per-language pool
  (including already-flagged items), then unioned with all flagged items —
  so the final sheet size can be less than "flagged + sample" if they
  overlap, but is never less than either alone.
- **Evidence or reasoning:** The brief says "ALL flagged items plus a
  random sample of at least 20%..." — "plus," not "plus, excluding
  flagged items." Sampling from the full pool (rather than only unflagged
  items) also means the random sample's statistical properties (e.g. for
  spot-checking general quality) reflect the whole language, not a
  flagged-biased subset.
- **Alternatives considered:** Sampling only from non-flagged items to
  guarantee the sheet size is exactly `flagged + sample_size` — rejected,
  would bias the "random" sample away from being representative of the
  language as a whole.
- **Risk:** None significant — worst case the sheet is a little smaller
  than the sum of the two targets when overlap is high, which is fine
  since both targets ("all flagged" and "at least N random") are still
  individually met.
- **Confidence:** High.

### D019 — Verdict vocabulary and agreement scope

- **Decision:** `reviewer_verdict` is expected to be one of `ok`,
  `needs_correction`, `reject` (documented in `reports/review/README.md`
  and `docs/VIVA_NOTES.md`). Agreement (percent + Cohen's kappa) is
  computed only over overlap ids where BOTH reviewers have filled in a
  non-blank verdict; incomplete ones are reported separately, not treated
  as a disagreement or excluded silently.
- **Evidence or reasoning:** The brief leaves the verdict vocabulary
  undefined but needs one for kappa to be meaningful (kappa requires
  discrete categories); a 3-way ok/needs_correction/reject scale is the
  simplest vocabulary that distinguishes "fine," "fixable," and
  "shouldn't be in the dataset," which covers what a Layer 2 English-side
  reviewer can actually judge. Restricting agreement stats to
  both-completed rows (rather than treating a blank as a category, or
  erroring) keeps the statistic honest and lets the report show real
  work-in-progress state.
- **Alternatives considered:** A free-text verdict with no fixed
  vocabulary — rejected, kappa becomes near-meaningless if every reviewer
  invents their own wording. Treating an incomplete row as automatic
  disagreement — rejected, conflates "haven't reviewed yet" with "reviewed
  and disagreed," which would misrepresent progress.
- **Risk:** If reviewers don't stick to the 3-value vocabulary, kappa
  still computes (the implementation handles arbitrary category strings)
  but the report becomes harder to interpret. Mitigated by stating the
  expected vocabulary prominently in the sheet README.
- **Confidence:** Medium — a reasonable default vocabulary, not specified
  in the brief.

### D020 — `reviewer_correction` mini-syntax

- **Decision:** `reviewer_correction` holds one or more `field: new value`
  clauses separated by ` | `, e.g. `translation_en: A better gloss` or
  `text: Fixed text | domain: proverb`. Recognised fields are the editable
  content/metadata fields (`text`, `translation_en`, `contributor_id`,
  `region`, `dialect`, `date_collected`, `source_type`, `domain`); `id`,
  `language`, and the review-status fields are never editable this way
  (status fields are derived by the script itself from which sheets
  reviewed the entry).
- **Evidence or reasoning:** The brief specifies the column exists and
  that "the reviewer_correction values" get applied, but not its format.
  A single free-text cell needs *some* convention to know which field a
  correction targets, since a reviewer might want to fix the translation,
  a metadata field, or (Layer 1 only) the text itself. A small
  human-writable `field: value` syntax is easy to type in a spreadsheet
  cell and easy to parse without a dependency.
- **Alternatives considered:** One review-sheet column per editable field
  — rejected, contradicts the brief's fixed column list ("Columns for all
  sheets: id, language, text, translation_en, auto_flags,
  reviewer_verdict, reviewer_correction, reviewer_notes"). Assuming
  `reviewer_correction` always corrects the single field the sheet is
  "about" — rejected, ambiguous for Layer 2 sheets which review multiple
  fields (translation, metadata, PII) at once.
- **Risk:** A reviewer typing free text without the `field:` prefix
  produces a correction that's silently ignored (no field recognised).
  Mitigated by documenting the syntax prominently in
  `reports/review/README.md` and each sheet's `.NOTE.md`.
- **Confidence:** Medium — a reasonable, simple convention; not specified
  by the brief.

### D021 — Corrections write a new file, never overwrite dataset.jsonl

- **Decision:** `apply_corrections.py` writes
  `data/processed/dataset_corrected.jsonl` and never modifies
  `data/processed/dataset.jsonl` in place.
- **Evidence or reasoning:** Keeping the preprocessing output immutable
  once written preserves a clear, re-runnable provenance chain (raw ->
  preprocessed -> corrected) and means re-running `preprocess.py` (e.g.
  after adding more raw data) can never silently clobber review work
  already recorded against a specific corrected version. `build_release.py`
  (Stage 5) is documented to prefer `dataset_corrected.jsonl` when present.
- **Alternatives considered:** Overwriting `dataset.jsonl` in place —
  rejected, destroys the distinction between "what preprocessing produced"
  and "what humans corrected," which matters for debugging and for the
  dataset card's "Preprocessing" vs. "Validation" sections being able to
  describe different things.
- **Risk:** An author could forget `dataset_corrected.jsonl` exists and
  keep working from `dataset.jsonl`. Mitigated: `build_release.py` picks
  the corrected file automatically when present and says so in its
  output.
- **Confidence:** High.

### D022 — `reviewed_by_independent` / `reviewer_id` bookkeeping after corrections

- **Decision:** After applying corrections, an entry is marked
  `reviewed = true` if it has a non-blank `reviewer_verdict` in ANY
  completed sheet. It is marked `reviewed_by_independent = true` only if
  its OWN language's Layer 1 sheet gave it a non-blank verdict — Layer 2
  (cross-author) review alone never sets this true, matching the schema's
  definition. `reviewer_id` is set to the Layer 1 reviewer's code
  (`R01`/`R02` per `docs/TEAM_PLAN.md`'s proposed defaults) when
  independently reviewed, else to whichever Layer 2 cross-reviewer
  (`R03`/`R04`) completed it, if any.
- **Evidence or reasoning:** Directly follows the schema field definition
  ("reviewed_by_independent: true only if reviewed by a fluent speaker who
  did not collect the entry"), which the pipeline is built to distinguish
  from Layer 2's English-side-only review.
- **Alternatives considered:** Leaving `reviewer_id` blank unless a real
  per-row reviewer code is threaded through the sheets — rejected as
  strictly less useful for a small two-team project where reviewer
  identity is 1:1 with which sheet/layer touched the row; the codes used
  here are exactly the ones `docs/TEAM_PLAN.md` proposes, so this is
  consistent rather than invented from nothing.
- **Risk:** If the authors deviate from the `R01`-`R04` code assignment in
  `TEAM_PLAN.md` (e.g. recruit a different reviewer with a different
  code), this hardcoded mapping in `apply_corrections.py` would need
  updating to match. Flagged here so it isn't missed.
- **Confidence:** Medium — correct given the current TEAM_PLAN defaults,
  brittle if those change without updating the script.

### D023 — Release gating signals: how build_release.py checks each condition

- **Decision:** `build_release.py` reads a specific literal line
  (`"PII check: PASS"` / `"PII check: FAIL"`) from `reports/validation.md`
  to gate on the PII check, treats any non-empty `reports/conflicts.csv`
  as unresolved conflicts, and refuses on any literal `"[FILL IN"`
  substring anywhere in the card file.
- **Evidence or reasoning:** The brief says build_release.py must "refuse
  to run if validation reports any failed PII check, if unresolved
  conflicts remain in reports/conflicts.csv, or if any placeholder text
  such as '[FILL IN]' remains in the card" — this implements each
  condition as literally and mechanically-checkably as possible, and
  `validate_auto.py` (Stage 4a) was deliberately written to emit that
  exact PII-check line for this script to key off.
- **Alternatives considered:** Re-running `validate_auto.py` from inside
  `build_release.py` to get a live PII check — rejected, would silently
  re-derive from whatever's in `data/processed/` rather than checking the
  validation report the authors actually looked at, and duplicates
  Stage 4a's logic.
- **Risk:** If someone hand-edits `reports/validation.md` to say PASS
  without re-running validation, or hand-deletes conflict rows without
  actually resolving them, this script can't detect that — it trusts the
  report files as given. This is inherent to a file-based gate; flagged
  here so the authors know not to hand-edit reports.
- **Confidence:** High that this matches the brief's literal requirement;
  medium on robustness against adversarial/careless report tampering
  (out of scope for a two-person course project).

### D024 — Release layout: combined + per-language directories

- **Decision:** `release/` gets a combined `dataset.jsonl`/`dataset.csv`
  at the top level, plus `release/lug/dataset_lug.{jsonl,csv}` and
  `release/yor/dataset_yor.{jsonl,csv}` in per-language subdirectories.
- **Evidence or reasoning:** The brief asks for "per-language files for
  the two configs" alongside the combined dataset, and Hugging Face
  Datasets commonly organises multi-config datasets with one subdirectory
  per config; this layout maps cleanly onto that without inventing
  Hugging Face `configs:` YAML wiring the authors haven't confirmed yet
  (see `docs/UPLOAD_GUIDE.md`, which explicitly leaves that manual step
  to the authors once they've decided on final naming).
- **Alternatives considered:** Flat files at the top level
  (`dataset_lug.jsonl`, `dataset_yor.jsonl` with no subdirectories) —
  considered simpler, but subdirectories make the "two configs" framing
  more visually explicit and avoid filename collisions if more file types
  are added later (e.g. a per-language card).
- **Risk:** None significant; this is a packaging convention, not a
  content decision, and easy to reorganise later if the authors want
  something else for the actual Hugging Face upload.
- **Confidence:** Medium — reasonable default, not the only valid choice.

### D025 — LICENSE file is a notice, not the full CC BY 4.0 legal code

- **Decision:** `release/LICENSE` contains a short CC BY 4.0 notice
  (rights granted, the attribution condition, links to the full legal
  text and human-readable summary) rather than reproducing the entire
  ~400-line CC BY 4.0 legal code text, and is explicitly marked
  "STATUS: PROPOSED."
- **Evidence or reasoning:** This is standard practice for CC-licensed
  datasets/repos (linking to the canonical, versioned legal text rather
  than vendoring a copy that could drift from the authoritative source),
  and keeps the file readable. The brief itself only says "proposed, to
  be confirmed by the authors" for the license, which this file states
  prominently at the top.
- **Alternatives considered:** Embedding the full legal code text —
  rejected as unnecessary bulk for a notice file whose job is to point to
  the authoritative, versioned source.
- **Risk:** None significant for a proposed/draft license notice.
- **Confidence:** High.

*(Further entries are appended in later stages as decisions come up —
schema field choices are in `docs/SCHEMA.md`'s rationale section and
summarised as D007+ below as validation, review and release stages are
built.)*
