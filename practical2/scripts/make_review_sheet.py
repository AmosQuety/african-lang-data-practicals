#!/usr/bin/env python3
"""Stage 4b: build reproducible (seed 42) two-layer manual review sheets.

Usage:
    python3 scripts/make_review_sheet.py [--dataset PATH] [--flags PATH]
        [--out-dir REPORTS/review] [--contributor-map PATH]

LAYER 1 (per-language, independent language review):
    reports/review/layer1_<lang>.csv — ALL flagged items for that language
    plus a random sample of at least max(20% of language entries, 50
    entries) per language (seed 42). Meant for a fluent speaker who did
    NOT collect the entries (see docs/TEAM_PLAN.md for reviewer codes). If
    no independent reviewer exists for a language, leave
    reviewed_by_independent=false for those entries when applying
    corrections — see docs/DATASET_CARD note and reports/review/README.md.

LAYER 2 (cross-review between the two authors, English-side only):
    reports/review/layer2_by_author1.csv — Author 1 reviews Author 2's
        entries, PLUS the shared overlap set.
    reports/review/layer2_by_author2.csv — Author 2 reviews Author 1's
        entries, PLUS the shared overlap set.
    Both sheets state at the top (and in reports/review/README.md) that
    this layer does NOT verify target-language correctness.

--contributor-map PATH: optional CSV with columns contributor_id,author
mapping each contributor_id to 'author1' or 'author2'. If omitted, this
script falls back to the project's default assignment (Author 1 collects
Rukiga, Author 2 collects Yoruba — see docs/TEAM_PLAN.md), which is
correct for the two-author/two-language design in this repo but would
need a real mapping if that assumption ever changes. This path is never
committed (see .gitignore's '*contributor_map*' pattern).

All columns for every sheet: id, language, text, translation_en,
auto_flags, reviewer_verdict, reviewer_correction, reviewer_notes (last
three blank, for the reviewer to fill in).
"""
from __future__ import annotations

import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

SEED = 42
LAYER1_MIN_FRACTION = 0.20
LAYER1_MIN_COUNT = 50
OVERLAP_MAX_COUNT = 30
OVERLAP_FRACTION = 0.20

SHEET_COLUMNS = ["id", "language", "text", "translation_en", "auto_flags",
                 "reviewer_verdict", "reviewer_correction", "reviewer_notes"]


def load_flags_by_id(flags_path: Path) -> dict[str, list[str]]:
    flags_by_id: dict[str, list[str]] = defaultdict(list)
    if not flags_path.exists():
        return flags_by_id
    for row in common.read_csv(flags_path):
        flags_by_id[row["id"]].append(row["check"])
    return flags_by_id


def to_sheet_row(row: dict, flags_by_id: dict[str, list[str]]) -> dict:
    return {
        "id": row.get("id", ""),
        "language": row.get("language", ""),
        "text": row.get("text", ""),
        "translation_en": row.get("translation_en", ""),
        "auto_flags": "; ".join(flags_by_id.get(row.get("id", ""), [])),
        "reviewer_verdict": "",
        "reviewer_correction": "",
        "reviewer_notes": "",
    }


def build_layer1_sheets(rows_by_lang: dict[str, list[dict]], flags_by_id: dict, rng: random.Random):
    sheets = {}
    for lang, rows in rows_by_lang.items():
        flagged_ids = {r["id"] for r in rows if flags_by_id.get(r["id"])}
        target_size = max(int(len(rows) * LAYER1_MIN_FRACTION + 0.999), LAYER1_MIN_COUNT)
        target_size = min(target_size, len(rows))
        pool = sorted(rows, key=lambda r: r["id"])  # deterministic order before shuffling
        sample = rng.sample(pool, target_size) if target_size < len(pool) else list(pool)
        sample_ids = {r["id"] for r in sample}
        chosen_ids = flagged_ids | sample_ids
        chosen_rows = [r for r in rows if r["id"] in chosen_ids]
        chosen_rows.sort(key=lambda r: r["id"])
        sheets[lang] = [to_sheet_row(r, flags_by_id) for r in chosen_rows]
    return sheets


def load_contributor_map(path: Path | None) -> dict[str, str] | None:
    if path is None:
        return None
    if not path.exists():
        print(f"WARNING: --contributor-map path {path} does not exist; falling back to default language-based assignment.")
        return None
    mapping = {}
    for row in common.read_csv(path):
        cid = row.get("contributor_id", "").strip()
        author = row.get("author", "").strip()
        if cid and author:
            mapping[cid] = author
    return mapping


def default_author_for_language(lang: str) -> str | None:
    # Project default (docs/TEAM_PLAN.md): Author 1 collects Rukiga,
    # Author 2 collects Yoruba.
    return {"cgg": "author1", "yor": "author2"}.get(lang)


def assign_authors(rows: list[dict], contributor_map: dict[str, str] | None) -> dict[str, str]:
    """Returns {row_id: author} for every row."""
    result = {}
    for row in rows:
        cid = row.get("contributor_id", "")
        author = None
        if contributor_map is not None:
            author = contributor_map.get(cid)
        if author is None:
            author = default_author_for_language(row.get("language", ""))
        result[row["id"]] = author or "unknown"
    return result


def build_overlap_set(rows: list[dict], rng: random.Random) -> list[dict]:
    total = len(rows)
    target = min(OVERLAP_MAX_COUNT, max(1, round(total * OVERLAP_FRACTION)))
    target = min(target, total)
    pool = sorted(rows, key=lambda r: r["id"])
    sample = rng.sample(pool, target) if target < len(pool) else list(pool)
    return sample


def build_layer2_sheets(rows: list[dict], flags_by_id: dict, author_of: dict[str, str],
                          overlap_rows: list[dict]):
    overlap_ids = {r["id"] for r in overlap_rows}
    by_author1 = []
    by_author2 = []
    for row in rows:
        author = author_of.get(row["id"])
        if author == "author2":
            by_author1.append(row)  # author1 reviews author2's entries
        elif author == "author1":
            by_author2.append(row)  # author2 reviews author1's entries
    # add overlap set to both (dedup by id, overlap entries may already be present)
    existing1 = {r["id"] for r in by_author1}
    existing2 = {r["id"] for r in by_author2}
    for r in overlap_rows:
        if r["id"] not in existing1:
            by_author1.append(r)
        if r["id"] not in existing2:
            by_author2.append(r)
    by_author1.sort(key=lambda r: r["id"])
    by_author2.sort(key=lambda r: r["id"])
    sheet1 = [to_sheet_row(r, flags_by_id) for r in by_author1]
    sheet2 = [to_sheet_row(r, flags_by_id) for r in by_author2]
    return sheet1, sheet2, overlap_ids


def write_sheet_with_note(path: Path, note: str, rows: list[dict]) -> None:
    """Writes the CSV sheet, and a matching .NOTE.md file carrying the
    required caveat text (kept out of the CSV itself so it stays a clean,
    strictly-columned file for spreadsheet tools)."""
    common.write_csv(path, SHEET_COLUMNS, rows)
    note_path = path.with_suffix(".NOTE.md")
    note_path.write_text(note, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--dataset", type=Path, default=base / "data" / "processed" / "dataset.jsonl")
    parser.add_argument("--flags", type=Path, default=base / "reports" / "flags.csv")
    parser.add_argument("--out-dir", type=Path, default=base / "reports" / "review")
    parser.add_argument("--contributor-map", type=Path, default=None,
                         help="Optional local CSV (contributor_id,author) — never committed.")
    args = parser.parse_args()

    rows = common.read_jsonl(args.dataset)
    if not rows:
        print("No entries in dataset; nothing to build review sheets from.")
        return 0
    flags_by_id = load_flags_by_id(args.flags)

    rows_by_lang: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        rows_by_lang[row.get("language", "")].append(row)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Layer 1 (fresh RNG per invocation, but seeded identically -> reproducible)
    layer1_sheets = build_layer1_sheets(rows_by_lang, flags_by_id, random.Random(SEED))
    for lang, sheet_rows in layer1_sheets.items():
        note = (
            f"# Layer 1 review — {common.LANGUAGE_NAMES.get(lang, lang)} (`{lang}`)\n\n"
            "This sheet is for a **fluent speaker of this language who did NOT "
            "collect these entries** (an independent reviewer — see "
            "docs/TEAM_PLAN.md for the reviewer code). They check target-language "
            "correctness, meaning, appropriateness, and whether the English "
            "translation is faithful.\n\n"
            "If no independent reviewer is available for this language, do not "
            "fill this sheet in as a substitute using the collecting author — "
            "leave `reviewed_by_independent=false` for these entries and record "
            "that limitation in the dataset card (docs template already includes "
            "this as a mandatory limitation).\n\n"
            "Contains every entry auto-flagged for this language, plus a "
            f"reproducible (seed {SEED}) random sample of at least "
            f"max({int(LAYER1_MIN_FRACTION*100)}%, {LAYER1_MIN_COUNT}) entries.\n"
        )
        write_sheet_with_note(args.out_dir / f"layer1_{lang}.csv", note, sheet_rows)
        print(f"Layer 1 [{lang}]: {len(sheet_rows)} entries -> {args.out_dir / f'layer1_{lang}.csv'}")

    # Layer 2
    contributor_map = load_contributor_map(args.contributor_map)
    author_of = assign_authors(rows, contributor_map)
    overlap_rows = build_overlap_set(rows, random.Random(SEED))
    sheet1, sheet2, overlap_ids = build_layer2_sheets(rows, flags_by_id, author_of, overlap_rows)

    layer2_note_common = (
        "**This layer does NOT verify target-language (Rukiga/Yoruba) "
        "correctness.** The reviewing author does not read the other "
        "author's language. Only check: (1) does the English translation "
        "read sensibly on its own, (2) any possible PII, (3) metadata "
        "fields look sane, (4) any auto_flags that can be judged without "
        "reading the source language. If a correction would change the "
        "`text` field (the original-language text itself), do NOT make it "
        "here — leave a note; scripts/apply_corrections.py routes any "
        "Layer 2 correction touching `text` to reports/conflicts.csv for "
        "the language's independent reviewer or collector to decide.\n\n"
    )

    write_sheet_with_note(
        args.out_dir / "layer2_by_author1.csv",
        "# Layer 2 review — by Author 1 (reviews Author 2's entries)\n\n" + layer2_note_common +
        f"Includes Author 2's entries plus the shared overlap set (reproducible, seed {SEED}, "
        f"{len(overlap_ids)} entries) also reviewed by Author 2, for agreement measurement.\n",
        sheet1,
    )
    write_sheet_with_note(
        args.out_dir / "layer2_by_author2.csv",
        "# Layer 2 review — by Author 2 (reviews Author 1's entries)\n\n" + layer2_note_common +
        f"Includes Author 1's entries plus the shared overlap set (reproducible, seed {SEED}, "
        f"{len(overlap_ids)} entries) also reviewed by Author 1, for agreement measurement.\n",
        sheet2,
    )
    common.write_csv(
        args.out_dir / "overlap_ids.csv",
        ["id"],
        [{"id": i} for i in sorted(overlap_ids)],
    )

    readme = build_readme(rows_by_lang, layer1_sheets, sheet1, sheet2, overlap_ids, contributor_map is not None)
    (args.out_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"Layer 2 [by author1]: {len(sheet1)} entries")
    print(f"Layer 2 [by author2]: {len(sheet2)} entries")
    print(f"Overlap set: {len(overlap_ids)} entries (reviewed by both authors)")
    print(f"Wrote {args.out_dir / 'README.md'}")
    return 0


def build_readme(rows_by_lang, layer1_sheets, sheet1, sheet2, overlap_ids, used_real_map) -> str:
    lines = ["# Review sheets — how to use them", ""]
    lines.append(f"Generated reproducibly with random seed {SEED}: re-running "
                  "`scripts/make_review_sheet.py` on the same dataset and flags "
                  "produces the same sheets.")
    lines.append("")
    lines.append("## Layer 1 — independent language review (per language)")
    lines.append("")
    for lang, rows in layer1_sheets.items():
        total = len(rows_by_lang.get(lang, []))
        lines.append(f"- `layer1_{lang}.csv` ({common.LANGUAGE_NAMES.get(lang, lang)}): "
                      f"{len(rows)} of {total} entries. See `layer1_{lang}.NOTE.md`.")
    lines.append("")
    lines.append("## Layer 2 — cross-review between the two authors (English-side only)")
    lines.append("")
    lines.append(f"- `layer2_by_author1.csv`: {len(sheet1)} entries. See `layer2_by_author1.NOTE.md`.")
    lines.append(f"- `layer2_by_author2.csv`: {len(sheet2)} entries. See `layer2_by_author2.NOTE.md`.")
    lines.append(f"- Shared overlap set: {len(overlap_ids)} entries, present in BOTH Layer 2 sheets "
                  "(see `overlap_ids.csv`) — used by `scripts/compute_agreement.py` to measure "
                  "inter-reviewer agreement.")
    if not used_real_map:
        lines.append("")
        lines.append("**Note:** no `--contributor-map` was supplied, so author assignment used the "
                      "project default (Author 1 = Rukiga collector, Author 2 = Yoruba collector, "
                      "per docs/TEAM_PLAN.md). Pass `--contributor-map path/to/local/file.csv` "
                      "(never committed) if contributors ever span both languages/authors.")
    lines.append("")
    lines.append("## All sheets share these columns")
    lines.append("")
    lines.append("`" + ", ".join(SHEET_COLUMNS) + "`")
    lines.append("")
    lines.append("`reviewer_verdict`, `reviewer_correction`, and `reviewer_notes` start blank — "
                  "reviewers fill these in. `reviewer_verdict` is free text but "
                  "`scripts/apply_corrections.py` and `scripts/compute_agreement.py` expect "
                  "one of: `ok`, `needs_correction`, `reject` (see docs/VIVA_NOTES.md).")
    lines.append("")
    lines.append("Once sheets are completed, run `scripts/compute_agreement.py` (on the two "
                  "Layer 2 sheets) and `scripts/apply_corrections.py` (on all completed sheets).")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
