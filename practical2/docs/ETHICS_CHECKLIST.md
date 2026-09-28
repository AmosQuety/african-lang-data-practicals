> **DRAFT — to be reviewed and adapted by both authors.** Follow our
> course's ethics guidance where it differs from this draft.

# Ethics checklist — tick before release

Go through this list together before running `scripts/build_release.py`
for real (not just on test fixtures). Do not check an item unless it is
actually true.

## Consent

- [ ] Every contributor was read/told the consent text (`CONSENT_FORM.md`)
      in their own language before contributing.
- [ ] No contributor who asked to withdraw before release is still
      represented in `data/raw/` or `data/processed/`.
- [ ] Contact details in `CONSENT_FORM.md` are filled in and correct.

## Anonymity

- [ ] No real name, phone number, email, address, or other personal
      identifier appears in any file under `data/`, `release/`, or
      `reports/`.
- [ ] No file mapping `contributor_id`/`reviewer_id` to a real identity has
      been committed to the repo (`git log --all -- '*contributor_map*'
      '*reviewer_map*' '*id_map*'` should return nothing).
- [ ] `scripts/validate_auto.py`'s PII checks have been run on the final
      data and any flagged items in `reports/flags.csv` have been reviewed
      by a human, not just auto-ignored.

## Content

- [ ] No entry contains content either author, or either language's
      independent reviewer, flags as offensive, hateful, or harassing.
- [ ] No entry names a private individual in a way that could embarrass or
      expose them.

## Review coverage (be honest — see DECISIONS.md)

- [ ] We know, per language, what share of entries were reviewed by an
      independent fluent speaker (Layer 1) vs. only cross-reviewed on the
      English side (Layer 2) vs. not reviewed at all, and this is
      accurately stated in the dataset card's limitations section.
- [ ] If either language had no independent reviewer, the dataset card's
      mandatory limitation says so explicitly (it is not hidden or
      softened).

## License and attribution

- [ ] License section of the dataset card matches what we've actually
      agreed with contributors via the consent form (currently CC BY 4.0,
      proposed).
- [ ] Authors and contributions section reflects who actually did what
      (see `TEAM_PLAN.md`'s CONTRIBUTIONS section).

## Technical

- [ ] `scripts/validate_auto.py` reports no failed checks that we haven't
      consciously decided to accept (and documented why in
      `DECISIONS.md`).
- [ ] `reports/conflicts.csv` is empty or every row has been resolved.
- [ ] `release/README.md` (the filled dataset card) contains no leftover
      `[FILL IN]` placeholders.
- [ ] `scripts/build_release.py` completed without refusing to run.

## Final check

- [ ] Both authors have read the finished `release/README.md` end to end.
- [ ] We are both comfortable with this being public, indefinitely, under
      the stated license.
