#!/usr/bin/env python3
"""Stage 4d: apply completed review-sheet corrections to the dataset.

Usage:
    python3 scripts/apply_corrections.py [--dataset PATH] [--review-dir DIR]
        [--out PATH] [--log PATH] [--conflicts PATH]

Reads data/processed/dataset.jsonl plus the four completed review sheets
(reports/review/layer1_cgg.csv, layer1_yor.csv, layer2_by_author1.csv,
layer2_by_author2.csv) and applies each row's `reviewer_correction` to
produce a corrected dataset.

reviewer_correction format (see DECISIONS.md D020): one or more
"field: new value" clauses separated by " | ", e.g.
    translation_en: A better English translation
    text: Fixed original text | domain: proverb
Recognised fields: text, translation_en, contributor_id, region, dialect,
date_collected, source_type, domain, source_url, site_name, retrieved_date,
source_license, translation_source. (id, language, reviewed*, reviewer_id
are never editable this way.)

Rules (see DECISIONS.md D020-D022):
  - A Layer 2 sheet's correction to `text` is NEVER applied directly — it
    is always written to reports/conflicts.csv for the language's
    independent (Layer 1) reviewer or original collector to decide.
  - If two sheets propose different corrections for the same (id, field),
    neither is applied — both are written to reports/conflicts.csv.
  - Every correction actually applied is logged to
    reports/corrections_log.csv: id, language, field, before, after,
    reviewer(=source sheet), layer.
  - `reviewed` is set true for any entry with a non-blank
    reviewer_verdict in ANY sheet. `reviewed_by_independent` is set true
    only for entries with a non-blank verdict in their language's Layer 1
    sheet.

Writes data/processed/dataset_corrected.jsonl (the original
data/processed/dataset.jsonl is never modified — see DECISIONS.md D021).
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

EDITABLE_FIELDS = {
    "text", "translation_en", "contributor_id", "region", "dialect",
    "date_collected", "source_type", "domain",
    # Added 2026-09-29 alongside web-scraping support (DECISIONS.md D026/D027)
    "source_url", "site_name", "retrieved_date", "source_license", "translation_source",
}

# Default reviewer codes per docs/TEAM_PLAN.md, used only to populate the
# reviewer_id field on entries a given sheet marks reviewed (see D022).
LAYER1_REVIEWER_CODE = {"cgg": "R01", "yor": "R02"}
LAYER2_REVIEWER_CODE = {"layer2_by_author1": "R03", "layer2_by_author2": "R04"}


def parse_correction(raw: str) -> dict[str, str]:
    """Parses 'field: value | field2: value2' into {field: value}.
    Unrecognised fields are ignored (and reported by the caller)."""
    result = {}
    if not raw or not raw.strip():
        return result
    for clause in raw.split("|"):
        clause = clause.strip()
        if not clause or ":" not in clause:
            continue
        field, _, value = clause.partition(":")
        field = field.strip()
        value = value.strip()
        if field in EDITABLE_FIELDS:
            result[field] = value
    return result


def load_sheet_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return common.read_csv(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--dataset", type=Path, default=base / "data" / "processed" / "dataset.jsonl")
    parser.add_argument("--review-dir", type=Path, default=base / "reports" / "review")
    parser.add_argument("--out", type=Path, default=base / "data" / "processed" / "dataset_corrected.jsonl")
    parser.add_argument("--log", type=Path, default=base / "reports" / "corrections_log.csv")
    parser.add_argument("--conflicts", type=Path, default=base / "reports" / "conflicts.csv")
    args = parser.parse_args()

    rows = common.read_jsonl(args.dataset)
    if not rows:
        print("No entries in dataset; nothing to correct.")
        return 0
    by_id = {r["id"]: r for r in rows}

    sheets = {
        f"layer1_{lang}": (args.review_dir / f"layer1_{lang}.csv", "layer1")
        for lang in common.LANGUAGES
    }
    sheets["layer2_by_author1"] = (args.review_dir / "layer2_by_author1.csv", "layer2")
    sheets["layer2_by_author2"] = (args.review_dir / "layer2_by_author2.csv", "layer2")

    # proposals[(id, field)] = list of (value, source_sheet_name, layer)
    proposals: dict[tuple[str, str], list[tuple[str, str, str]]] = defaultdict(list)
    # reviewed_ids[source_sheet_name] = set of ids with a non-blank verdict
    reviewed_ids: dict[str, set[str]] = {}

    for name, (path, layer) in sheets.items():
        sheet_rows = load_sheet_rows(path)
        reviewed_ids[name] = set()
        for row in sheet_rows:
            rid = row.get("id", "")
            if rid not in by_id:
                continue  # stale sheet referencing an id no longer in the dataset
            verdict = (row.get("reviewer_verdict") or "").strip()
            if verdict:
                reviewed_ids[name].add(rid)
            correction = parse_correction(row.get("reviewer_correction", ""))
            for field, value in correction.items():
                proposals[(rid, field)].append((value, name, layer))

    conflicts = []
    corrections_log = []
    corrected_by_id: dict[str, dict] = {rid: dict(row) for rid, row in by_id.items()}

    for (rid, field), props in proposals.items():
        row = by_id[rid]
        lang = row.get("language", "")

        # Rule: a Layer 2 correction to 'text' is NEVER auto-applied.
        layer2_text_props = [p for p in props if field == "text" and p[2] == "layer2"]
        for value, source, layer in layer2_text_props:
            conflicts.append({
                "id": rid, "language": lang, "field": field,
                "reason": "layer2_text_correction_requires_language_reviewer",
                "proposals": f"{source}: {value!r}",
            })

        applicable_props = [p for p in props if not (field == "text" and p[2] == "layer2")]
        if not applicable_props:
            continue

        distinct_values = {v for v, _, _ in applicable_props}
        if len(distinct_values) > 1:
            conflicts.append({
                "id": rid, "language": lang, "field": field,
                "reason": "conflicting_corrections",
                "proposals": "; ".join(f"{source}: {value!r}" for value, source, _ in applicable_props),
            })
            continue

        value = applicable_props[0][0]
        source = applicable_props[0][1]
        layer = applicable_props[0][2]
        before = row.get(field)
        if before == value:
            continue  # no actual change
        corrected_by_id[rid][field] = value
        corrections_log.append({
            "id": rid, "language": lang, "field": field,
            "before": before if before is not None else "",
            "after": value, "reviewer": source, "layer": layer,
        })

    # Update reviewed / reviewed_by_independent / reviewer_id.
    for rid, row in corrected_by_id.items():
        lang = row.get("language", "")
        layer1_name = f"layer1_{lang}" if lang in common.LANGUAGES else None
        reviewed_by_layer1 = layer1_name is not None and rid in reviewed_ids.get(layer1_name, set())
        reviewed_by_layer2 = any(
            rid in reviewed_ids.get(name, set())
            for name in ("layer2_by_author1", "layer2_by_author2")
        )
        if reviewed_by_layer1 or reviewed_by_layer2:
            row["reviewed"] = True
        if reviewed_by_layer1:
            row["reviewed_by_independent"] = True
            row["reviewer_id"] = LAYER1_REVIEWER_CODE.get(lang, row.get("reviewer_id"))
        elif reviewed_by_layer2:
            # Reviewed only by cross-review, not independently — record
            # which cross-reviewer touched it, but reviewed_by_independent
            # stays False (see docs/SCHEMA.md).
            for name in ("layer2_by_author1", "layer2_by_author2"):
                if rid in reviewed_ids.get(name, set()):
                    row["reviewer_id"] = LAYER2_REVIEWER_CODE.get(name, row.get("reviewer_id"))

    output_rows = [corrected_by_id[r["id"]] for r in rows]
    common.write_jsonl(args.out, output_rows)
    common.write_csv(args.log, ["id", "language", "field", "before", "after", "reviewer", "layer"], corrections_log)
    common.write_csv(args.conflicts, ["id", "language", "field", "reason", "proposals"], conflicts)

    print(f"Applied {len(corrections_log)} correction(s) -> {args.out}")
    print(f"{len(conflicts)} conflict(s) written to {args.conflicts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
