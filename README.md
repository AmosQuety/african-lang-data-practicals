# african-lang-data-practicals

Coursework for a data curation course, working with datasets for African languages.
This repository is a set of learning exercises. It is not a dataset release.

## Disclaimer

The data in this repository was prepared as part of a course experiment. It has been
cleaned and reformatted for practice only, and its quality has not been validated for any
other purpose.

**Do not use this data to train, evaluate, or benchmark models.** For any real use, obtain
the original dataset from its source below.

## Practical 1: Luganda named entity recognition

| | |
|---|---|
| Dataset | MasakhaNER 1.0, Luganda (`lug`) subset |
| Original source | https://github.com/masakhane-io/masakhane-ner (`data/lug/`) |
| Source commit | `ba5843cd08aa491d5f96a5e809e71eb9ec461391` |
| Original creators | The Masakhane community; see the citation below |
| Licence of the data | CC BY-NC 4.0 (Attribution-NonCommercial) |
| Data type | Secondary data (collected and annotated by others) |

### Terms of use

- The data is licensed by its creators under
  [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Use is non-commercial
  only, and the original creators must be credited.
- The source repository notes that the underlying news text may carry further restrictions
  depending on the website it came from. Check the original repository before any reuse.
- The files under `practical1/data/processed/` are modified copies of the originals
  (duplicates removed, tags repaired, format changed). The changes are listed in
  `practical1/reports/before_after_table.md` and `practical1/reports/changes.csv`. The
  unmodified originals are in `practical1/data/raw/`.
- The licence in the source repository covers the dataset it released. It does not cover the
  analysis scripts and reports written for this coursework.

### Citation

If you use the original dataset, cite its authors:

> Adelani et al. (2021). MasakhaNER: Named Entity Recognition for African Languages.
> Transactions of the Association for Computational Linguistics, 9, 1116-1131.
> https://doi.org/10.1162/tacl_a_00416

The full BibTeX entry is in `practical1/DATASET_INFO.md`.

### Known limitations

- Entity labels and span boundaries were not checked by hand. Tags were only checked for
  valid BIO sequences (see `practical1/REPORT.md`).
- The manual review covered 100 sentences, so it is a sample and not a full audit.
- Near-duplicate sentences were not checked for.

## Where to look

- `practical1/REPORT.md`: the write-up of the preparation pipeline.
- `practical1/DATASET_INFO.md`: full provenance, checksums and licence text.
- `practical1/README.md`: folder layout and how to re-run the pipeline.
