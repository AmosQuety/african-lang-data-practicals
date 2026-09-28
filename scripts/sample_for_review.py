#!/usr/bin/env python3
"""
Stage 4b: draw a reproducible random sample of 100 sentences (seed 42) from the RAW data,
spread across splits proportional to size, for manual review by the student.

Writes practical1/reports/manual_review_sample.csv with columns:
  id, split, raw_text, processed_text, auto_flags, my_verdict, my_notes

my_verdict and my_notes are left BLANK for the student to fill in - this script does not
guess or pre-fill them.
"""
import csv
import json
import random
from pathlib import Path

RAW_DIR = Path("practical1/data/raw")
PROCESSED_DIR = Path("practical1/data/processed")
OUT = Path("practical1/reports/manual_review_sample.csv")
SEED = 42
TOTAL_SAMPLE = 100
SPLITS = ["train", "dev", "test"]


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
                continue
            tok, tag = cols
            tokens.append(tok)
            tags.append(tag)
    if tokens:
        sentences.append({"tokens": tokens, "tags": tags, "start_line": start_line})
    return sentences


def read_jsonl_by_text(path):
    """Map raw sentence text -> processed text, for sentences that survived preprocessing
    (looked up by original raw text; a raw sentence removed as an exact duplicate or otherwise
    absent from processed output has no processed counterpart)."""
    mapping = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            text = " ".join(obj["tokens"])
            mapping[text] = text  # processed text (post any token-level edits); same tokens here
    return mapping


def valid_bio(tags):
    prev = "O"
    for tag in tags:
        if tag == "O":
            prev = tag
            continue
        if "-" not in tag:
            return False
        prefix, etype = tag.split("-", 1)
        if prefix not in ("B", "I"):
            return False
        if prefix == "I":
            if prev == "O":
                return False
            if "-" in prev:
                _, petype = prev.split("-", 1)
                if petype != etype:
                    return False
        prev = tag
    return True


def flags_for(sentence, dup_seen_before):
    flags = []
    if len(sentence["tokens"]) <= 1:
        flags.append("one_token_or_empty")
    if not valid_bio(sentence["tags"]):
        flags.append("invalid_bio")
    if dup_seen_before:
        flags.append("exact_duplicate_within_split")
    return ";".join(flags) if flags else ""


def main():
    rng = random.Random(SEED)

    raw = {split: read_conll(RAW_DIR / f"{split}.txt") for split in SPLITS}
    processed_texts = {split: read_jsonl_by_text(PROCESSED_DIR / f"{split}.jsonl") for split in SPLITS}

    total_raw = sum(len(raw[s]) for s in SPLITS)
    # proportional allocation, largest remainder method to hit TOTAL_SAMPLE exactly
    raw_alloc = {s: (len(raw[s]) / total_raw) * TOTAL_SAMPLE for s in SPLITS}
    base_alloc = {s: int(raw_alloc[s]) for s in SPLITS}
    remainder = TOTAL_SAMPLE - sum(base_alloc.values())
    # distribute remainder to splits with largest fractional part
    fractional = sorted(SPLITS, key=lambda s: raw_alloc[s] - base_alloc[s], reverse=True)
    for i in range(remainder):
        base_alloc[fractional[i % len(fractional)]] += 1

    rows = []
    for split in SPLITS:
        n = min(base_alloc[split], len(raw[split]))
        idxs = list(range(len(raw[split])))
        rng.shuffle(idxs)
        chosen = sorted(idxs[:n])  # sort for readability; selection itself is the random part

        seen_texts = set()
        text_counts = {}
        for s in raw[split]:
            t = " ".join(s["tokens"])
            text_counts[t] = text_counts.get(t, 0) + 1

        seen_so_far = set()
        for s in raw[split]:
            seen_so_far.add(" ".join(s["tokens"]))  # build up occurrence order tracking below

        # recompute "is this a repeat occurrence" in true document order
        occurrence_seen = set()
        is_dup_occurrence = []
        for s in raw[split]:
            t = " ".join(s["tokens"])
            is_dup_occurrence.append(t in occurrence_seen)
            occurrence_seen.add(t)

        for idx in chosen:
            s = raw[split][idx]
            raw_text = " ".join(s["tokens"])
            processed_text = processed_texts[split].get(raw_text, "(removed during preprocessing - see changes.csv)")
            flags = flags_for(s, is_dup_occurrence[idx])
            rows.append({
                "id": f"{split}-rawidx{idx}-line{s['start_line']}",
                "split": split,
                "raw_text": raw_text,
                "processed_text": processed_text,
                "auto_flags": flags,
                "my_verdict": "",
                "my_notes": "",
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "split", "raw_text", "processed_text", "auto_flags", "my_verdict", "my_notes",
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} rows to {OUT}")
    print("Per-split allocation:", base_alloc)


if __name__ == "__main__":
    main()
