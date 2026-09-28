"""Unit tests for scripts/validate_auto.py's individual checks, using only
synthetic in-memory rows (TEST_* placeholders)."""
import validate_auto as va


def row(**kwargs):
    base = {
        "id": "lug-0001", "language": "lug", "text": "TEST placeholder text here",
        "translation_en": "TEST placeholder translation", "contributor_id": "C001",
        "region": None, "dialect": None, "date_collected": "2026-01",
        "source_type": "self-written", "domain": "test", "reviewed": False,
        "reviewer_id": None, "reviewed_by_independent": False,
    }
    base.update(kwargs)
    return base


def test_required_field_missing_flags_empty_translation():
    rows = [row(translation_en="")]
    flags = va.check_schema_and_required(rows)
    checks = {f["check"] for f in flags}
    assert "required_field_missing" in checks


def test_schema_language_invalid():
    rows = [row(language="fra")]
    flags = va.check_schema_and_required(rows)
    assert any(f["check"] == "schema_language_invalid" for f in flags)


def test_empty_and_very_short_text():
    rows = [row(id="lug-0001", text=""), row(id="lug-0002", text="ab")]
    flags = va.check_empty_or_short(rows)
    by_id = {f["id"]: f["check"] for f in flags}
    assert by_id["lug-0001"] == "empty_text"
    assert by_id["lug-0002"] == "very_short_text"


def test_duplicate_within_language():
    rows = [
        row(id="lug-0001", text="TEST_DUP same"),
        row(id="lug-0002", text="TEST_DUP same"),
    ]
    flags = va.check_duplicates_within_language(rows)
    assert len(flags) == 1
    assert flags[0]["id"] == "lug-0002"


def test_duplicate_across_languages_flags_possible_mislabel():
    rows = [
        row(id="lug-0001", language="lug", text="TEST_SAME_TEXT_ACROSS"),
        row(id="yor-0001", language="yor", text="TEST_SAME_TEXT_ACROSS"),
    ]
    flags = va.check_duplicates_across_languages(rows)
    assert len(flags) == 1
    assert flags[0]["id"] == "yor-0001"


def test_pii_detects_email_and_ugandan_and_nigerian_phone():
    rows = [
        row(id="lug-0001", text="TEST contact test@example.com here"),
        row(id="lug-0002", text="TEST call 0771234567 now"),
        row(id="lug-0003", text="TEST call 08031234567 now"),  # NG-shaped
    ]
    flags = va.check_pii(rows)
    checks_by_id = {}
    for f in flags:
        checks_by_id.setdefault(f["id"], set()).add(f["detail"])
    assert any("email" in d for d in checks_by_id.get("lug-0001", []))
    assert any("ugandan_phone" in d for d in checks_by_id.get("lug-0002", []))
    assert any("nigerian_phone" in d for d in checks_by_id.get("lug-0003", []))


def test_translation_sanity_empty_identical_and_ratio_outlier():
    rows = [
        row(id="lug-0001", text="TEST source", translation_en=""),
        row(id="lug-0002", text="TEST_SAME", translation_en="TEST_SAME"),
        row(id="lug-0003", text="TEST short", translation_en="TEST " + "x" * 200),
    ]
    flags = va.check_translation_sanity(rows)
    checks_by_id = {}
    for f in flags:
        checks_by_id.setdefault(f["id"], set()).add(f["check"])
    assert "translation_empty" in checks_by_id["lug-0001"]
    assert "translation_identical_to_source" in checks_by_id["lug-0002"]
    assert "translation_length_ratio_outlier" in checks_by_id["lug-0003"]


def test_length_outliers_flags_extreme_entry():
    rows = [row(id=f"lug-{i:04d}", text="TEST normal length entry here") for i in range(10)]
    rows.append(row(id="lug-9999", text="TEST " + "x" * 500))
    by_lang = {"lug": rows}
    flags = va.check_length_outliers(by_lang)
    assert any(f["id"] == "lug-9999" for f in flags)


def test_diacritic_consistency_flags_non_nfc_text():
    decomposed = "TEST café"  # not NFC
    rows = [row(id="lug-0001", text=decomposed)]
    flags, summary = va.check_diacritic_consistency({"lug": rows})
    assert any(f["check"] == "non_nfc_text" for f in flags)
    assert summary["lug"]["non_nfc"] == 1
