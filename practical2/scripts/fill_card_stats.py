#!/usr/bin/env python3
"""Stage 5b: print real per-language stats to paste into the dataset card.

Usage:
    python3 scripts/fill_card_stats.py [--dataset PATH]

Prefers data/processed/dataset_corrected.jsonl if it exists (the
human-reviewed, corrected dataset), else falls back to
data/processed/dataset.jsonl. Prints (does not write any file) per-language:
entry count, text length stats (chars), unique-token count, share of
entries containing a tone/diacritic mark, field completeness, contributor
count, reviewed share, independently-reviewed share.
"""
from __future__ import annotations

import argparse
import statistics
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def has_diacritic_or_tone_mark(text: str) -> bool:
    return any(unicodedata.category(ch) in ("Mn", "Mc") for ch in text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent.parent
    default_dataset = base / "data" / "processed" / "dataset_corrected.jsonl"
    if not default_dataset.exists():
        default_dataset = base / "data" / "processed" / "dataset.jsonl"
    parser.add_argument("--dataset", type=Path, default=default_dataset)
    args = parser.parse_args()

    rows = common.read_jsonl(args.dataset)
    if not rows:
        print(f"No entries found in {args.dataset}.")
        return 0

    print(f"Source: {args.dataset}")
    print(f"Total entries (all languages): {len(rows)}")
    print()

    by_lang: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_lang[row.get("language") or "(unknown)"].append(row)

    for lang in sorted(by_lang):
        lang_rows = by_lang[lang]
        n = len(lang_rows)
        lengths = [len(r.get("text") or "") for r in lang_rows]
        contributors = {r.get("contributor_id") for r in lang_rows if r.get("contributor_id")}
        with_marks = sum(1 for r in lang_rows if has_diacritic_or_tone_mark(r.get("text") or ""))
        reviewed = sum(1 for r in lang_rows if r.get("reviewed"))
        independent = sum(1 for r in lang_rows if r.get("reviewed_by_independent"))

        tokens = set()
        for r in lang_rows:
            tokens.update((r.get("text") or "").split())

        completeness = {}
        for field in common.ALL_FIELDS:
            filled = sum(1 for r in lang_rows if r.get(field) not in (None, "", False) or (field in common.BOOLEAN_FIELDS))
            completeness[field] = filled

        print(f"## {common.LANGUAGE_NAMES.get(lang, lang)} (`{lang}`)")
        print(f"- Entry count: {n}")
        if lengths:
            print(f"- Text length (chars): min={min(lengths)}, max={max(lengths)}, "
                  f"mean={statistics.mean(lengths):.1f}, median={statistics.median(lengths):.1f}")
        print(f"- Unique whitespace-delimited tokens: {len(tokens)}")
        print(f"- Entries containing a diacritic/tone/combining mark: {with_marks} ({with_marks/n*100:.1f}%)")
        print(f"- Distinct contributors: {len(contributors)}")
        print(f"- Reviewed (any layer): {reviewed} ({reviewed/n*100:.1f}%)")
        print(f"- Reviewed by independent language reviewer (Layer 1): {independent} ({independent/n*100:.1f}%)")
        print("- Field completeness (non-empty count / total):")
        for field in common.REQUIRED_FIELDS:
            print(f"    {field}: {completeness[field]}/{n}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
