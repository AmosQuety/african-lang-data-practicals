#!/usr/bin/env python3
"""
Profile CoNLL-format NER data (Practical I).

Reads practical1/data/raw/{train,dev,test}.txt (or a --data-dir override) and writes:
  practical1/reports/profile_before.json
  practical1/reports/profile_before.md

Run with --data-dir practical1/data/processed --jsonl to profile the processed JSONL
output instead (used for the "after" snapshot in Stage 4), writing profile_after.json/.md.

This script only OBSERVES the data. It never modifies raw/processed files.
"""
import argparse
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

SPLITS = ["train", "dev", "test"]

# Zero-width / invisible characters worth flagging explicitly (beyond general Unicode category checks)
ZERO_WIDTH = {
    "​": "ZERO WIDTH SPACE",
    "‌": "ZERO WIDTH NON-JOINER",
    "‍": "ZERO WIDTH JOINER",
    "‎": "LEFT-TO-RIGHT MARK",
    "‏": "RIGHT-TO-LEFT MARK",
    "﻿": "ZERO WIDTH NO-BREAK SPACE (BOM)",
    "⁠": "WORD JOINER",
}

CURLY_QUOTES = {
    "‘": "LEFT SINGLE QUOTATION MARK",
    "’": "RIGHT SINGLE QUOTATION MARK",
    "“": "LEFT DOUBLE QUOTATION MARK",
    "”": "RIGHT DOUBLE QUOTATION MARK",
}

UNUSUAL_WHITESPACE = {
    " ": "NO-BREAK SPACE",
    " ": "FIGURE SPACE",
    " ": "THIN SPACE",
    "　": "IDEOGRAPHIC SPACE",
    "\t": "TAB",
}


def is_control_char(ch):
    if ch in ("\n", "\r", "\t"):
        return False
    cat = unicodedata.category(ch)
    return cat.startswith("C") and cat != "Cf"  # Cc = control; keep Cf (format, incl. zero-width) separate


def read_conll(path):
    """Yield (sentence_id, tokens, tags, malformed_lines) per sentence, plus raw line numbers."""
    sentences = []
    malformed = []
    tokens, tags = [], []
    line_no = 0
    start_line = 1
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line_no += 1
            line = raw_line.rstrip("\n")
            if line.strip() == "":
                if tokens:
                    sentences.append({
                        "tokens": tokens,
                        "tags": tags,
                        "start_line": start_line,
                        "end_line": line_no - 1,
                    })
                    tokens, tags = [], []
                start_line = line_no + 1
                continue
            cols = line.split(" ")
            if len(cols) != 2:
                malformed.append({"line": line_no, "content": line, "n_cols": len(cols)})
                continue
            tok, tag = cols
            tokens.append(tok)
            tags.append(tag)
    if tokens:
        sentences.append({
            "tokens": tokens, "tags": tags,
            "start_line": start_line, "end_line": line_no,
        })
    return sentences, malformed


def read_jsonl(path):
    sentences = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            sentences.append({
                "id": obj.get("id"),
                "tokens": obj["tokens"],
                "tags": obj["ner_tags"],
                "start_line": line_no,
                "end_line": line_no,
            })
    return sentences, []


def sentence_text(tokens):
    return " ".join(tokens)


def check_bio(tags):
    """Return list of (index, issue) for invalid BIO transitions."""
    issues = []
    prev = "O"
    for i, tag in enumerate(tags):
        if tag == "O":
            prev = tag
            continue
        if "-" not in tag:
            issues.append((i, f"malformed tag '{tag}' (no B-/I- prefix)"))
            prev = tag
            continue
        prefix, etype = tag.split("-", 1)
        if prefix not in ("B", "I"):
            issues.append((i, f"malformed tag '{tag}' (prefix not B/I)"))
            prev = tag
            continue
        if prefix == "I":
            if prev == "O":
                issues.append((i, f"'{tag}' follows 'O' (I- tag with no preceding B-/I- of same type)"))
            elif "-" in prev:
                pprefix, petype = prev.split("-", 1)
                if petype != etype:
                    issues.append((i, f"'{tag}' follows '{prev}' (entity type mismatch)"))
        prev = tag
    return issues


def unicode_findings(text):
    findings = defaultdict(int)
    nfc = unicodedata.normalize("NFC", text)
    if nfc != text:
        findings["non_nfc"] += 1
    for ch in text:
        if ch in ZERO_WIDTH:
            findings[f"zero_width:{ZERO_WIDTH[ch]}"] += 1
        elif ch in CURLY_QUOTES:
            findings[f"curly_quote:{CURLY_QUOTES[ch]}"] += 1
        elif ch in UNUSUAL_WHITESPACE:
            findings[f"unusual_whitespace:{UNUSUAL_WHITESPACE[ch]}"] += 1
        elif is_control_char(ch):
            findings[f"control_char:U+{ord(ch):04X}"] += 1
    return findings


def profile_split(name, sentences, malformed):
    n_sent = len(sentences)
    tok_lens = [len(s["tokens"]) for s in sentences]
    all_tokens = [t for s in sentences for t in s["tokens"]]
    unique_tokens = set(all_tokens)
    label_counter = Counter(t for s in sentences for t in s["tags"])

    empties = [s for s in sentences if len(s["tokens"]) == 0]
    one_token = [s for s in sentences if len(s["tokens"]) == 1]

    exact_dupe_texts = Counter(sentence_text(s["tokens"]) for s in sentences)
    dup_within = {text: c for text, c in exact_dupe_texts.items() if c > 1}

    unicode_issue_sentences = []
    bio_issue_sentences = []
    for s in sentences:
        text = sentence_text(s["tokens"])
        uf = unicode_findings(text)
        if uf:
            unicode_issue_sentences.append({
                "start_line": s["start_line"], "text": text, "findings": dict(uf),
            })
        bio_issues = check_bio(s["tags"])
        if bio_issues:
            bio_issue_sentences.append({
                "start_line": s["start_line"],
                "text": text,
                "tags": s["tags"],
                "issues": [{"index": i, "issue": msg} for i, msg in bio_issues],
            })

    length_dist = {}
    if tok_lens:
        sorted_lens = sorted(tok_lens)
        length_dist = {
            "min": min(sorted_lens),
            "median": statistics.median(sorted_lens),
            "mean": round(statistics.mean(sorted_lens), 2),
            "max": max(sorted_lens),
        }

    return {
        "split": name,
        "sentence_count": n_sent,
        "token_count": len(all_tokens),
        "unique_token_count": len(unique_tokens),
        "sentence_length_distribution": length_dist,
        "label_distribution": dict(label_counter),
        "empty_sentence_count": len(empties),
        "one_token_sentence_count": len(one_token),
        "one_token_sentence_examples": [
            {"start_line": s["start_line"], "token": s["tokens"][0], "tag": s["tags"][0]}
            for s in one_token[:10]
        ],
        "exact_duplicate_sentence_groups_within_split": len(dup_within),
        "exact_duplicate_sentence_instances_within_split": sum(dup_within.values()) - len(dup_within) if dup_within else 0,
        "exact_duplicate_examples_within_split": [
            {"text": text, "count": c} for text, c in list(dup_within.items())[:10]
        ],
        "unicode_issue_sentence_count": len(unicode_issue_sentences),
        "unicode_issue_examples": unicode_issue_sentences[:10],
        "invalid_bio_sentence_count": len(bio_issue_sentences),
        "invalid_bio_examples": bio_issue_sentences[:10],
        "malformed_line_count": len(malformed),
        "malformed_line_examples": malformed[:10],
        "_sentence_texts": exact_dupe_texts,  # used for cross-split comparison, stripped before json dump
    }


def cross_split_duplicates(profiles):
    """Find exact-duplicate sentences that appear in more than one split."""
    split_sets = {p["split"]: set(p["_sentence_texts"].keys()) for p in profiles}
    pairs = []
    names = list(split_sets.keys())
    cross = defaultdict(set)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            overlap = split_sets[a] & split_sets[b]
            if overlap:
                pairs.append({"splits": [a, b], "count": len(overlap), "examples": list(overlap)[:10]})
    return pairs


def render_markdown(profiles, cross_dupes, title):
    lines = [f"# {title}", ""]
    for p in profiles:
        lines.append(f"## Split: {p['split']}")
        lines.append("")
        lines.append(f"- Sentence count: {p['sentence_count']}")
        lines.append(f"- Token count: {p['token_count']}")
        lines.append(f"- Unique tokens: {p['unique_token_count']}")
        ld = p["sentence_length_distribution"]
        if ld:
            lines.append(
                f"- Sentence length (tokens): min={ld['min']}, median={ld['median']}, "
                f"mean={ld['mean']}, max={ld['max']}"
            )
        lines.append(f"- Empty sentences: {p['empty_sentence_count']}")
        lines.append(f"- One-token sentences: {p['one_token_sentence_count']}")
        if p["one_token_sentence_examples"]:
            lines.append("  - Examples: " + ", ".join(
                f"`{e['token']}`/{e['tag']} (line {e['start_line']})"
                for e in p["one_token_sentence_examples"][:5]
            ))
        lines.append(
            f"- Exact duplicate sentence groups within split: "
            f"{p['exact_duplicate_sentence_groups_within_split']} "
            f"({p['exact_duplicate_sentence_instances_within_split']} extra instances beyond first occurrence)"
        )
        if p["exact_duplicate_examples_within_split"]:
            for ex in p["exact_duplicate_examples_within_split"][:3]:
                snippet = ex["text"][:80] + ("..." if len(ex["text"]) > 80 else "")
                lines.append(f"  - \"{snippet}\" x{ex['count']}")
        lines.append(f"- Sentences with Unicode issues (non-NFC / invisible / control / unusual whitespace / curly quotes): {p['unicode_issue_sentence_count']}")
        if p["unicode_issue_sentence_count"] == 0:
            lines.append("  - None found.")
        else:
            for ex in p["unicode_issue_examples"][:3]:
                snippet = ex["text"][:80] + ("..." if len(ex["text"]) > 80 else "")
                lines.append(f"  - line {ex['start_line']}: \"{snippet}\" -> {ex['findings']}")
        lines.append(f"- Invalid BIO sequences: {p['invalid_bio_sentence_count']}")
        if p["invalid_bio_sentence_count"] == 0:
            lines.append("  - None found.")
        else:
            for ex in p["invalid_bio_examples"][:3]:
                snippet = ex["text"][:80] + ("..." if len(ex["text"]) > 80 else "")
                issues_str = "; ".join(i["issue"] for i in ex["issues"])
                lines.append(f"  - line {ex['start_line']}: \"{snippet}\" -> {issues_str}")
        lines.append(f"- Malformed lines (wrong column count): {p['malformed_line_count']}")
        if p["malformed_line_count"] == 0:
            lines.append("  - None found.")
        else:
            for ex in p["malformed_line_examples"][:5]:
                lines.append(f"  - line {ex['line']}: `{ex['content']}` ({ex['n_cols']} columns)")
        lines.append("")
        lines.append("- Label distribution:")
        for label, count in sorted(p["label_distribution"].items(), key=lambda kv: -kv[1]):
            lines.append(f"  - {label}: {count}")
        lines.append("")

    lines.append("## Cross-split exact duplicates")
    lines.append("")
    if not cross_dupes:
        lines.append("None found.")
    else:
        for cd in cross_dupes:
            lines.append(f"- {cd['splits'][0]} <-> {cd['splits'][1]}: {cd['count']} identical sentences")
            for ex in cd["examples"][:5]:
                snippet = ex[:80] + ("..." if len(ex) > 80 else "")
                lines.append(f"  - \"{snippet}\"")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="practical1/data/raw")
    ap.add_argument("--out-json", default="practical1/reports/profile_before.json")
    ap.add_argument("--out-md", default="practical1/reports/profile_before.md")
    ap.add_argument("--jsonl", action="store_true", help="Read {split}.jsonl instead of {split}.txt")
    ap.add_argument("--title", default="Profile: Raw Data (before preparation)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    profiles = []
    for split in SPLITS:
        ext = "jsonl" if args.jsonl else "txt"
        path = data_dir / f"{split}.{ext}"
        if not path.exists():
            print(f"WARNING: {path} not found, skipping split '{split}'", file=sys.stderr)
            continue
        if args.jsonl:
            sentences, malformed = read_jsonl(path)
        else:
            sentences, malformed = read_conll(path)
        profiles.append(profile_split(split, sentences, malformed))

    cross_dupes = cross_split_duplicates(profiles)

    # strip internal helper field before JSON dump
    json_profiles = []
    for p in profiles:
        p2 = {k: v for k, v in p.items() if k != "_sentence_texts"}
        json_profiles.append(p2)

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "splits": json_profiles,
            "cross_split_exact_duplicates": cross_dupes,
        }, f, ensure_ascii=False, indent=2)

    md = render_markdown(profiles, cross_dupes, args.title)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Wrote {out_json} and {out_md}")


if __name__ == "__main__":
    main()
