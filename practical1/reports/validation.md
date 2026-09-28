# Validation Report — Practical I (Stage 4a, automatic)

Overall: ALL CHECKS PASSED

| Check | Result | Detail |
|---|---|---|
| valid_jsonl[train] | PASS | 1420 lines parsed OK |
| valid_jsonl[dev] | PASS | 200 lines parsed OK |
| valid_jsonl[test] | PASS | 403 lines parsed OK |
| token_tag_length_match[train] | PASS | OK |
| token_tag_length_match[dev] | PASS | OK |
| token_tag_length_match[test] | PASS | OK |
| valid_bio[train] | PASS | OK |
| valid_bio[dev] | PASS | OK |
| valid_bio[test] | PASS | OK |
| no_empty_sentences[train] | PASS | OK |
| no_empty_sentences[dev] | PASS | OK |
| no_empty_sentences[test] | PASS | OK |
| no_duplicate_sentences_within_split[train] | PASS | OK |
| no_duplicate_sentences_within_split[dev] | PASS | OK |
| no_duplicate_sentences_within_split[test] | PASS | OK |
| unique_ids[train] | PASS | OK |
| unique_ids[dev] | PASS | OK |
| unique_ids[test] | PASS | OK |
| cross_split_train_test_overlap_documented | PASS | 1 test sentence(s) also appear in train (kept intentionally, see DECISIONS.md D7): ['test-343'] |

Note: `cross_split_train_test_overlap_documented` is informational, not a pass/fail gate — its purpose is to make the known train/test leak (1 sentence, see DECISIONS.md D7) visible in this report rather than silently correct or silently ignored.