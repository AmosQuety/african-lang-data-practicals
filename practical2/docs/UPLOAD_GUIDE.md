> **DRAFT — to be reviewed and adapted by both authors.** This is a guide
> for the authors to follow by hand. Nothing in this repository uploads
> anything automatically.

# Upload guide

Complete `scripts/build_release.py` successfully first — it refuses to
run if the PII check hasn't passed, if `reports/conflicts.csv` has
unresolved rows, or if the dataset card still has `[FILL IN]`
placeholders. Only upload the contents of `release/` once it built
cleanly and both authors have gone through `docs/ETHICS_CHECKLIST.md`.

## Hugging Face Datasets (primary target)

1. **Create an account / organisation.** The dataset can be created under
   one author's personal account, or under a shared Hugging Face
   organisation both authors join. An organisation is usually easier for
   joint ownership — create one at https://huggingface.co/organizations/new
   and add the other author as a member.
2. **Create a token.** In Hugging Face account settings → Access Tokens,
   create a token with **write** access. Do not share this token or paste
   it into any file in this repo — it is read only from the `HF_TOKEN`
   environment variable.
3. **Add the other author as a collaborator** (if uploading under a
   personal account rather than an organisation): on the dataset repo
   page, Settings → Collaborators → add their Hugging Face username with
   Write access.
4. **Run the upload, by hand, locally** (not from an unattended session):
   ```bash
   export HF_TOKEN=hf_your_token_here
   python3 scripts/upload_to_hf.py --repo-id <username-or-org>/<dataset-name>
   ```
   Add `--private` first if you want to review the uploaded repo before
   making it public — you can flip it to public later in the repo
   settings once you're both happy with it.
5. **Check the rendered dataset card** on the Hugging Face page — the
   YAML front matter in `release/README.md` drives the "Languages",
   "License" etc. metadata badges; make sure they rendered as expected.
6. **Configs:** this release ships `dataset.jsonl`/`.csv` (combined) plus
   `lug/dataset_lug.jsonl` and `yor/dataset_yor.jsonl` (per-language). If
   you want these to appear as separate selectable "configs" in the HF
   dataset viewer, add a `configs:` section to the YAML front matter
   pointing at each file (see Hugging Face's "Manual configuration" docs)
   — this wasn't hardcoded into the card template since we don't yet know
   the final directory layout you'll want; do this by hand once uploaded.

## Alternatives, if you switch away from Hugging Face

### GitHub (e.g. a dedicated dataset release, or GitHub Releases)

- Simplest option: commit `release/` to a repo (this one, or a new public
  one) and tag a release, attaching `release/dataset.jsonl` and
  `release/dataset.csv` as release assets.
- `git tag -a v1.0 -m "Practical 2 dataset release" && git push --tags`,
  then use `gh release create v1.0 release/dataset.jsonl release/dataset.csv --notes-file release/README.md`.

### Zenodo

- Zenodo is good if you want a DOI (useful for citation). Create an
  account, connect your GitHub repo (Zenodo can auto-archive a GitHub
  release), or upload `release/` directly as a new "Dataset" upload at
  https://zenodo.org/deposit/new. Fill in the same metadata (license,
  languages, description) from `release/README.md`.

### Kaggle

- Create a new Dataset at https://www.kaggle.com/datasets, upload the
  files in `release/`, and paste the summary/description/license from
  `release/README.md`. Kaggle datasets support versioning if you update
  later.

## After uploading

- Update `release/README.md` (or the repo's live copy) with the actual
  dataset URL if you want it cross-referenced.
- Keep `HF_TOKEN` (or any other credential) out of this repository,
  always.
