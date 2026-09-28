# Dataset Info — Practical I

## Source
- Repository: `masakhane-io/masakhane-ner`
- URL: https://github.com/masakhane-io/masakhane-ner
- Path used: `data/lug/` (MasakhaNER **1.0**, Luganda)
- Commit hash retrieved: `ba5843cd08aa491d5f96a5e809e71eb9ec461391`
- Commit date: 2025-10-15 16:37:20 -0400
- Retrieved: 2026-09-28 (this session), via `git clone --depth 1`

## Files and splits
Copied verbatim (byte-identical, verified by MD5) from `data/lug/` into `practical1/data/raw/`:

| File | Split | Lines (incl. blank sentence separators) |
|---|---|---|
| `train.txt` | train | 34,431 |
| `dev.txt`   | dev   | 3,971 |
| `test.txt`  | test  | 10,248 |

Format: CoNLL-style, whitespace-separated `TOKEN TAG` per line, blank line separates sentences.

MD5 checksums (raw/original == copied):
- train.txt: `eb2b2b6ed24401eb7f35f3e9470e0247`
- dev.txt: `03c881a9cd667bb0e29ac1da166ec2ca`
- test.txt: `cebccbf4d1e278617aa6f5a399738b7b`

## Primary or secondary data
**Secondary data.** This dataset was collected and annotated by the Masakhane community
(volunteer annotators, listed in `data/README.md` of the source repo, e.g. for Luganda:
Joyce Nabende, Jonathan Mukiibi, Eric Peter Kigaye, Ivan Ssenkungu, Ibrahim Mbabaali,
Batista Tobius, Maurice Katusiime, Deborah Nabagereka, Tobius Saolo) and published for reuse.
I did not collect or annotate any of it myself; I am reusing an existing public dataset,
which makes it secondary data for the purposes of this assignment.

## License
Copied verbatim from `LICENSE` (repository root) and confirmed by `data/README.md` line 7
("The license of the NER dataset is in [CC-BY-4.0-NC](https://creativecommons.org/licenses/by-nc/4.0/),
the monolingual data have difference licenses depending on the news website license.").

The `LICENSE` file itself contains two license texts back to back:
1. Apache License 2.0 — applies to the repository's **code** (HuggingFace-based training code),
   attributed: "The masakhane-NER code is based on the original tansformer code by the Hugging
   Face team and released under Apache 2: Copyright 2018- The Hugging Face team. All rights reserved."
2. Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) — applies to the
   **NER dataset** itself (the `data/` files, including `data/lug/`), starting at the line
   "Attribution-NonCommercial 4.0 International" (`LICENSE`, line 212 onward).

Verbatim excerpt of the section that applies to the dataset (from `LICENSE`, source repo root):

> Attribution-NonCommercial 4.0 International
>
> Creative Commons Corporation ("Creative Commons") is not a law firm and does not provide
> legal services or legal advice. Distribution of Creative Commons public licenses does not
> create a lawyer-client or other relationship. Creative Commons makes its licenses and related
> information available on an "as-is" basis. Creative Commons gives no warranties regarding its
> licenses, any material licensed under their terms and conditions, or any related information.
> Creative Commons disclaims all liability for damages resulting from their use to the fullest
> extent possible.
>
> [... full CC BY-NC 4.0 legal code follows in `LICENSE`, lines 212–610 of the source repository ...]

The README also notes: "the monolingual data have difference licenses depending on the news
website license" — i.e. the underlying news-source text may carry additional restrictions beyond
CC BY-NC 4.0 depending on which news outlet a given sentence came from. This detail is stated by
the source repo; I did not independently verify per-sentence provenance.

**Practical implication:** CC BY-NC 4.0 permits reuse with attribution for **non-commercial**
purposes only. This coursework use (Practical I, non-commercial, educational) is compliant.

## Citation
From the source repo's `README.md`:

```bibtex
@article{10.1162/tacl_a_00416,
    author = {Adelani, David Ifeoluwa and Abbott, Jade and Neubig, Graham and D’souza, Daniel and Kreutzer, Julia and Lignos, Constantine and Palen-Michel, Chester and Buzaaba, Happy and Rijhwani, Shruti and Ruder, Sebastian and Mayhew, Stephen and Azime, Israel Abebe and Muhammad, Shamsuddeen H. and Emezue, Chris Chinenye and Nakatumba-Nabende, Joyce and Ogayo, Perez and Anuoluwapo, Aremu and Gitau, Catherine and Mbaye, Derguene and Alabi, Jesujoba and Yimam, Seid Muhie and Gwadabe, Tajuddeen Rabiu and Ezeani, Ignatius and Niyongabo, Rubungo Andre and Mukiibi, Jonathan and Otiende, Verrah and Orife, Iroro and David, Davis and Ngom, Samba and Adewumi, Tosin and Rayson, Paul and Adeyemi, Mofetoluwa and Muriuki, Gerald and Anebi, Emmanuel and Chukwuneke, Chiamaka and Odu, Nkiruka and Wairagala, Eric Peter and Oyerinde, Samuel and Siro, Clemencia and Bateesa, Tobius Saul and Oloyede, Temilola and Wambui, Yvonne and Akinode, Victor and Nabagereka, Deborah and Katusiime, Maurice and Awokoya, Ayodele and MBOUP, Mouhamadane and Gebreyohannes, Dibora and Tilaye, Henok and Nwaike, Kelechi and Wolde, Degaga and Faye, Abdoulaye and Sibanda, Blessing and Ahia, Orevaoghene and Dossou, Bonaventure F. P. and Ogueji, Kelechi and DIOP, Thierno Ibrahima and Diallo, Abdoulaye and Akinfaderin, Adewale and Marengereke, Tendai and Osei, Salomey},
    title = "{MasakhaNER: Named Entity Recognition for African Languages}",
    journal = {Transactions of the Association for Computational Linguistics},
    volume = {9},
    pages = {1116-1131},
    year = {2021},
    month = {10},
    issn = {2307-387X},
    doi = {10.1162/tacl_a_00416},
    url = {https://doi.org/10.1162/tacl_a_00416},
}
```
