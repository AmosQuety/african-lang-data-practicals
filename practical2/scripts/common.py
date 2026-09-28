"""Shared constants and helpers for the Practical 2 pipeline.

Standard-library only, on purpose (see DECISIONS.md: NETWORK RULES / no
non-stdlib dependency risk for the core pipeline). Every pipeline script
imports from here so the schema, field list, and normalisation rules are
defined in exactly one place.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

LANGUAGES = ("lug", "yor")
LANGUAGE_NAMES = {"lug": "Luganda", "yor": "Yoruba"}

# Column order matches docs/raw_template.csv and docs/SCHEMA.md.
ALL_FIELDS = [
    "id",
    "language",
    "text",
    "translation_en",
    "contributor_id",
    "region",
    "dialect",
    "date_collected",
    "source_type",
    "domain",
    "reviewed",
    "reviewer_id",
    "reviewed_by_independent",
]

REQUIRED_FIELDS = [
    "id",
    "language",
    "text",
    "translation_en",
    "contributor_id",
    "source_type",
    "reviewed",
    "reviewed_by_independent",
]

OPTIONAL_FIELDS = [f for f in ALL_FIELDS if f not in REQUIRED_FIELDS]

BOOLEAN_FIELDS = ("reviewed", "reviewed_by_independent")

SOURCE_TYPES = ("self-written", "volunteer-contributed", "proverb", "other")

ID_PATTERN = re.compile(r"^[a-z]{3}-[0-9]{4,}$")
CONTRIBUTOR_ID_PATTERN = re.compile(r"^C[0-9]{3,}$")
REVIEWER_ID_PATTERN = re.compile(r"^R[0-9]{2,}$")
DATE_COLLECTED_PATTERN = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])$")

SCHEMA_JSON_PATH = Path(__file__).resolve().parent.parent / "docs" / "schema.json"


def load_json_schema() -> dict:
    with open(SCHEMA_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Boolean parsing (raw CSV values arrive as text: TRUE/FALSE/yes/no/1/0/blank)
# ---------------------------------------------------------------------------

_TRUE_STRINGS = {"true", "yes", "y", "1"}
_FALSE_STRINGS = {"false", "no", "n", "0", ""}


def parse_bool(raw_value: str | None) -> bool:
    """Parse a raw CSV boolean-ish value.

    Blank/missing is treated as False (see DECISIONS.md D009: at
    collection time these columns are normally left blank, meaning "not
    yet reviewed").
    """
    return parse_bool_strict(raw_value)[0]


def parse_bool_strict(raw_value: str | None) -> tuple[bool, bool]:
    """Like parse_bool, but also returns whether the raw value was one of
    the recognised spellings. (value, recognised). An unrecognised
    non-blank value (e.g. a typo like "flase") still resolves to False so
    preprocessing never crashes, but callers (preprocess.py) log it as an
    anomaly so it isn't silently lost — see DECISIONS.md D009."""
    if raw_value is None:
        return False, True
    value = raw_value.strip().lower()
    if value in _TRUE_STRINGS:
        return True, True
    if value in _FALSE_STRINGS:
        return False, True
    return False, False


# ---------------------------------------------------------------------------
# Text normalisation primitives (Stage 3)
# ---------------------------------------------------------------------------

# Curly quote / apostrophe variants normalised to straight ASCII.
# NOTE: does NOT include U+02BC (MODIFIER LETTER APOSTROPHE) or any
# combining diacritical marks / tone marks — those may be phonemic in
# Luganda or Yoruba and must never be touched (DECISIONS.md D005).
_QUOTE_MAP = {
    "‘": "'",  # LEFT SINGLE QUOTATION MARK
    "’": "'",  # RIGHT SINGLE QUOTATION MARK
    "‚": "'",  # SINGLE LOW-9 QUOTATION MARK
    "‛": "'",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK
    "“": '"',  # LEFT DOUBLE QUOTATION MARK
    "”": '"',  # RIGHT DOUBLE QUOTATION MARK
    "„": '"',  # DOUBLE LOW-9 QUOTATION MARK
    "‟": '"',  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
}
_QUOTE_RE = re.compile("|".join(re.escape(k) for k in _QUOTE_MAP))

# Characters to drop as "invisible" (Stage 3b): Unicode category Cf (format
# characters — zero-width space/joiner/non-joiner, LRM/RLM/BOM, etc.) and
# Cc (control characters) other than the whitespace we handle separately.
# Combining marks (category Mn/Mc), which carry tone/diacritic information,
# are category M* and are never touched here.
_KEEP_CONTROL = {"\t", "\n", "\r"}


def strip_invisible(text: str) -> str:
    out_chars = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat == "Cf":
            continue
        if cat == "Cc" and ch not in _KEEP_CONTROL:
            continue
        out_chars.append(ch)
    return "".join(out_chars)


_LINEBREAK_RE = re.compile(r"\r\n|\r")
_SPACE_RUN_RE = re.compile(r"[ \t]+")
_MULTI_BLANK_LINE_RE = re.compile(r"\n{3,}")


def normalise_whitespace(text: str) -> str:
    text = _LINEBREAK_RE.sub("\n", text)
    text = _SPACE_RUN_RE.sub(" ", text)
    text = _MULTI_BLANK_LINE_RE.sub("\n\n", text)
    # trim each line, then trim the whole string
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines).strip()
    return text


def normalise_quotes(text: str) -> str:
    return _QUOTE_RE.sub(lambda m: _QUOTE_MAP[m.group(0)], text)


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def preprocess_text(text: str) -> tuple[str, dict[str, bool]]:
    """Run the four per-field text normalisation steps in order, returning
    the final text and a dict of which steps actually changed something."""
    changed = {}

    step1 = nfc(text)
    changed["nfc"] = step1 != text

    step2 = strip_invisible(step1)
    changed["invisible"] = step2 != step1

    step3 = normalise_whitespace(step2)
    changed["whitespace"] = step3 != step2

    step4 = normalise_quotes(step3)
    changed["quotes"] = step4 != step3

    return step4, changed


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def record_to_schema(row: dict, anomalies: list[dict] | None = None) -> dict:
    """Coerce a raw-CSV-shaped dict into the strict processed schema shape
    (booleans as real booleans, optional blanks as None).

    If `anomalies` is given, any unrecognised boolean-field spelling is
    appended to it as {id, language, field, raw_value} so it can be
    reported rather than silently dropped (DECISIONS.md D009)."""
    out = {}
    for field in ALL_FIELDS:
        value = row.get(field, "")
        value = "" if value is None else str(value)
        if field in BOOLEAN_FIELDS:
            parsed, recognised = parse_bool_strict(value)
            out[field] = parsed
            if not recognised and anomalies is not None:
                anomalies.append(
                    {
                        "id": row.get("id", ""),
                        "language": row.get("language", ""),
                        "field": field,
                        "raw_value": value,
                    }
                )
        elif field in OPTIONAL_FIELDS:
            out[field] = value.strip() if value.strip() != "" else None
        else:
            out[field] = value.strip()
    return out


def schema_row_to_flat(row: dict) -> dict:
    """Inverse of record_to_schema for CSV export: booleans -> TRUE/FALSE,
    None -> ''."""
    out = {}
    for field in ALL_FIELDS:
        value = row.get(field)
        if field in BOOLEAN_FIELDS:
            out[field] = "TRUE" if value else "FALSE"
        elif value is None:
            out[field] = ""
        else:
            out[field] = value
    return out
