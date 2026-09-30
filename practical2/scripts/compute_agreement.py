#!/usr/bin/env python3
"""Stage 4c: inter-reviewer agreement on the Layer 2 overlap set.

Usage:
    python3 scripts/compute_agreement.py [--sheet1 PATH] [--sheet2 PATH]
                                          [--out PATH]

Reads the two completed Layer 2 cross-review sheets (default:
reports/review/layer2_by_author1.csv and layer2_by_author2.csv), finds
the ids present in both (the overlap set — see scripts/make_review_sheet.py
and reports/review/overlap_ids.csv), and computes percent agreement and
Cohen's kappa on `reviewer_verdict` for the ids both reviewers have
actually completed (non-blank verdict in both sheets). Standard-library
only (no scipy/sklearn).

**This measures agreement on the Layer 2 English-side checks (does the
translation read sensibly, PII, metadata, formatting, flagged items) —
NOT agreement on target-language (Rukiga/Yoruba) correctness**, which
neither Layer 2 reviewer is positioned to judge (see the .NOTE.md files
next to each sheet). That is Layer 1's job.

Writes reports/agreement.md.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def load_sheet(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return {row["id"]: row for row in common.read_csv(path)}


def cohens_kappa(pairs: list[tuple[str, str]]) -> float | None:
    """Standard two-rater Cohen's kappa, stdlib only.
    pairs: list of (verdict_rater1, verdict_rater2)."""
    n = len(pairs)
    if n == 0:
        return None
    categories = sorted({v for pair in pairs for v in pair})
    if len(categories) < 2:
        return 1.0 if all(a == b for a, b in pairs) else 0.0

    agree = sum(1 for a, b in pairs if a == b)
    po = agree / n

    marginal1 = Counter(a for a, _ in pairs)
    marginal2 = Counter(b for _, b in pairs)
    pe = sum((marginal1.get(c, 0) / n) * (marginal2.get(c, 0) / n) for c in categories)

    if pe == 1.0:
        return 1.0  # perfect expected agreement and po==pe==1 (all one category)
    return (po - pe) / (1 - pe)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--sheet1", type=Path, default=base / "reports" / "review" / "layer2_by_author1.csv")
    parser.add_argument("--sheet2", type=Path, default=base / "reports" / "review" / "layer2_by_author2.csv")
    parser.add_argument("--out", type=Path, default=base / "reports" / "agreement.md")
    args = parser.parse_args()

    sheet1 = load_sheet(args.sheet1)
    sheet2 = load_sheet(args.sheet2)

    if not sheet1 or not sheet2:
        write_report(args.out, sheet1_path=args.sheet1, sheet2_path=args.sheet2,
                     overlap_total=0, completed=[], incomplete_ids=[], pairs=[],
                     disagreements=[], error="One or both sheets are missing or empty. Run "
                     "scripts/make_review_sheet.py and have both reviewers complete their "
                     "sheets before computing agreement.")
        print("One or both sheets missing/empty; wrote a placeholder report.")
        return 0

    overlap_ids = sorted(set(sheet1) & set(sheet2))

    pairs = []
    disagreements = []
    incomplete_ids = []
    for oid in overlap_ids:
        v1 = (sheet1[oid].get("reviewer_verdict") or "").strip()
        v2 = (sheet2[oid].get("reviewer_verdict") or "").strip()
        if not v1 or not v2:
            incomplete_ids.append(oid)
            continue
        pairs.append((v1, v2))
        if v1 != v2:
            disagreements.append({
                "id": oid,
                "language": sheet1[oid].get("language", ""),
                "verdict_author1": v1,
                "verdict_author2": v2,
                "notes_author1": sheet1[oid].get("reviewer_notes", ""),
                "notes_author2": sheet2[oid].get("reviewer_notes", ""),
            })

    write_report(args.out, sheet1_path=args.sheet1, sheet2_path=args.sheet2,
                 overlap_total=len(overlap_ids), completed=pairs, incomplete_ids=incomplete_ids,
                 pairs=pairs, disagreements=disagreements, error=None)

    print(f"Overlap ids: {len(overlap_ids)}; completed by both: {len(pairs)}; "
          f"incomplete: {len(incomplete_ids)}; disagreements: {len(disagreements)}")
    return 0


def write_report(path: Path, sheet1_path, sheet2_path, overlap_total, completed, incomplete_ids,
                  pairs, disagreements, error: str | None) -> None:
    lines = ["# Layer 2 inter-reviewer agreement", ""]
    lines.append(
        "**Scope note:** this measures agreement between the two authors' "
        "Layer 2 English-side checks (translation readability, PII, "
        "metadata, formatting, flagged items) on the shared overlap set. "
        "It does **not** measure agreement on target-language (Rukiga/"
        "Yoruba) correctness — neither Layer 2 reviewer reads the other's "
        "language. Target-language correctness is Layer 1's job."
    )
    lines.append("")
    lines.append(f"Sheet 1: `{sheet1_path}`")
    lines.append(f"Sheet 2: `{sheet2_path}`")
    lines.append("")

    if error:
        lines.append(f"**{error}**")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    n_completed = len(pairs)
    lines.append(f"Overlap set size: {overlap_total}")
    lines.append(f"Completed by both reviewers: {n_completed}")
    if incomplete_ids:
        lines.append(f"Not yet completed by both reviewers: {len(incomplete_ids)} "
                      f"({', '.join(incomplete_ids[:20])}{' ...' if len(incomplete_ids) > 20 else ''})")
    lines.append("")

    if n_completed == 0:
        lines.append("No overlap ids have a verdict from both reviewers yet — nothing to compute.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    agree_count = sum(1 for a, b in pairs if a == b)
    percent_agreement = agree_count / n_completed * 100
    kappa = cohens_kappa(pairs)

    lines.append(f"**Percent agreement:** {percent_agreement:.1f}% ({agree_count}/{n_completed})")
    lines.append(f"**Cohen's kappa:** {kappa:.3f}" if kappa is not None else "**Cohen's kappa:** n/a")
    lines.append("")
    lines.append(
        "Kappa interpretation (Landis & Koch 1977 rule of thumb, informal): "
        "<0 poor, 0.00-0.20 slight, 0.21-0.40 fair, 0.41-0.60 moderate, "
        "0.61-0.80 substantial, 0.81-1.00 almost perfect."
    )
    lines.append("")

    verdict_counts1 = Counter(a for a, _ in pairs)
    verdict_counts2 = Counter(b for _, b in pairs)
    all_verdicts = sorted(set(verdict_counts1) | set(verdict_counts2))
    lines.append("## Verdict distribution (completed overlap only)")
    lines.append("")
    lines.append("| Verdict | Author 1 | Author 2 |")
    lines.append("|---|---|---|")
    for v in all_verdicts:
        lines.append(f"| `{v}` | {verdict_counts1.get(v, 0)} | {verdict_counts2.get(v, 0)} |")
    lines.append("")

    lines.append(f"## Disagreements ({len(disagreements)})")
    lines.append("")
    if disagreements:
        lines.append("| id | language | Author 1 verdict | Author 2 verdict | Author 1 notes | Author 2 notes |")
        lines.append("|---|---|---|---|---|---|")
        for d in disagreements:
            lines.append(
                f"| {d['id']} | {d['language']} | {d['verdict_author1']} | {d['verdict_author2']} | "
                f"{d['notes_author1'][:80]} | {d['notes_author2'][:80]} |"
            )
        lines.append("")
        lines.append("The two authors should discuss each disagreement above and agree on a "
                      "resolution (recorded via reviewer_correction in the relevant sheet, or "
                      "escalated to the language's independent reviewer if it touches the "
                      "original-language `text`).")
    else:
        lines.append("None — full agreement on the completed overlap set.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
