"""Unit and integration tests for scripts/apply_corrections.py, using only
synthetic in-memory/tmp_path data (TEST_* placeholders)."""
import csv
import sys

import apply_corrections as ac
import common


def test_parse_correction_single_field():
    result = ac.parse_correction("translation_en: TEST a better gloss")
    assert result == {"translation_en": "TEST a better gloss"}


def test_parse_correction_multi_field():
    result = ac.parse_correction("text: TEST fixed text | domain: proverb")
    assert result == {"text": "TEST fixed text", "domain": "proverb"}


def test_parse_correction_ignores_unrecognised_field():
    result = ac.parse_correction("made_up_field: TEST value")
    assert result == {}


def test_parse_correction_blank():
    assert ac.parse_correction("") == {}
    assert ac.parse_correction("   ") == {}


def _write_dataset(tmp_path, rows):
    path = tmp_path / "dataset.jsonl"
    common.write_jsonl(path, rows)
    return path


def _write_sheet(tmp_path, name, rows):
    review_dir = tmp_path / "review"
    review_dir.mkdir(exist_ok=True)
    path = review_dir / f"{name}.csv"
    fieldnames = ["id", "language", "text", "translation_en", "auto_flags",
                  "reviewer_verdict", "reviewer_correction", "reviewer_notes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            full = {k: r.get(k, "") for k in fieldnames}
            w.writerow(full)
    return review_dir


def _sheet_row(rid, lang, verdict="", correction=""):
    return {"id": rid, "language": lang, "text": "TEST text", "translation_en": "TEST en",
            "auto_flags": "", "reviewer_verdict": verdict, "reviewer_correction": correction,
            "reviewer_notes": ""}


def test_layer2_text_correction_is_blocked_and_routed_to_conflicts(tmp_path):
    dataset = [{
        "id": "yor-0001", "language": "yor", "text": "TEST original text",
        "translation_en": "TEST original en", "contributor_id": "C101", "region": None,
        "dialect": None, "date_collected": "2026-01", "source_type": "self-written",
        "domain": "test", "reviewed": False, "reviewer_id": None, "reviewed_by_independent": False,
    }]
    dataset_path = _write_dataset(tmp_path, dataset)
    review_dir = tmp_path / "review"
    review_dir.mkdir(exist_ok=True)
    _write_sheet(tmp_path, "layer1_lug", [])
    _write_sheet(tmp_path, "layer1_yor", [])
    _write_sheet(tmp_path, "layer2_by_author1", [
        _sheet_row("yor-0001", "yor", verdict="needs_correction", correction="text: TEST should not apply")
    ])
    _write_sheet(tmp_path, "layer2_by_author2", [])

    out_path = tmp_path / "dataset_corrected.jsonl"
    log_path = tmp_path / "corrections_log.csv"
    conflicts_path = tmp_path / "conflicts.csv"

    argv_backup = sys.argv
    try:
        sys.argv = ["apply_corrections.py", "--dataset", str(dataset_path),
                    "--review-dir", str(review_dir), "--out", str(out_path),
                    "--log", str(log_path), "--conflicts", str(conflicts_path)]
        rc = ac.main()
    finally:
        sys.argv = argv_backup

    assert rc == 0
    corrected = common.read_jsonl(out_path)
    assert corrected[0]["text"] == "TEST original text"  # unchanged
    conflicts = common.read_csv(conflicts_path)
    assert any(c["reason"] == "layer2_text_correction_requires_language_reviewer" for c in conflicts)
    log = common.read_csv(log_path)
    assert log == []  # nothing applied


def test_conflicting_non_text_corrections_are_not_applied(tmp_path):
    dataset = [{
        "id": "lug-0001", "language": "lug", "text": "TEST original text",
        "translation_en": "TEST original en", "contributor_id": "C001", "region": "OldRegion",
        "dialect": None, "date_collected": "2026-01", "source_type": "self-written",
        "domain": "test", "reviewed": False, "reviewer_id": None, "reviewed_by_independent": False,
    }]
    dataset_path = _write_dataset(tmp_path, dataset)
    review_dir = tmp_path / "review"
    review_dir.mkdir(exist_ok=True)
    _write_sheet(tmp_path, "layer1_lug", [])
    _write_sheet(tmp_path, "layer1_yor", [])
    _write_sheet(tmp_path, "layer2_by_author1", [
        _sheet_row("lug-0001", "lug", verdict="ok", correction="region: RegionA")
    ])
    _write_sheet(tmp_path, "layer2_by_author2", [
        _sheet_row("lug-0001", "lug", verdict="ok", correction="region: RegionB")
    ])

    out_path = tmp_path / "dataset_corrected.jsonl"
    log_path = tmp_path / "corrections_log.csv"
    conflicts_path = tmp_path / "conflicts.csv"
    argv_backup = sys.argv
    try:
        sys.argv = ["apply_corrections.py", "--dataset", str(dataset_path),
                    "--review-dir", str(review_dir), "--out", str(out_path),
                    "--log", str(log_path), "--conflicts", str(conflicts_path)]
        rc = ac.main()
    finally:
        sys.argv = argv_backup

    assert rc == 0
    corrected = common.read_jsonl(out_path)
    assert corrected[0]["region"] == "OldRegion"  # neither applied
    conflicts = common.read_csv(conflicts_path)
    assert any(c["reason"] == "conflicting_corrections" and c["field"] == "region" for c in conflicts)


def test_layer1_text_correction_is_applied_and_marks_independent_review(tmp_path):
    dataset = [{
        "id": "lug-0001", "language": "lug", "text": "TEST original text",
        "translation_en": "TEST original en", "contributor_id": "C001", "region": None,
        "dialect": None, "date_collected": "2026-01", "source_type": "self-written",
        "domain": "test", "reviewed": False, "reviewer_id": None, "reviewed_by_independent": False,
    }]
    dataset_path = _write_dataset(tmp_path, dataset)
    review_dir = tmp_path / "review"
    review_dir.mkdir(exist_ok=True)
    _write_sheet(tmp_path, "layer1_lug", [
        _sheet_row("lug-0001", "lug", verdict="needs_correction", correction="text: TEST corrected text")
    ])
    _write_sheet(tmp_path, "layer1_yor", [])
    _write_sheet(tmp_path, "layer2_by_author1", [])
    _write_sheet(tmp_path, "layer2_by_author2", [])

    out_path = tmp_path / "dataset_corrected.jsonl"
    log_path = tmp_path / "corrections_log.csv"
    conflicts_path = tmp_path / "conflicts.csv"
    argv_backup = sys.argv
    try:
        sys.argv = ["apply_corrections.py", "--dataset", str(dataset_path),
                    "--review-dir", str(review_dir), "--out", str(out_path),
                    "--log", str(log_path), "--conflicts", str(conflicts_path)]
        rc = ac.main()
    finally:
        sys.argv = argv_backup

    assert rc == 0
    corrected = common.read_jsonl(out_path)
    assert corrected[0]["text"] == "TEST corrected text"
    assert corrected[0]["reviewed"] is True
    assert corrected[0]["reviewed_by_independent"] is True
    assert corrected[0]["reviewer_id"] == "R01"
