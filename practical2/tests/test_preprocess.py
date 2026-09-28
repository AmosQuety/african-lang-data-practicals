"""Unit and integration tests for scripts/preprocess.py, using only the
synthetic fixtures in tests/fixtures/."""
import preprocess
import common

from conftest import FIXTURES_DIR


def make_row(**kwargs):
    base = {
        "id": "", "language": "cgg", "text": "TEST placeholder", "translation_en": "TEST placeholder en",
        "contributor_id": "C001", "region": "", "dialect": "", "date_collected": "2026-01",
        "source_type": "self-written", "domain": "test", "reviewed": "", "reviewer_id": "",
        "reviewed_by_independent": "", "_source_file": "test.csv",
    }
    base.update(kwargs)
    return base


def test_assign_ids_sequential_per_language():
    rows = [common.record_to_schema(make_row(language="cgg")) for _ in range(3)]
    rows += [common.record_to_schema(make_row(language="yor")) for _ in range(2)]
    for r, src in zip(rows, ["a"] * 3 + ["b"] * 2):
        r["_source_file"] = src
    preprocess.assign_ids(rows)
    cgg_ids = [r["id"] for r in rows if r["language"] == "cgg"]
    yor_ids = [r["id"] for r in rows if r["language"] == "yor"]
    assert cgg_ids == ["cgg-0001", "cgg-0002", "cgg-0003"]
    assert yor_ids == ["yor-0001", "yor-0002"]


def test_assign_ids_preserves_existing_valid_id_and_avoids_collision():
    rows = [
        common.record_to_schema(make_row(id="cgg-0005", language="cgg")),
        common.record_to_schema(make_row(language="cgg")),  # should NOT become cgg-0001, must avoid 0005
    ]
    preprocess.assign_ids(rows)
    assert rows[0]["id"] == "cgg-0005"
    assert rows[1]["id"] == "cgg-0006"


def test_remove_exact_duplicates_keeps_first_and_logs_rest():
    rows = [
        common.record_to_schema(make_row(id="cgg-0001", language="cgg", text="TEST_DUP same text")),
        common.record_to_schema(make_row(id="cgg-0002", language="cgg", text="TEST_DUP same text")),
        common.record_to_schema(make_row(id="cgg-0003", language="cgg", text="TEST_DUP different text")),
    ]
    kept, removed = preprocess.remove_exact_duplicates(rows)
    assert [r["id"] for r in kept] == ["cgg-0001", "cgg-0003"]
    assert len(removed) == 1
    assert removed[0]["id"] == "cgg-0002"
    assert removed[0]["duplicate_of_id"] == "cgg-0001"


def test_flag_near_duplicates_detects_similar_not_identical_text():
    rows = [
        common.record_to_schema(make_row(id="cgg-0001", language="cgg", text="TEST_NEARDUP aaaaaaaaaa")),
        common.record_to_schema(make_row(id="cgg-0002", language="cgg", text="TEST_NEARDUP aaaaaaaaab")),  # 1 char different, high similarity
        common.record_to_schema(make_row(id="cgg-0003", language="cgg", text="TEST_NEARDUP completely_different_zzzzz")),
    ]
    flags = preprocess.flag_near_duplicates(rows)
    flagged_pairs = {(f["id_a"], f["id_b"]) for f in flags}
    assert ("cgg-0001", "cgg-0002") in flagged_pairs
    assert not any("cgg-0003" in pair for pair in flagged_pairs)


def test_normalise_rows_applies_quote_and_whitespace_cleanup_and_logs_changes():
    rows = [common.record_to_schema(make_row(
        id="cgg-0001", language="cgg",
        text="  TEST_NORM ‘quoted’  text  ",
        translation_en="TEST_NORM en",
    ))]
    normalised, changes = preprocess.normalise_rows(rows)
    assert normalised[0]["text"] == "TEST_NORM 'quoted' text"
    steps = {c["step"] for c in changes if c["id"] == "cgg-0001" and c["field"] == "text"}
    assert "whitespace" in steps
    assert "quotes" in steps


def test_load_and_combine_detects_cross_file_id_conflict(tmp_path):
    raw_dir = FIXTURES_DIR
    files = preprocess.find_raw_files(raw_dir)
    assert len(files) >= 2  # the checked-in synthetic author1/author2 fixtures
    combined, conflicts, skipped = preprocess.load_and_combine(files)
    assert not skipped
    conflict_ids = {c["id"] for c in conflicts}
    assert "id-conflict-001" in conflict_ids
    # The conflicting row should have been excluded from combined (first kept only)
    kept_conflict_rows = [r for r in combined if r.get("id") == "id-conflict-001"]
    assert len(kept_conflict_rows) == 1


def test_full_preprocess_pipeline_end_to_end(tmp_path):
    out_dir = tmp_path / "processed"
    reports_dir = tmp_path / "reports"
    import argparse
    import sys

    argv_backup = sys.argv
    try:
        sys.argv = [
            "preprocess.py",
            "--raw-dir", str(FIXTURES_DIR),
            "--out-dir", str(out_dir),
            "--reports-dir", str(reports_dir),
        ]
        rc = preprocess.main()
    finally:
        sys.argv = argv_backup

    assert rc == 0
    dataset_path = out_dir / "dataset.jsonl"
    assert dataset_path.exists()
    rows = common.read_jsonl(dataset_path)
    assert len(rows) > 0
    for row in rows:
        assert row["language"] in ("cgg", "yor")
        assert row["id"]
    assert (reports_dir / "preprocess_summary.md").exists()
    assert (reports_dir / "duplicates_removed.csv").exists()
    assert (reports_dir / "id_conflicts.csv").exists()
