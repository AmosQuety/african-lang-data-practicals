# Profile: Raw Data (before preparation)

## Split: train

- Sentence count: 1428
- Token count: 33003
- Unique tokens: 11362
- Sentence length (tokens): min=1, median=21.0, mean=23.11, max=91
- Empty sentences: 0
- One-token sentences: 1
  - Examples: `.`/O (line 19929)
- Exact duplicate sentence groups within split: 8 (8 extra instances beyond first occurrence)
  - "Sizoni ewedde baamalira mu kyamwenda ku ttiimu 21 ." x2
  - "Bali ku nnamba Dr . Katende 0701891189 oba Nkuubi ku 0772672551 ." x2
  - "Mu kiseera kino Kawala akyapooca nebiwundu mu ddwaaliro e Kiruddu ." x2
- Sentences with Unicode issues (non-NFC / invisible / control / unusual whitespace / curly quotes): 0
  - None found.
- Invalid BIO sequences: 3
  - line 6309: "Amagatte bibiri ebivunaanyizibwa ku byemmere okuli ekya Food and Agriculture Org..." -> 'I-ORG' follows 'O' (I- tag with no preceding B-/I- of same type)
  - line 17415: "Wabwire nabatebuka namuddusa ku kitebe kya poliisi eMpigi gya kuumirwa mu byokwe..." -> 'I-PER' follows 'O' (I- tag with no preceding B-/I- of same type)
  - line 25539: "Azira ne Farouk Miya wabadde tewakola bulungi kuba baalemeddwa wadde okukubayo p..." -> 'I-PER' follows 'O' (I- tag with no preceding B-/I- of same type)
- Malformed lines (wrong column count): 0
  - None found.

- Label distribution:
  - O: 27964
  - B-PER: 1319
  - I-PER: 780
  - B-LOC: 678
  - B-ORG: 655
  - I-DATE: 530
  - I-ORG: 497
  - B-DATE: 429
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

- Sentence count: 407
- Token count: 9841
- Unique tokens: 4501
- Sentence length (tokens): min=6, median=23, mean=24.18, max=67
- Empty sentences: 0
- One-token sentences: 0
- Exact duplicate sentence groups within split: 4 (4 extra instances beyond first occurrence)
  - "Tujja kukutuusaako ebisingawo ku ggulire lino ." x2
  - "Akulira poliisi ye Mpigi , Erias Twesigye agambye nti Ssebunya agguddwaako omusa..." x2
  - "Cooperative eyasooka okuwandiikibwa mu 1964 , eyawandiikibwa mu 1997 yeddiza eby..." x2
- Sentences with Unicode issues (non-NFC / invisible / control / unusual whitespace / curly quotes): 0
  - None found.
- Invalid BIO sequences: 0
  - None found.
- Malformed lines (wrong column count): 0
  - None found.

- Label distribution:
  - O: 8422
  - B-PER: 379
  - I-PER: 223
  - B-LOC: 209
  - B-ORG: 153
  - I-DATE: 143
  - B-DATE: 113
  - I-ORG: 113
  - I-LOC: 86

## Cross-split exact duplicates

- train <-> test: 1 identical sentences
  - "Ye omubaka we Buvuma mu Palamenti Robert Migadde Ndugwa yagambye nti ebbanga dde..."
