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

*(Further entries are appended in later stages as decisions come up —
schema field choices are in `docs/SCHEMA.md`'s rationale section and
summarised as D007+ below as validation, review and release stages are
built.)*
