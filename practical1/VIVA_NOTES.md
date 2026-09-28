# Viva Notes — Practical I

Anticipated questions a lecturer might ask, with answers drawn only from `DECISIONS.md` and the
`reports/` files (not invented after the fact). Where the honest answer is "this was a default"
or "I wasn't sure," that's stated plainly.

---

**Q: Why MasakhaNER 1.0 and not 2.0, when 2.0 is bigger and newer?**
A: The task instruction was to use whichever version was found first while browsing the
repository, not necessarily the best one. The source repo's own README lists "MasakhaNER 1.0 can
be found in... `data/`" before mentioning 2.0's location, and `data/lug/` is the simpler,
top-level path. This was a rule-following choice (D1), not a claim that 1.0 is better data —
in fact 2.0 is a larger, expanded annotation of the same language per the source paper, so a
production system would likely want 2.0 instead.

**Q: Why did you skip Unicode NFC normalisation? Doesn't all real-world text need it?**
A: Because Stage 2 profiling actually checked for it — comparing every sentence's text to its
NFC-normalised form, and separately scanning for zero-width/invisible/control characters and
unusual whitespace — and found zero instances in any of the three splits (D5). Applying a
normalisation step that changes nothing would be a no-op that still has to be logged as a "step,"
which the task explicitly said not to do for steps that aren't needed. If a different copy of
this dataset (or a different language's file) did have such issues, this would be the wrong
answer for that file — this is a claim about what this specific raw data contains, not a general
one.

**Q: Why did you keep the sentence that appears in both train and test, instead of just deleting
it from test?**
A: The task instruction was explicit: report any test sentences that also appear in train
"instead of silently deleting them from test" (D7). So the one overlapping sentence is flagged in
`changes.csv` and again in `validation.md` as an informational (non-failing) check, but left in
place. I did not independently decide this was the best ML-methodology choice — it's what was
asked for. The known cost is disclosed in REPORT.md section 6: it's a very small, single-sentence
leak.

**Q: Why didn't you repair every BIO tagging error you found?**
A: There were only 3 BIO errors total (all in train), and all 3 had the exact same, unambiguous
shape: an `I-<TYPE>` tag as the very first tag of a sentence, with literally no preceding token
it could be continuing. That's the specific case the task named as safe to auto-fix ("a leading
I- tag that should be B-"). No other BIO error pattern occurred in this dataset (D8) — I didn't
have to decide about a genuinely ambiguous case here, because none showed up. If a mid-sentence
`I-` following an unrelated `O` or a different entity type had appeared, I would not have
auto-fixed it; that's a real judgement call I'd have flagged in `bio_issues.csv` without
resolving it.

**Q: How do you know the BIO fix was correct and not, say, a missing continuation from a
previous, truncated sentence?**
A: I don't have independent confirmation of annotator intent — I can't fully rule that out. The
CoNLL format used here doesn't carry cross-sentence entity continuation, and these are treated as
standalone sentences, which makes the fix's correctness plausible but not proven (D8, "Risk"
section). I consider this medium-high confidence, not certainty.

**Q: How was the 100-sentence manual review sample chosen, and why that split (70/10/20)?**
A: Sample size 100 was specified directly by the task, not chosen by me. The 70/10/20 split
across train/dev/test is proportional to each split's share of the total raw sentence count
(1428/200/407 out of 2035 total), rounded to hit exactly 100 (D10). It was drawn from the *raw*
data (not processed) with a fixed random seed (42) so it's reproducible — anyone re-running
`scripts/sample_for_review.py` gets the identical 100 sentences.

**Q: Did you check for near-duplicate (not just exact-duplicate) sentences?**
A: No — and I want to be precise about this: I didn't run any fuzzy-similarity check, so I have
no evidence either way about whether near-duplicates exist (D11). This is different from the
Unicode/whitespace checks above, where I actually looked and found nothing. It's an honest gap in
scope, not a "checked, none found" result. The task's Stage 3 candidate list only specified exact
duplicate removal, so I didn't build a similarity-threshold detector without a stated reason to.

**Q: Why does the processed data have fewer unique tokens counted the same as before (11,362 for
train in both before and after)?**
A: Because the only preprocessing steps applied were removing 8 whole duplicate sentences and
changing a handful of tag characters (not token text) in 3 sentences. Removing already-duplicated
sentences doesn't remove any token *types* that don't also appear elsewhere in the (now smaller)
corpus, in this dataset's case — the vocabulary happened to stay identical. That's an observation
from the numbers, not something I engineered.

**Q: What would you do differently if you ran this again?**
A: I'd flag that MasakhaNER 2.0 (the larger version) exists and is likely the better choice for
anyone actually training a model on this data, even though the task rules pointed me to 1.0
here (D1). I'd also consider whether a near-duplicate check is worth doing for news-sourced text
specifically, since wire-service republishing is a plausible source of near-duplicates that exact
matching wouldn't catch (D11) — I didn't do this here because it wasn't asked for, not because I
checked and it wasn't needed.
