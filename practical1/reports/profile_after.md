# Profile: Processed Data (after preparation)

## Split: train

- Sentence count: 1420
- Token count: 32883
- Unique tokens: 11362
- Sentence length (tokens): min=1, median=21.0, mean=23.16, max=91
- Empty sentences: 0
- One-token sentences: 1
  - Examples: `.`/O (line 824)
- Exact duplicate sentence groups within split: 0 (0 extra instances beyond first occurrence)
- Sentences with Unicode issues (non-NFC / invisible / control / unusual whitespace / curly quotes): 0
  - None found.
- Invalid BIO sequences: 0
  - None found.
- Malformed lines (wrong column count): 0
  - None found.

- Label distribution:
  - O: 27862
  - B-PER: 1314
  - I-PER: 777
  - B-LOC: 673
  - B-ORG: 656
  - I-DATE: 527
  - I-ORG: 496
  - B-DATE: 427
  - I-LOC: 151

## Split: dev

- Sentence count: 200
- Token count: 3771
- Unique tokens: 2009
- Sentence length (tokens): min=6, median=17.0, mean=18.86, max=49
- Empty sentences: 0
- One-token sentences: 0
- Exact duplicate sentence groups within split: 0 (0 extra instances beyond first occurrence)
- Sentences with Unicode issues (non-NFC / invisible / control / unusual whitespace / curly quotes): 0
  - None found.
- Invalid BIO sequences: 0
  - None found.
- Malformed lines (wrong column count): 0
  - None found.

- Label distribution:
  - O: 3327
  - B-PER: 170
  - I-PER: 78
  - B-LOC: 56
  - I-DATE: 33
  - B-DATE: 32
  - B-ORG: 30
  - I-LOC: 23
  - I-ORG: 22

## Split: test

- Sentence count: 403
- Token count: 9758
- Unique tokens: 4501
- Sentence length (tokens): min=6, median=23, mean=24.21, max=67
- Empty sentences: 0
- One-token sentences: 0
- Exact duplicate sentence groups within split: 0 (0 extra instances beyond first occurrence)
- Sentences with Unicode issues (non-NFC / invisible / control / unusual whitespace / curly quotes): 0
  - None found.
- Invalid BIO sequences: 0
  - None found.
- Malformed lines (wrong column count): 0
  - None found.

- Label distribution:
  - O: 8353
  - B-PER: 376
  - I-PER: 222
  - B-LOC: 206
  - B-ORG: 151
  - I-DATE: 143
  - I-ORG: 111
  - B-DATE: 110
  - I-LOC: 86

## Cross-split exact duplicates

- train <-> test: 1 identical sentences
  - "Ye omubaka we Buvuma mu Palamenti Robert Migadde Ndugwa yagambye nti ebbanga dde..."
