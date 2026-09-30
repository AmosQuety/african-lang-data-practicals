#!/usr/bin/env python3
"""Stage 3: combine and clean raw CSVs into data/processed/dataset.jsonl.

Usage:
    python3 scripts/preprocess.py [--raw-dir DATA/RAW] [--out-dir DATA/PROCESSED]
                                   [--reports-dir REPORTS]

Reads every *.csv in data/raw/, combines them, applies the normalisation
steps from docs/SCHEMA.md / DECISIONS.md (NFC, invisible-char removal,
whitespace cleanup, quote normalisation), assigns ids, removes exact
duplicates (keeping the first occurrence), flags near-duplicates, and
writes:
  - data/processed/dataset.jsonl       the cleaned dataset
  - reports/preprocess_changes.csv     every text-normalisation change made
  - reports/duplicates_removed.csv     exact duplicates that were dropped
  - reports/near_duplicates.csv        near-duplicate flags (not removed)
  - reports/id_conflicts.csv           rows skipped due to id collisions
                                        across raw files with different content
  - reports/preprocess_summary.md      human-readable per-language summary

Never modifies files under data/raw/. Never changes the meaning of a text
entry — only encoding/whitespace/quote-style normalisation, per
DECISIONS.md D005 and the diacritics rule in the task brief.
"""
from __future__ import annotations

import argparse
import difflib
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

NEAR_DUP_THRESHOLD = 0.90


def find_raw_files(raw_dir: Path) -> list[Path]:
    return sorted(raw_dir.glob("*.csv"))


def load_and_combine(raw_files: list[Path]) -> tuple[list[dict], list[dict], list[str]]:
    """Returns (combined_rows, id_conflicts, skipped_file_messages).

    combined_rows: list of dicts in ALL_FIELDS shape (still raw strings,
    pre-normalisation), each tagged with '_source_file'.
    """
    combined: list[dict] = []
    seen_ids: dict[str, dict] = {}  # id -> row (for conflict detection)
    id_conflicts: list[dict] = []
    skipped: list[str] = []

    for path in raw_files:
        rows = common.read_csv(path)
        if not rows:
            continue
        header = set(rows[0].keys())
        missing_required = [f for f in common.REQUIRED_FIELDS if f not in header]
        if missing_required:
            skipped.append(
                f"{path.name}: missing required column(s) {missing_required}; file skipped entirely."
            )
            continue

        for row in rows:
            row = dict(row)
            row["_source_file"] = path.name
            raw_id = (row.get("id") or "").strip()
            if raw_id:
                prior = seen_ids.get(raw_id)
                if prior is not None and prior.get("text") != row.get("text"):
                    id_conflicts.append(
                        {
                            "id": raw_id,
                            "language": row.get("language", ""),
                            "file_a": prior.get("_source_file", ""),
                            "text_a": prior.get("text", ""),
                            "file_b": row.get("_source_file", ""),
                            "text_b": row.get("text", ""),
                        }
                    )
                    continue  # skip the conflicting row; keep the first
                seen_ids[raw_id] = row
            combined.append(row)

    return combined, id_conflicts, skipped


def assign_ids(rows: list[dict]) -> None:
    """Assigns 'id' in place for any row whose raw id is blank."""
    counters: dict[str, int] = defaultdict(int)
    # Pre-seed counters from any ids already present, so we never collide
    # with a pre-existing id.
    for row in rows:
        existing = (row.get("id") or "").strip()
        if existing and common.ID_PATTERN.match(existing):
            prefix = existing.split("-")[0]
            num = int(existing.split("-")[1])
            counters[prefix] = max(counters[prefix], num)

    for row in rows:
        existing = (row.get("id") or "").strip()
        if existing:
            continue
        lang = (row.get("language") or "").strip().lower()
        prefix = lang if lang in common.LANGUAGES else "unk"
        counters[prefix] += 1
        row["id"] = f"{prefix}-{counters[prefix]:04d}"


def normalise_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Applies text normalisation to 'text' and 'translation_en'.
    Returns (normalised_rows, change_log_rows)."""
    changes: list[dict] = []
    for row in rows:
        for field in ("text", "translation_en"):
            original = row.get(field) or ""
            cleaned, changed_steps = common.preprocess_text(original)
            row[field] = cleaned
            for step, did_change in changed_steps.items():
                if did_change:
                    changes.append(
                        {
                            "id": row.get("id", ""),
                            "language": row.get("language", ""),
                            "field": field,
                            "step": step,
                            "before": original,
                            "after": cleaned,
                        }
                    )
                    # only record 'before' as the pristine original once;
                    # subsequent steps' before/after both reflect the
                    # cumulative field value at that point, which is fine
                    # for an audit trail (each row shows one step's effect
                    # on the field's value at that stage).
                original = cleaned if did_change else original
    return rows, changes


def remove_exact_duplicates(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Exact duplicate = same (language, text) after normalisation. Keeps
    first occurrence. Returns (kept_rows, removed_rows)."""
    seen: dict[tuple[str, str], dict] = {}
    kept: list[dict] = []
    removed: list[dict] = []
    for row in rows:
        key = ((row.get("language") or "").strip().lower(), row.get("text") or "")
        if key in seen:
            removed.append(
                {
                    "id": row.get("id", ""),
                    "language": row.get("language", ""),
                    "text": row.get("text", ""),
                    "translation_en": row.get("translation_en", ""),
                    "duplicate_of_id": seen[key].get("id", ""),
                }
            )
            continue
        seen[key] = row
        kept.append(row)
    return kept, removed


def flag_near_duplicates(rows: list[dict]) -> list[dict]:
    """Flags (does not remove) near-duplicate text pairs within the same
    language, using difflib.SequenceMatcher ratio >= NEAR_DUP_THRESHOLD.
    O(n^2) per language; fine at the 150-250 entries/language scale this
    dataset targets (see DECISIONS.md)."""
    flags: list[dict] = []
    by_lang: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        lang = (row.get("language") or "").strip().lower()
        by_lang[lang].append(row)

    for lang, lang_rows in by_lang.items():
        for i in range(len(lang_rows)):
            for j in range(i + 1, len(lang_rows)):
                a, b = lang_rows[i], lang_rows[j]
                text_a, text_b = a.get("text") or "", b.get("text") or ""
                if not text_a or not text_b:
                    continue
                ratio = difflib.SequenceMatcher(None, text_a, text_b).ratio()
                if ratio >= NEAR_DUP_THRESHOLD:
                    flags.append(
                        {
                            "id_a": a.get("id", ""),
                            "id_b": b.get("id", ""),
                            "language": lang,
                            "ratio": f"{ratio:.3f}",
                            "text_a": text_a,
                            "text_b": text_b,
                        }
                    )
    return flags


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--raw-dir", type=Path, default=base / "data" / "raw")
    parser.add_argument("--out-dir", type=Path, default=base / "data" / "processed")
    parser.add_argument("--reports-dir", type=Path, default=base / "reports")
    args = parser.parse_args()

    raw_files = find_raw_files(args.raw_dir)
    if not raw_files:
        print(f"No CSV files found in {args.raw_dir}. Nothing to do.")
        # Still write an empty dataset + summary so downstream scripts have
        # something well-formed to read.
        common.write_jsonl(args.out_dir / "dataset.jsonl", [])
        return 0

    combined, id_conflicts, skipped_files = load_and_combine(raw_files)
    for msg in skipped_files:
        print(f"WARNING: {msg}")

    # Normalise to strict schema shape (bools, blanks) before id assignment
    # so id assignment can rely on a clean 'language' string.
    bool_anomalies: list[dict] = []
    schema_rows = [common.record_to_schema(r, bool_anomalies) for r in combined]
    for schema_row, raw_row in zip(schema_rows, combined):
        schema_row["_source_file"] = raw_row.get("_source_file", "")

    assign_ids(schema_rows)
    schema_rows, text_changes = normalise_rows(schema_rows)
    kept_rows, exact_duplicates = remove_exact_duplicates(schema_rows)
    near_dup_flags = flag_near_duplicates(kept_rows)

    # Strip internal bookkeeping field before writing the dataset.
    output_rows = []
    for row in kept_rows:
        row = dict(row)
        row.pop("_source_file", None)
        output_rows.append(row)
    output_rows.sort(key=lambda r: (r.get("language") or "", r.get("id") or ""))

    common.write_jsonl(args.out_dir / "dataset.jsonl", output_rows)

    common.write_csv(
        args.reports_dir / "preprocess_changes.csv",
        ["id", "language", "field", "step", "before", "after"],
        text_changes,
    )
    common.write_csv(
        args.reports_dir / "duplicates_removed.csv",
        ["id", "language", "text", "translation_en", "duplicate_of_id"],
        exact_duplicates,
    )
    common.write_csv(
        args.reports_dir / "near_duplicates.csv",
        ["id_a", "id_b", "language", "ratio", "text_a", "text_b"],
        near_dup_flags,
    )
    common.write_csv(
        args.reports_dir / "id_conflicts.csv",
        ["id", "language", "file_a", "text_a", "file_b", "text_b"],
        id_conflicts,
    )
    common.write_csv(
        args.reports_dir / "boolean_anomalies.csv",
        ["id", "language", "field", "raw_value"],
        bool_anomalies,
    )

    write_summary(args.reports_dir / "preprocess_summary.md", raw_files, skipped_files,
                   combined, output_rows, text_changes, exact_duplicates, near_dup_flags,
                   id_conflicts, bool_anomalies)

    print(f"Wrote {len(output_rows)} entries to {args.out_dir / 'dataset.jsonl'}")
    print(f"Reports written to {args.reports_dir}")
    return 0


def write_summary(path, raw_files, skipped_files, combined, output_rows, text_changes,
                   exact_duplicates, near_dup_flags, id_conflicts, bool_anomalies=None) -> None:
    by_lang_in = defaultdict(int)
    for r in combined:
        by_lang_in[(r.get("language") or "").strip().lower()] += 1

    by_lang_out = defaultdict(int)
    for r in output_rows:
        by_lang_out[r.get("language") or ""] += 1

    nfc_changed = defaultdict(set)
    invisible_changed = defaultdict(set)
    whitespace_changed = defaultdict(set)
    quotes_changed = defaultdict(set)
    for c in text_changes:
        lang = c["language"]
        bucket = {
            "nfc": nfc_changed,
            "invisible": invisible_changed,
            "whitespace": whitespace_changed,
            "quotes": quotes_changed,
        }.get(c["step"])
        if bucket is not None:
            bucket[lang].add(c["id"])

    dup_by_lang = defaultdict(int)
    for d in exact_duplicates:
        dup_by_lang[d["language"]] += 1

    near_by_lang = defaultdict(int)
    for f in near_dup_flags:
        near_by_lang[f["language"]] += 1

    lines = ["# Preprocessing summary", ""]
    lines.append(f"Raw files read: {len(raw_files)} ({', '.join(p.name for p in raw_files) or 'none'})")
    if skipped_files:
        lines.append("")
        lines.append("**Skipped files (missing required columns):**")
        for msg in skipped_files:
            lines.append(f"- {msg}")
    if id_conflicts:
        lines.append("")
        lines.append(f"**Id conflicts across files (row skipped, first occurrence kept):** {len(id_conflicts)} — see reports/id_conflicts.csv")
    if bool_anomalies:
        lines.append("")
        lines.append(f"**Unrecognised `reviewed`/`reviewed_by_independent` values (defaulted to False):** {len(bool_anomalies)} — see reports/boolean_anomalies.csv")

    lines.append("")
    lines.append("## Per-language counts")
    lines.append("")
    lines.append("| Language | Input rows | NFC changed | Invisible-char changed | Whitespace changed | Quotes changed | Exact duplicates removed | Near-duplicates flagged | Final entries |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    all_langs = sorted(set(list(by_lang_in.keys()) + list(by_lang_out.keys())))
    for lang in all_langs:
        label = common.LANGUAGE_NAMES.get(lang, lang or "(blank/unknown)")
        lines.append(
            f"| {label} (`{lang or 'unk'}`) | {by_lang_in.get(lang, 0)} | "
            f"{len(nfc_changed.get(lang, set()))} | {len(invisible_changed.get(lang, set()))} | "
            f"{len(whitespace_changed.get(lang, set()))} | {len(quotes_changed.get(lang, set()))} | "
            f"{dup_by_lang.get(lang, 0)} | {near_by_lang.get(lang, 0)} | {by_lang_out.get(lang, 0)} |"
        )

    lines.append("")
    lines.append(
        "NFC-normalisation counts are reported separately per the task brief, since "
        "diacritic/combining-mark encoding inconsistency is a common source of "
        "silent duplicates and mismatches (see DECISIONS.md D005)."
    )
    lines.append("")
    lines.append(
        "Near-duplicates are **flagged only, never auto-deleted** — see "
        "reports/near_duplicates.csv and DECISIONS.md D006."
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
