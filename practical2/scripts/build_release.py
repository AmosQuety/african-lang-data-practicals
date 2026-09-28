#!/usr/bin/env python3
"""Stage 5c: assemble release/ from the final dataset and a filled card.

Usage:
    python3 scripts/build_release.py [--dataset PATH] [--card PATH]
        [--validation PATH] [--conflicts PATH] [--release-dir DIR]

REFUSES TO RUN (exits nonzero, writes nothing) if:
  1. reports/validation.md's PII check is not PASS (see
     scripts/validate_auto.py — "PII check: FAIL" line), or is missing
     entirely (validation hasn't been run).
  2. reports/conflicts.csv has any unresolved rows (see
     scripts/apply_corrections.py).
  3. The card file (--card, default release/DATASET_CARD_TEMPLATE.md)
     still contains the placeholder text "[FILL IN]" anywhere.

On success, assembles:
  - release/dataset.jsonl, release/dataset.csv    (combined, both languages)
  - release/cgg/dataset_cgg.jsonl(.csv)             (Rukiga-only config)
  - release/yor/dataset_yor.jsonl(.csv)             (Yoruba-only config)
  - release/README.md                               (the filled card)
  - release/LICENSE                                 (CC BY 4.0 notice, proposed)
"""
from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

PLACEHOLDER = "[FILL IN"

LICENSE_TEXT = """Creative Commons Attribution 4.0 International (CC BY 4.0)
============================================================

STATUS: PROPOSED — to be confirmed by the authors (Nabasa Amos and
Jesulewami Kupoluyi) before real-world release. See practical2/docs/
CONSENT_FORM.md for the license as presented to contributors, and
practical2/DECISIONS.md for the reasoning.

This dataset is licensed under the Creative Commons Attribution 4.0
International License (CC BY 4.0).

You are free to:
  - Share — copy and redistribute the material in any medium or format
  - Adapt — remix, transform, and build upon the material
  for any purpose, even commercially.

Under the following terms:
  - Attribution — You must give appropriate credit, provide a link to
    the license, and indicate if changes were made.

No additional restrictions — You may not apply legal terms or
technological measures that legally restrict others from doing anything
the license permits.

Full legal text: https://creativecommons.org/licenses/by/4.0/legalcode
Human-readable summary: https://creativecommons.org/licenses/by/4.0/
"""


def check_pii_pass(validation_path: Path) -> tuple[bool, str]:
    if not validation_path.exists():
        return False, f"{validation_path} does not exist — run scripts/validate_auto.py first."
    text = validation_path.read_text(encoding="utf-8")
    if "PII check: PASS" in text:
        return True, ""
    if "PII check: FAIL" in text:
        return False, f"{validation_path} reports PII check: FAIL. Resolve flagged possible-PII items first."
    return False, f"{validation_path} has no recognisable PII check line — re-run scripts/validate_auto.py."


def check_no_unresolved_conflicts(conflicts_path: Path) -> tuple[bool, str]:
    if not conflicts_path.exists():
        return True, ""  # no conflicts file at all = nothing unresolved
    rows = common.read_csv(conflicts_path)
    if rows:
        return False, f"{conflicts_path} has {len(rows)} unresolved conflict(s). Resolve them (or confirm resolution) before building the release."
    return True, ""


def check_no_placeholders(card_path: Path) -> tuple[bool, str]:
    if not card_path.exists():
        return False, f"{card_path} does not exist."
    text = card_path.read_text(encoding="utf-8")
    if PLACEHOLDER in text:
        count = text.count(PLACEHOLDER)
        return False, f"{card_path} still contains {count} '{PLACEHOLDER}' placeholder(s). Fill in every real fact before building the release."
    return True, ""


def resolve_dataset_path(base: Path, override: Path | None) -> Path:
    if override is not None:
        return override
    corrected = base / "data" / "processed" / "dataset_corrected.jsonl"
    if corrected.exists():
        return corrected
    return base / "data" / "processed" / "dataset.jsonl"


def write_dataset_files(rows: list[dict], jsonl_path: Path, csv_path: Path) -> None:
    common.write_jsonl(jsonl_path, rows)
    flat_rows = [common.schema_row_to_flat(r) for r in rows]
    common.write_csv(csv_path, common.ALL_FIELDS, flat_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--dataset", type=Path, default=None)
    parser.add_argument("--card", type=Path, default=base / "release" / "DATASET_CARD_TEMPLATE.md")
    parser.add_argument("--validation", type=Path, default=base / "reports" / "validation.md")
    parser.add_argument("--conflicts", type=Path, default=base / "reports" / "conflicts.csv")
    parser.add_argument("--release-dir", type=Path, default=base / "release")
    args = parser.parse_args()

    dataset_path = resolve_dataset_path(base, args.dataset)

    failures = []
    ok, msg = check_pii_pass(args.validation)
    if not ok:
        failures.append(msg)
    ok, msg = check_no_unresolved_conflicts(args.conflicts)
    if not ok:
        failures.append(msg)
    ok, msg = check_no_placeholders(args.card)
    if not ok:
        failures.append(msg)

    if failures:
        print("REFUSING to build release. Fix the following and re-run:")
        for f in failures:
            print(f"  - {f}")
        return 1

    rows = common.read_jsonl(dataset_path)
    if not rows:
        print(f"REFUSING to build release: {dataset_path} has no entries.")
        return 1

    args.release_dir.mkdir(parents=True, exist_ok=True)

    write_dataset_files(rows, args.release_dir / "dataset.jsonl", args.release_dir / "dataset.csv")

    for lang in common.LANGUAGES:
        lang_rows = [r for r in rows if r.get("language") == lang]
        lang_dir = args.release_dir / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        write_dataset_files(
            lang_rows,
            lang_dir / f"dataset_{lang}.jsonl",
            lang_dir / f"dataset_{lang}.csv",
        )
        print(f"{lang}: {len(lang_rows)} entries -> {lang_dir}")

    shutil.copyfile(args.card, args.release_dir / "README.md")
    (args.release_dir / "LICENSE").write_text(LICENSE_TEXT, encoding="utf-8")

    print(f"Release built: {len(rows)} total entries -> {args.release_dir}")
    print(f"Card: {args.card} -> {args.release_dir / 'README.md'}")
    print("Nothing was uploaded anywhere. See docs/UPLOAD_GUIDE.md for the manual upload steps.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
