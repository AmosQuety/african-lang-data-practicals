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

*(Further entries are appended in later stages as decisions come up —
schema field choices are in `docs/SCHEMA.md`'s rationale section and
summarised as D007+ below as validation, review and release stages are
built.)*
