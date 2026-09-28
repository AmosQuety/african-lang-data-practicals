"""Unit tests for scripts/common.py normalisation primitives.

All test strings are synthetic placeholders (TEST_*), never real
Rukiga/Yoruba/English data, and diacritic test data uses explicit Unicode
escapes as required by the DATA SAFETY RULES.
"""
import unicodedata

import common


def test_nfc_normalises_decomposed_to_composed_without_changing_meaning():
    # 'e' + COMBINING ACUTE ACCENT (decomposed) vs precomposed 'é' (composed)
    decomposed = "TEST_SENTENCE_001 café sample"
    composed = "TEST_SENTENCE_001 café sample"
    assert decomposed != composed  # different byte sequences going in

    cleaned_decomposed, changes_d = common.preprocess_text(decomposed)
    cleaned_composed, changes_c = common.preprocess_text(composed)

    # Both normalise to the SAME final string (NFC), proving NFC only
    # changes encoding, not content.
    assert cleaned_decomposed == cleaned_composed == composed
    assert changes_d["nfc"] is True
    assert changes_c["nfc"] is False

    # The visible character sequence (after full Unicode NFC normalisation
    # of both) is identical — no diacritic was stripped or added.
    assert unicodedata.normalize("NFC", decomposed) == unicodedata.normalize("NFC", composed)


def test_nfc_never_strips_combining_marks():
    # A synthetic string with several combining diacritics that must survive.
    text = "TEST_DIACRITIC_002 áèîọṵ"
    cleaned, changes = common.preprocess_text(text)
    # Every combining mark's base+mark pair should still decompose to the
    # same combining marks after our pipeline (round-trip via NFD).
    original_marks = [ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) in ("Mn", "Mc")]
    cleaned_marks = [ch for ch in unicodedated_nfd(cleaned) if unicodedata.category(ch) in ("Mn", "Mc")]
    assert sorted(original_marks) == sorted(cleaned_marks)


def unicodedated_nfd(text):
    return unicodedata.normalize("NFD", text)


def test_strip_invisible_removes_zero_width_space_but_not_combining_marks():
    text = "TEST_SENTENCE_003 a​b"  # zero-width space between a and b
    out = common.strip_invisible(text)
    assert "​" not in out
    assert out == "TEST_SENTENCE_003 ab"

    with_mark = "TEST_SENTENCE_004 é"  # e + combining acute accent
    out2 = common.strip_invisible(with_mark)
    assert "́" in out2  # combining mark preserved


def test_normalise_quotes_only_touches_curly_variants():
    text = "TEST_QUOTE_005 ‘single’ and “double”"
    out = common.normalise_quotes(text)
    assert out == "TEST_QUOTE_005 'single' and \"double\""

    # Modifier letter apostrophe (used phonemically in some African
    # languages) must NOT be touched.
    phonemic = "TEST_QUOTE_006 woʼyo"
    assert common.normalise_quotes(phonemic) == phonemic


def test_normalise_whitespace_trims_and_collapses():
    text = "  TEST_WS_007   multiple   spaces  \t here \r\n and a line break  "
    out = common.normalise_whitespace(text)
    assert out == "TEST_WS_007 multiple spaces here\nand a line break"
    assert "  " not in out  # no doubled spaces remain
    assert not out.startswith(" ") and not out.endswith(" ")


def test_parse_bool_strict_recognised_and_unrecognised():
    assert common.parse_bool_strict("TRUE") == (True, True)
    assert common.parse_bool_strict("false") == (False, True)
    assert common.parse_bool_strict("") == (False, True)
    assert common.parse_bool_strict(None) == (False, True)
    assert common.parse_bool_strict("yes") == (True, True)
    assert common.parse_bool_strict("flase") == (False, False)  # typo -> unrecognised, defaults False


def test_record_to_schema_logs_boolean_anomalies():
    anomalies = []
    row = {"id": "cgg-0001", "language": "cgg", "reviewed": "flase", "reviewed_by_independent": ""}
    out = common.record_to_schema(row, anomalies)
    assert out["reviewed"] is False
    assert out["reviewed_by_independent"] is False
    assert len(anomalies) == 1
    assert anomalies[0]["field"] == "reviewed"
    assert anomalies[0]["raw_value"] == "flase"
