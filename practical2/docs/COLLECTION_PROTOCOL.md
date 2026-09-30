> **DRAFT — to be reviewed and adapted by both authors.** Follow our
> course's ethics guidance where it differs from this draft.

# Collection protocol

This is the working procedure for collecting entries for the dataset. It
exists so that both authors collect consistently, even though neither can
verify the other's language.

> **This protocol covers consented human collection only.** As of
> 2026-09-29, entries may also be sourced by scraping openly-licensed
> websites (lecturer-approved — see DECISIONS.md D026), which follows a
> different process (no consent form, since no individual is contributing
> personal data — instead source attribution and license tracking; see
> `scripts/scrape_source.py` and `docs/SCHEMA.md`'s `source_url`/
> `site_name`/`source_license`/`translation_source` fields). The
> DATA SAFETY RULES below (no PII, no private individuals) still apply
> fully to scraped text.

## 1. Before collecting: consent

1. Read (or paraphrase accurately) `CONSENT_FORM.md` to the contributor in
   their own language, before asking for anything.
2. Only proceed if they agree. Do not pressure a hesitant contributor.
3. Do not record their name or any identifier alongside their consent —
   just note, in your own private working notes (not in the repo, not in
   any data file), that contributor `C0xx` consented on `[date]`. See
   Section 4 for how anonymous IDs work.

## 2. What to collect

- Short sentences, phrases, or proverbs in the contributor's language
  (Rukiga for Author 1's contributors, Yoruba for Author 2's).
- Aim for entries that are self-contained and make sense out of context.
- Target: 150–250 entries per language in total across all contributors
  (see `TEAM_PLAN.md` for how this is split across contributors/sessions).

## 3. What to avoid — never collect or write down

Do not include, anywhere in `text`, `translation_en`, `region`, `dialect`,
or `domain`:

- Personal information: full names, nicknames that identify a specific
  private person, phone numbers, addresses, email addresses, ID/account
  numbers.
- Names of private individuals (a well-known public figure mentioned
  neutrally in a proverb is fine; a private person's name is not).
- Health, medical, or other sensitive personal details about anyone,
  contributor or not.
- Offensive, hateful, or harassing content.
- Anything the contributor says is private or that you would not want
  published under an open license forever.

If a contributor offers something like this, thank them and simply don't
record that particular item — you don't need to explain in detail why,
just that it's outside what we can collect for this project.

## 4. Anonymous contributor IDs — never store identity

- Assign each contributor a sequential code: `C001`, `C002`, ... within
  your own collection (Author 1 and Author 2 keep separate sequences, or a
  shared spreadsheet with an agreed next-number — see `TEAM_PLAN.md`).
- Only the code goes into `data/raw/*.csv`.
- If you personally need to remember which code belongs to which
  contributor (e.g. to follow up with them, or to pay/thank them), keep
  that mapping in a file **outside this git repository** — for example in
  your own private notes app, or in a local file that matches the pattern
  `*contributor_map*` (which `.gitignore` blocks from being committed even
  if you put it inside the repo folder by mistake). Never email, message,
  or paste that mapping anywhere public.
- The same applies to `reviewer_id` codes (`R01`, `R02`, ...) for Layer 1
  independent reviewers — see `TEAM_PLAN.md`.

## 5. Recording consent without storing identity

Keep a simple private tally (outside the repo) of: contributor code,
date, language, and "consented: yes". Do not add a name. This is enough to
demonstrate consent was obtained without ever putting identity in the
dataset.

## 6. Writing the English translation

- Translate for **meaning**, not word-for-word. A grammatically odd but
  accurate word-for-word translation is less useful than a natural English
  sentence that captures what the original actually means.
- For proverbs or idioms with no direct English equivalent: translate the
  literal meaning as best you can, and you may add a short bracketed note,
  e.g. `He who visits the village benefits from it later. [meaning: value
  of maintaining relationships/connections]`.
- `translation_en` is **required** for every entry — never leave it blank
  (see `DECISIONS.md` D003).
- Because neither author reads the other's language, translation quality
  for the *other* author's language can only be checked by: (a) the
  independent Layer 1 reviewer for that language, and (b) whether the
  English reads sensibly on its own (Layer 2, both authors can check
  this). Keep translations clear enough that a non-speaker cross-reviewer
  can sanity-check the English even without understanding the source text.

## 7. Filling in the row

See `FILLING_GUIDE.md` for the column-by-column guide and
`raw_template.csv` for the template. Save your file as
`data/raw/raw_<lang>_<authorN>.csv`.

## 8. After collection

Hand your raw CSV(s) to the pipeline (`scripts/preprocess.py`) — see the
top-level `practical2/README.md` for the exact command. Do not hand-edit
`data/raw/*.csv` after this point except to append new rows; the pipeline
treats `data/raw/` as the untouched source of truth.
