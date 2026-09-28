#!/usr/bin/env python3
"""
Stage 4a: automatic validation of practical1/data/processed/*.jsonl.

Runs assertions and writes a pass/fail report to practical1/reports/validation.md.
Does not modify any data.
"""
import json
from pathlib import Path

SPLITS = ["train", "dev", "test"]
PROCESSED_DIR = Path("practical1/data/processed")
OUT = Path("practical1/reports/validation.md")


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


def main():
    results = []

    def check(name, condition, detail=""):
        results.append({"check": name, "passed": bool(condition), "detail": detail})

    all_sentences = {}
    parse_ok = True
    for split in SPLITS:
        path = PROCESSED_DIR / f"{split}.jsonl"
        sentences = []
        try:
            with open(path, encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)  # raises if invalid JSON
                    for field in ("id", "split", "tokens", "ner_tags"):
                        if field not in obj:
                            raise ValueError(f"{path}:{line_no} missing field '{field}'")
                    sentences.append(obj)
        except Exception as e:
            parse_ok = False
            check(f"valid_jsonl[{split}]", False, str(e))
            all_sentences[split] = []
            continue
        check(f"valid_jsonl[{split}]", True, f"{len(sentences)} lines parsed OK")
        all_sentences[split] = sentences

    # token/tag length match
    for split in SPLITS:
        mismatches = [s["id"] for s in all_sentences[split] if len(s["tokens"]) != len(s["ner_tags"])]
        check(
            f"token_tag_length_match[{split}]",
            len(mismatches) == 0,
            "OK" if not mismatches else f"{len(mismatches)} mismatches: {mismatches[:5]}",
        )

    # valid BIO
    for split in SPLITS:
        bad = [s["id"] for s in all_sentences[split] if not valid_bio(s["ner_tags"])]
        check(
            f"valid_bio[{split}]",
            len(bad) == 0,
            "OK" if not bad else f"{len(bad)} invalid: {bad[:5]}",
        )

    # no empty sentences
    for split in SPLITS:
        empties = [s["id"] for s in all_sentences[split] if len(s["tokens"]) == 0]
        check(
            f"no_empty_sentences[{split}]",
            len(empties) == 0,
            "OK" if not empties else f"{len(empties)} empty: {empties[:5]}",
        )

    # no exact duplicate sentences within split
    for split in SPLITS:
        texts = [" ".join(s["tokens"]) for s in all_sentences[split]]
        dupe_count = len(texts) - len(set(texts))
        check(
            f"no_duplicate_sentences_within_split[{split}]",
            dupe_count == 0,
            "OK" if dupe_count == 0 else f"{dupe_count} duplicate instances remain",
        )

    # ids unique within split
    for split in SPLITS:
        ids = [s["id"] for s in all_sentences[split]]
        check(
            f"unique_ids[{split}]",
            len(ids) == len(set(ids)),
            "OK" if len(ids) == len(set(ids)) else "duplicate ids found",
        )

    # KNOWN, EXPECTED "failure": cross-split train/test overlap (documented, not a bug)
    train_texts = {" ".join(s["tokens"]) for s in all_sentences["train"]}
    test_overlap = [s["id"] for s in all_sentences["test"] if " ".join(s["tokens"]) in train_texts]
    check(
        "cross_split_train_test_overlap_documented",
        True,  # this is informational, not a pass/fail gate - see DECISIONS.md D7
        f"{len(test_overlap)} test sentence(s) also appear in train (kept intentionally, see DECISIONS.md D7): {test_overlap}",
    )

    all_passed = all(r["passed"] for r in results)

    lines = ["# Validation Report — Practical I (Stage 4a, automatic)", ""]
    lines.append(f"Overall: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")
    lines.append("")
    lines.append("| Check | Result | Detail |")
    lines.append("|---|---|---|")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(f"| {r['check']} | {status} | {r['detail']} |")
    lines.append("")
    lines.append(
        "Note: `cross_split_train_test_overlap_documented` is informational, not a "
        "pass/fail gate — its purpose is to make the known train/test leak (1 sentence, "
        "see DECISIONS.md D7) visible in this report rather than silently correct or "
        "silently ignored."
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
