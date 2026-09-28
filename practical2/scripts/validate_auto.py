#!/usr/bin/env python3
"""Stage 4a: automated validation of data/processed/dataset.jsonl.

Usage:
    python3 scripts/validate_auto.py [--dataset PATH] [--reports-dir REPORTS]

Every check is heuristic-assisted, not a verdict — this script cannot read
Luganda or Yoruba, so anything beyond schema/format checks is a flag for a
human reviewer, not a fact. See reports/validation.md's "Limitations"
section, written by this script every run, for what each check can and
cannot actually tell you.

Writes:
  - reports/validation.md   pass/fail + counts per check, PER LANGUAGE
  - reports/flags.csv       every individual flagged item: id, language,
                             check, detail
Exit code is always 0 (this script never blocks anything by itself —
scripts/build_release.py is what refuses to run on a failed PII check).
"""
from __future__ import annotations

import argparse
import difflib
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

# ---------------------------------------------------------------------------
# Thresholds (see DECISIONS.md for rationale on each)
# ---------------------------------------------------------------------------

VERY_SHORT_CHARS = 3           # D010: entries shorter than this are "very short"
LENGTH_OUTLIER_STD = 3.0       # D010: length outlier = more than N std devs from the per-language mean
RARE_CHAR_MAX_ENTRIES = 2      # D012: a char appearing in <= this many entries in its language is "rare"
REGION_SIMILARITY_THRESHOLD = 0.82  # D013: near-identical region spellings
ENGLISH_STOPWORD_FRACTION = 0.5     # D014: share of common-English words that trips "looks like English"
TRANSLATION_RATIO_MIN = 0.15   # D011: translation/source length ratio outlier bounds
TRANSLATION_RATIO_MAX = 6.0

# A small, deliberately generic set of very common English function words.
# This is NOT a claim about Luganda/Yoruba vocabulary — see limitations.
COMMON_ENGLISH_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "on",
    "and", "or", "but", "with", "for", "this", "that", "it", "as", "at",
    "by", "from", "be", "he", "she", "they", "we", "you", "i", "not",
    "have", "has", "had", "will", "would", "can", "could", "my", "your",
    "his", "her", "their", "our",
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE)
HANDLE_RE = re.compile(r"(?<!\w)@[A-Za-z0-9_]{2,}")
LONG_DIGIT_RUN_RE = re.compile(r"\d{7,}")
# Ugandan mobile: +256 7XXXXXXXX or 07XXXXXXXX (9-10 digits total after 0/+256)
UG_PHONE_RE = re.compile(r"(?:\+256|0)7\d{8}\b")
# Nigerian mobile: +234 XXXXXXXXXX or 0[789]XXXXXXXXX
NG_PHONE_RE = re.compile(r"(?:\+234|0)[789]\d{9}\b")
# Generic international number: + followed by 8-15 digits (with optional separators)
INTL_PHONE_RE = re.compile(r"\+\d[\d \-]{7,14}\d")
# Capitalised token not at the very start of the string — a crude name-like hint
CAP_TOKEN_RE = re.compile(r"(?<=\S )\b[A-Z][a-z]{2,}\b")

# Yoruba tone-mark vs. subdot heuristics (informational only; see D015).
YORUBA_TONE_MARK_CHARS = set("̀́̂")  # combining grave/acute/circumflex
YORUBA_SUBDOT_CHARS = set("ẹọṣẸỌṢ̣")  # ẹ ọ ṣ (+upper) and combining dot below


def load_dataset(path: Path) -> list[dict]:
    return common.read_jsonl(path)


def by_language(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        out[row.get("language") or ""].append(row)
    return out


# ---------------------------------------------------------------------------
# Individual checks. Each returns a list of flag dicts:
#   {"id":..., "language":..., "check":..., "detail":...}
# ---------------------------------------------------------------------------


def check_schema_and_required(rows: list[dict]) -> list[dict]:
    flags = []
    for row in rows:
        rid, lang = row.get("id", ""), row.get("language", "")
        for field in common.REQUIRED_FIELDS:
            if field not in row or row.get(field) in (None, ""):
                if field in common.BOOLEAN_FIELDS:
                    continue  # booleans are never "missing" — False is valid
                flags.append({"id": rid, "language": lang, "check": "required_field_missing",
                              "detail": f"'{field}' is empty or missing"})
        if lang and lang not in common.LANGUAGES:
            flags.append({"id": rid, "language": lang, "check": "schema_language_invalid",
                          "detail": f"language '{lang}' is not one of {common.LANGUAGES}"})
        if row.get("id") and not common.ID_PATTERN.match(row["id"]):
            flags.append({"id": rid, "language": lang, "check": "schema_id_format",
                          "detail": f"id '{row['id']}' does not match ^[a-z]{{3}}-[0-9]{{4,}}$"})
        cid = row.get("contributor_id") or ""
        if cid and not common.CONTRIBUTOR_ID_PATTERN.match(cid):
            flags.append({"id": rid, "language": lang, "check": "schema_contributor_id_format",
                          "detail": f"contributor_id '{cid}' does not match ^C[0-9]{{3,}}$"})
        rev_id = row.get("reviewer_id")
        if rev_id and not common.REVIEWER_ID_PATTERN.match(rev_id):
            flags.append({"id": rid, "language": lang, "check": "schema_reviewer_id_format",
                          "detail": f"reviewer_id '{rev_id}' does not match ^R[0-9]{{2,}}$"})
        date = row.get("date_collected")
        if date and not common.DATE_COLLECTED_PATTERN.match(date):
            flags.append({"id": rid, "language": lang, "check": "schema_date_format",
                          "detail": f"date_collected '{date}' is not YYYY-MM"})
        src = row.get("source_type") or ""
        if src and src not in common.SOURCE_TYPES:
            flags.append({"id": rid, "language": lang, "check": "schema_source_type_invalid",
                          "detail": f"source_type '{src}' not in {common.SOURCE_TYPES}"})
        if row.get("reviewed_by_independent") and not row.get("reviewed"):
            flags.append({"id": rid, "language": lang, "check": "schema_review_flag_inconsistent",
                          "detail": "reviewed_by_independent=true but reviewed=false"})
    return flags


def check_empty_or_short(rows: list[dict]) -> list[dict]:
    flags = []
    for row in rows:
        text = (row.get("text") or "").strip()
        if len(text) == 0:
            flags.append({"id": row.get("id", ""), "language": row.get("language", ""),
                          "check": "empty_text", "detail": "text is empty"})
        elif len(text) < VERY_SHORT_CHARS:
            flags.append({"id": row.get("id", ""), "language": row.get("language", ""),
                          "check": "very_short_text",
                          "detail": f"text is only {len(text)} character(s): '{text}'"})
    return flags


def check_duplicates_within_language(rows: list[dict]) -> list[dict]:
    flags = []
    seen: dict[tuple[str, str], str] = {}
    for row in rows:
        key = (row.get("language") or "", row.get("text") or "")
        if key in seen:
            flags.append({"id": row.get("id", ""), "language": row.get("language", ""),
                          "check": "duplicate_within_language",
                          "detail": f"identical text to {seen[key]}"})
        else:
            seen[key] = row.get("id", "")
    return flags


def check_duplicates_across_languages(rows: list[dict]) -> list[dict]:
    """Same text appearing under two different language labels — likely a
    mislabel, since Luganda and Yoruba text should essentially never be
    identical strings by chance for anything but the shortest tokens."""
    flags = []
    seen: dict[str, tuple[str, str]] = {}  # text -> (id, language)
    for row in rows:
        text = row.get("text") or ""
        if not text:
            continue
        if text in seen and seen[text][1] != row.get("language"):
            other_id, other_lang = seen[text]
            flags.append({"id": row.get("id", ""), "language": row.get("language", ""),
                          "check": "duplicate_across_languages",
                          "detail": f"identical text to {other_id} (language={other_lang}) — possible mislabel"})
        else:
            seen.setdefault(text, (row.get("id", ""), row.get("language", "")))
    return flags


def check_length_outliers(rows_by_lang: dict[str, list[dict]]) -> list[dict]:
    flags = []
    for lang, rows in rows_by_lang.items():
        lengths = [len((r.get("text") or "")) for r in rows if r.get("text")]
        if len(lengths) < 5:
            continue  # not enough data for a meaningful std dev
        mean = statistics.mean(lengths)
        stdev = statistics.pstdev(lengths)
        if stdev == 0:
            continue
        for row in rows:
            length = len(row.get("text") or "")
            z = (length - mean) / stdev
            if abs(z) > LENGTH_OUTLIER_STD:
                flags.append({"id": row.get("id", ""), "language": lang,
                              "check": "length_outlier",
                              "detail": f"text length {length} chars is {z:+.1f} std devs from language mean {mean:.1f}"})
    return flags


def check_character_anomalies(rows_by_lang: dict[str, list[dict]]) -> list[dict]:
    """Rare-character rule uses each language's OWN character distribution
    (built from this dataset), not any external reference."""
    flags = []
    for lang, rows in rows_by_lang.items():
        char_entry_count: Counter = Counter()
        for row in rows:
            text = row.get("text") or ""
            for ch in set(text):
                if ch.isspace():
                    continue
                char_entry_count[ch] += 1
        rare_chars = {ch for ch, n in char_entry_count.items() if n <= RARE_CHAR_MAX_ENTRIES}
        if not rare_chars:
            continue
        for row in rows:
            text = row.get("text") or ""
            present_rare = sorted(set(text) & rare_chars)
            if present_rare:
                flags.append({"id": row.get("id", ""), "language": lang,
                              "check": "rare_character",
                              "detail": f"contains character(s) rare in {lang} (<= {RARE_CHAR_MAX_ENTRIES} entries dataset-wide): {present_rare}"})
    return flags


def check_pii(rows: list[dict]) -> list[dict]:
    flags = []
    for row in rows:
        for field in ("text", "translation_en", "region", "dialect", "domain"):
            value = row.get(field) or ""
            if not value:
                continue
            hits = []
            if EMAIL_RE.search(value):
                hits.append("email")
            if URL_RE.search(value):
                hits.append("url")
            if HANDLE_RE.search(value):
                hits.append("@handle")
            if UG_PHONE_RE.search(value):
                hits.append("ugandan_phone")
            if NG_PHONE_RE.search(value):
                hits.append("nigerian_phone")
            if INTL_PHONE_RE.search(value):
                hits.append("international_phone")
            if LONG_DIGIT_RUN_RE.search(value) and "ugandan_phone" not in hits and "nigerian_phone" not in hits:
                hits.append("long_digit_run")
            if CAP_TOKEN_RE.search(value):
                hits.append("capitalised_token(name?)")
            for hit in hits:
                flags.append({"id": row.get("id", ""), "language": row.get("language", ""),
                              "check": "possible_pii",
                              "detail": f"field '{field}' matched pattern '{hit}'"})
    return flags


def check_metadata_consistency(rows: list[dict]) -> list[dict]:
    flags = []
    # contributor_id / reviewer_id format is covered in check_schema_and_required.
    # Region spelling consistency: group near-identical region strings.
    regions = sorted({(r.get("region") or "").strip() for r in rows if r.get("region")})
    for i in range(len(regions)):
        for j in range(i + 1, len(regions)):
            a, b = regions[i], regions[j]
            if a.casefold() == b.casefold():
                continue  # exact case-insensitive match is fine, not flagged
            ratio = difflib.SequenceMatcher(None, a.casefold(), b.casefold()).ratio()
            if ratio >= REGION_SIMILARITY_THRESHOLD:
                for row in rows:
                    if (row.get("region") or "").strip() in (a, b):
                        flags.append({"id": row.get("id", ""), "language": row.get("language", ""),
                                      "check": "region_spelling_inconsistent",
                                      "detail": f"region '{row.get('region')}' is similar to (but not identical to) another spelling in use: compare '{a}' vs '{b}'"})
    return flags


def check_language_label_sanity(rows_by_lang: dict[str, list[dict]]) -> list[dict]:
    """Heuristic only — both languages use Latin script, so this cannot
    reliably tell Luganda from Yoruba. It can only flag entries that look
    unusually like English, or whose character profile is closer to the
    OTHER language's profile than to its own, built from this dataset."""
    flags = []

    # Build per-language character-frequency profiles (normalised).
    profiles: dict[str, Counter] = {}
    for lang, rows in rows_by_lang.items():
        counter: Counter = Counter()
        for row in rows:
            counter.update(ch for ch in (row.get("text") or "").lower() if ch.isalpha())
        total = sum(counter.values()) or 1
        profiles[lang] = Counter({ch: n / total for ch, n in counter.items()})

    for lang, rows in rows_by_lang.items():
        other_langs = [l for l in profiles if l != lang]
        for row in rows:
            text = row.get("text") or ""
            words = re.findall(r"[A-Za-z']+", text.lower())
            if len(words) >= 3:
                english_share = sum(1 for w in words if w in COMMON_ENGLISH_WORDS) / len(words)
                if english_share >= ENGLISH_STOPWORD_FRACTION:
                    flags.append({"id": row.get("id", ""), "language": lang,
                                  "check": "language_looks_like_english",
                                  "detail": f"{english_share:.0%} of words are common English function words — human review needed"})

            own_score = _profile_similarity(text, profiles.get(lang, Counter()))
            for other in other_langs:
                other_score = _profile_similarity(text, profiles.get(other, Counter()))
                if other_score > own_score and (own_score + other_score) > 0:
                    flags.append({"id": row.get("id", ""), "language": lang,
                                  "check": "language_looks_like_other_language",
                                  "detail": f"character profile closer to '{other}' ({other_score:.3f}) than to '{lang}' ({own_score:.3f}) — heuristic only, human review needed"})
    return flags


def _profile_similarity(text: str, profile: Counter) -> float:
    chars = [ch for ch in text.lower() if ch.isalpha()]
    if not chars or not profile:
        return 0.0
    return sum(profile.get(ch, 0.0) for ch in chars) / len(chars)


def check_diacritic_consistency(rows_by_lang: dict[str, list[dict]]) -> tuple[list[dict], dict]:
    flags = []
    summary = {}
    for lang, rows in rows_by_lang.items():
        with_marks = 0
        without_marks = 0
        mixed_style = 0
        non_nfc = 0
        for row in rows:
            text = row.get("text") or ""
            rid = row.get("id", "")
            if unicodedata.normalize("NFC", text) != text:
                non_nfc += 1
                flags.append({"id": rid, "language": lang, "check": "non_nfc_text",
                              "detail": "text is not in NFC form (contains a decomposed sequence NFC would change)"})
            has_combining = any(unicodedata.category(ch) in ("Mn", "Mc") for ch in text)
            has_tone = any(ch in YORUBA_TONE_MARK_CHARS for ch in text) or has_combining and lang == "lug"
            has_subdot = any(ch in YORUBA_SUBDOT_CHARS for ch in text)
            if has_tone or has_subdot or has_combining:
                with_marks += 1
            else:
                without_marks += 1
            if lang == "yor" and has_tone and has_subdot:
                mixed_style += 1
                flags.append({"id": rid, "language": lang, "check": "diacritic_mixed_style",
                              "detail": "entry appears to mix tone-mark and subdot conventions (heuristic; human review needed)"})
        total = max(with_marks + without_marks, 1)
        summary[lang] = {
            "with_marks": with_marks,
            "without_marks": without_marks,
            "with_marks_pct": with_marks / total * 100,
            "mixed_style": mixed_style,
            "non_nfc": non_nfc,
        }
    return flags, summary


def check_translation_sanity(rows: list[dict]) -> list[dict]:
    flags = []
    ratios_by_lang: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        text = (row.get("text") or "").strip()
        translation = (row.get("translation_en") or "").strip()
        rid, lang = row.get("id", ""), row.get("language", "")
        if not translation:
            flags.append({"id": rid, "language": lang, "check": "translation_empty",
                          "detail": "translation_en is empty"})
            continue
        if text and translation.casefold() == text.casefold():
            flags.append({"id": rid, "language": lang, "check": "translation_identical_to_source",
                          "detail": "translation_en is identical to text"})
        if text:
            ratio = len(translation) / max(len(text), 1)
            ratios_by_lang[lang].append(ratio)
            if ratio < TRANSLATION_RATIO_MIN or ratio > TRANSLATION_RATIO_MAX:
                flags.append({"id": rid, "language": lang, "check": "translation_length_ratio_outlier",
                              "detail": f"translation/text length ratio {ratio:.2f} outside [{TRANSLATION_RATIO_MIN}, {TRANSLATION_RATIO_MAX}]"})
    return flags


# ---------------------------------------------------------------------------
# Report writing
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--dataset", type=Path, default=base / "data" / "processed" / "dataset.jsonl")
    parser.add_argument("--reports-dir", type=Path, default=base / "reports")
    args = parser.parse_args()

    rows = load_dataset(args.dataset)
    rows_by_lang = by_language(rows)

    all_flags: list[dict] = []
    all_flags += check_schema_and_required(rows)
    all_flags += check_empty_or_short(rows)
    all_flags += check_duplicates_within_language(rows)
    all_flags += check_duplicates_across_languages(rows)
    all_flags += check_length_outliers(rows_by_lang)
    all_flags += check_character_anomalies(rows_by_lang)
    pii_flags = check_pii(rows)
    all_flags += pii_flags
    all_flags += check_metadata_consistency(rows)
    all_flags += check_language_label_sanity(rows_by_lang)
    diacritic_flags, diacritic_summary = check_diacritic_consistency(rows_by_lang)
    all_flags += diacritic_flags
    all_flags += check_translation_sanity(rows)

    common.write_csv(
        args.reports_dir / "flags.csv",
        ["id", "language", "check", "detail"],
        all_flags,
    )

    write_validation_md(args.reports_dir / "validation.md", rows, rows_by_lang, all_flags,
                         pii_flags, diacritic_summary)

    print(f"Validated {len(rows)} entries across {len(rows_by_lang)} language(s).")
    print(f"{len(all_flags)} total flags written to {args.reports_dir / 'flags.csv'}")
    print(f"{len(pii_flags)} possible-PII flags.")
    return 0


def write_validation_md(path: Path, rows, rows_by_lang, all_flags, pii_flags, diacritic_summary) -> None:
    by_check_lang: dict[tuple[str, str], int] = Counter()
    for f in all_flags:
        by_check_lang[(f["check"], f["language"])] += 1

    checks = sorted({f["check"] for f in all_flags})
    langs = sorted(rows_by_lang.keys())

    lines = ["# Automated validation report", ""]
    lines.append(f"Total entries: {len(rows)}. Languages present: {', '.join(langs) or '(none)'}.")
    lines.append("")
    lines.append(
        f"**PII check: {'FAIL' if pii_flags else 'PASS'}** "
        f"({len(pii_flags)} possible-PII item(s) flagged in reports/flags.csv). "
        "`scripts/build_release.py` refuses to run while this is FAIL."
    )
    lines.append("")

    lines.append("## Checks per language")
    lines.append("")
    header = "| Check | " + " | ".join(langs) + " | Total |"
    sep = "|---|" + "---|" * (len(langs) + 1)
    lines.append(header)
    lines.append(sep)
    for check in checks:
        row_counts = [by_check_lang.get((check, lang), 0) for lang in langs]
        lines.append(f"| `{check}` | " + " | ".join(str(c) for c in row_counts) + f" | {sum(row_counts)} |")
    if not checks:
        lines.append("| *(no flags raised)* | " + " | ".join("0" for _ in langs) + " | 0 |")

    lines.append("")
    lines.append("## Diacritic consistency per language")
    lines.append("")
    lines.append("| Language | Entries with tone/subdot marks | Entries with none | % with marks | Mixed-style flags | Non-NFC entries |")
    lines.append("|---|---|---|---|---|---|")
    for lang in langs:
        s = diacritic_summary.get(lang, {})
        lines.append(
            f"| {common.LANGUAGE_NAMES.get(lang, lang)} | {s.get('with_marks', 0)} | "
            f"{s.get('without_marks', 0)} | {s.get('with_marks_pct', 0):.1f}% | "
            f"{s.get('mixed_style', 0)} | {s.get('non_nfc', 0)} |"
        )

    lines.append("")
    lines.append("## Limitations (read before trusting any flag above)")
    lines.append("")
    lines.append(
        "- **Language-label sanity** (`language_looks_like_english`, "
        "`language_looks_like_other_language`): both Luganda and Yoruba use "
        "Latin script, so this cannot be verified by script alone — the "
        "check only compares an entry's characters/words against this "
        "dataset's own character profile and a generic list of common "
        "English function words. It is a hint for a human reviewer, not a "
        "verdict, and can both over- and under-flag."
    )
    lines.append(
        "- **Personal-name detection**: Yoruba and Luganda personal names "
        "cannot be reliably detected automatically. The `capitalised_token` "
        "PII hint only flags a capitalised word that isn't at the start of "
        "the text — most such flags will be false positives (proper nouns, "
        "sentence-internal capitalisation) and most real names will NOT be "
        "flagged unless capitalised unusually. Human review is required for "
        "any name-related judgement."
    )
    lines.append(
        "- **Rare-character / length-outlier checks** are computed from this "
        "dataset's own distribution, which is small (150-250 entries per "
        "language target) — with few entries, thresholds are noisy and may "
        "flag legitimate variation as anomalous."
    )
    lines.append(
        "- **Diacritic mixed-style check** is a coarse heuristic based on a "
        "small hardcoded set of Yoruba tone-mark and subdot code points; it "
        "does not encode real Yoruba orthographic rules and needs a fluent "
        "reviewer to confirm."
    )
    lines.append(
        "- **PII patterns** (email/phone/URL/@handle/long-digit-run) catch "
        "only known shapes; they cannot catch identifying information "
        "phrased in prose (e.g. \"my brother who lives on X street\")."
    )
    lines.append("")
    lines.append("Flags are written to `reports/flags.csv` (columns: id, language, "
                  "check, detail) for a human reviewer to work through — see "
                  "`scripts/make_review_sheet.py`. Nothing is auto-deleted or "
                  "auto-edited based on a flag.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
