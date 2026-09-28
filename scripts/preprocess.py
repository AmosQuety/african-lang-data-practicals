#!/usr/bin/env python3
"""
Preprocess raw CoNLL Luganda NER data for Practical I.

Reads practical1/data/raw/{train,dev,test}.txt and writes:
  practical1/data/processed/{train,dev,test}.jsonl
  practical1/reports/changes.csv        (one row per changed/removed item, all steps)
  practical1/reports/bio_issues.csv     (every sentence with a BIO issue, fixed or not)

Steps applied are limited to what Stage 2 profiling (profile_before.json) showed were
actually needed for this dataset:
  - Unicode NFC normalisation / invisible-control-char stripping: SKIPPED (none found)
  - Whitespace / quote normalisation: SKIPPED (none found)
  - Exact-duplicate sentence removal within each split (keep first occurrence)
  - Train/test cross-split exact duplicates: reported, NOT deleted from test
  - BIO repair: only the unambiguous "leading I- at sentence start" case is auto-fixed;
    every sentence with a BIO issue (fixed or not) is written to bio_issues.csv
  - Reformat to JSONL: id, split, tokens, ner_tags

See practical1/DECISIONS.md D5-D9 for the reasoning behind each choice.
"""
import argparse
import csv
import json
import unicodedata
from pathlib import Path


def read_conll(path):
    sentences = []
    tokens, tags = [], []
    line_no = 0
    start_line = 1
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line_no += 1
            line = raw_line.rstrip("\n")
            if line.strip() == "":
                if tokens:
                    sentences.append({"tokens": tokens, "tags": tags, "start_line": start_line})
                    tokens, tags = [], []
                start_line = line_no + 1
                continue
            cols = line.split(" ")
            if len(cols) != 2:
                # Malformed lines: none found in Stage 2 profiling for this dataset;
                # if encountered, skip the line but keep going rather than crash.
                continue
            tok, tag = cols
            tokens.append(tok)
            tags.append(tag)
    if tokens:
        sentences.append({"tokens": tokens, "tags": tags, "start_line": start_line})
    return sentences


def sentence_text(tokens):
    return " ".join(tokens)


def has_bio_issue(tags):
    """Return True if tags contain any invalid BIO transition."""
    prev = "O"
    for tag in tags:
        if tag == "O":
            prev = tag
            continue
        if "-" not in tag:
            return True
        prefix, etype = tag.split("-", 1)
        if prefix not in ("B", "I"):
            return True
        if prefix == "I":
            if prev == "O":
                return True
            if "-" in prev:
                _, petype = prev.split("-", 1)
                if petype != etype:
                    return True
        prev = tag
    return False


def bio_issue_details(tags):
    prev = "O"
    issues = []
    for i, tag in enumerate(tags):
        if tag == "O":
            prev = tag
            continue
        if "-" not in tag:
            issues.append((i, f"malformed tag '{tag}'"))
            prev = tag
            continue
        prefix, etype = tag.split("-", 1)
        if prefix not in ("B", "I"):
            issues.append((i, f"malformed tag '{tag}'"))
            prev = tag
            continue
        if prefix == "I":
            if prev == "O":
                issues.append((i, f"'{tag}' follows 'O'"))
            elif "-" in prev:
                _, petype = prev.split("-", 1)
                if petype != etype:
                    issues.append((i, f"'{tag}' follows '{prev}' (type mismatch)"))
        prev = tag
    return issues


def try_autofix_leading_i(tags):
    """
    Unambiguous auto-fix: if tags[0] is 'I-<TYPE>' (i.e. the very first tag of the sentence
    is an I- tag with literally nothing before it), convert it to 'B-<TYPE>'.
    Returns (new_tags, fixed: bool). Does not touch any other position.
    """
    if not tags:
        return tags, False
    first = tags[0]
    if first.startswith("I-"):
        new_tags = list(tags)
        new_tags[0] = "B-" + first[2:]
        return new_tags, True
    return tags, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default="practical1/data/raw")
    ap.add_argument("--out-dir", default="practical1/data/processed")
    ap.add_argument("--changes-csv", default="practical1/reports/changes.csv")
    ap.add_argument("--bio-csv", default="practical1/reports/bio_issues.csv")
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    Path(args.changes_csv).parent.mkdir(parents=True, exist_ok=True)

    splits = ["train", "dev", "test"]
    raw_sentences = {}
    for split in splits:
        path = raw_dir / f"{split}.txt"
        raw_sentences[split] = read_conll(path)

    # NFC / whitespace / quote checks: verify still no-ops (defensive re-check, not blind trust
    # of Stage 2 — if this ever finds something, we log it as a change; see D5/D6).
    changes_rows = []
    bio_rows = []

    # Pass 1: exact-duplicate removal within each split (keep first occurrence)
    dedup_sentences = {}
    for split in splits:
        seen = {}
        kept = []
        for s in raw_sentences[split]:
            text = sentence_text(s["tokens"])
            if text in seen:
                changes_rows.append({
                    "step": "dedup_within_split",
                    "split": split,
                    "sentence_id": f"{split}-line{s['start_line']}",
                    "before_text": text,
                    "after_text": "(removed - exact duplicate of earlier sentence in this split)",
                })
                continue
            seen[text] = True
            kept.append(s)
        dedup_sentences[split] = kept

    # Cross-split train/test overlap: report only, no deletion
    train_texts = {sentence_text(s["tokens"]) for s in dedup_sentences["train"]}
    test_leak_count = 0
    for s in dedup_sentences["test"]:
        text = sentence_text(s["tokens"])
        if text in train_texts:
            test_leak_count += 1
            changes_rows.append({
                "step": "cross_split_overlap_flagged_not_removed",
                "split": "test",
                "sentence_id": f"test-line{s['start_line']}",
                "before_text": text,
                "after_text": text + "  [ALSO IN TRAIN - kept in test per instructions, not deleted]",
            })

    # Pass 2: Unicode NFC check (defensive; expected no-op per D5)
    for split in splits:
        for s in dedup_sentences[split]:
            text = sentence_text(s["tokens"])
            nfc = unicodedata.normalize("NFC", text)
            if nfc != text:
                changes_rows.append({
                    "step": "unicode_nfc_normalisation",
                    "split": split,
                    "sentence_id": f"{split}-line{s['start_line']}",
                    "before_text": text,
                    "after_text": nfc,
                })
                # apply the fix token-by-token to keep token/tag length aligned
                s["tokens"] = [unicodedata.normalize("NFC", t) for t in s["tokens"]]

    # Pass 3: BIO issues - log every issue found, auto-fix only the unambiguous leading-I- case
    for split in splits:
        for s in dedup_sentences[split]:
            tags = s["tags"]
            if not has_bio_issue(tags):
                continue
            before_text = sentence_text(s["tokens"])
            before_tags = list(tags)
            issues = bio_issue_details(tags)
            new_tags, fixed = try_autofix_leading_i(tags)
            fully_resolved = fixed and not has_bio_issue(new_tags)
            s["tags"] = new_tags
            bio_rows.append({
                "split": split,
                "sentence_id": f"{split}-line{s['start_line']}",
                "text": before_text,
                "tags_before": " ".join(before_tags),
                "tags_after": " ".join(new_tags),
                "issues": "; ".join(msg for _, msg in issues),
                "auto_fixed": "yes" if fixed else "no",
                "fully_resolved": "yes" if fully_resolved else "no",
            })
            if fixed:
                changes_rows.append({
                    "step": "bio_autofix_leading_I_to_B",
                    "split": split,
                    "sentence_id": f"{split}-line{s['start_line']}",
                    "before_text": " ".join(before_tags),
                    "after_text": " ".join(new_tags),
                })

    # Assert token/tag length parity before writing out (safety net; must never fail)
    for split in splits:
        for s in dedup_sentences[split]:
            assert len(s["tokens"]) == len(s["tags"]), f"length mismatch in {split}: {s}"

    # Write JSONL
    counts = {}
    for split in splits:
        out_path = out_dir / f"{split}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for idx, s in enumerate(dedup_sentences[split]):
                obj = {
                    "id": f"{split}-{idx}",
                    "split": split,
                    "tokens": s["tokens"],
                    "ner_tags": s["tags"],
                }
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        counts[split] = len(dedup_sentences[split])

    # Write changes.csv
    with open(args.changes_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["step", "split", "sentence_id", "before_text", "after_text"])
        writer.writeheader()
        for row in changes_rows:
            writer.writerow(row)

    # Write bio_issues.csv
    with open(args.bio_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "split", "sentence_id", "text", "tags_before", "tags_after",
            "issues", "auto_fixed", "fully_resolved",
        ])
        writer.writeheader()
        for row in bio_rows:
            writer.writerow(row)

    summary = {
        "raw_sentence_counts": {s: len(raw_sentences[s]) for s in splits},
        "processed_sentence_counts": counts,
        "duplicates_removed_within_split": {
            s: len(raw_sentences[s]) - counts[s] for s in splits
        },
        "cross_split_train_test_overlap_kept_in_test": test_leak_count,
        "bio_issues_found": len(bio_rows),
        "bio_issues_autofixed": sum(1 for r in bio_rows if r["auto_fixed"] == "yes"),
    }
    print(json.dumps(summary, indent=2))
    with open("practical1/reports/preprocess_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
