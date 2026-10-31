
from pathlib import Path

import pytest

from mac_local_rag.discovery.scanner import scan_directory
from mac_local_rag.discovery.database import MetadataDatabase


@pytest.fixture
def sample_folder(tmp_path):
    root = tmp_path / "documents"
    root.mkdir()

    (root / "aws").mkdir()
    (root / "aws" / "glue.txt").write_text(
        "AWS Glue processes data from S3."
    )
    (root / "notes.txt").write_text(
        "Local RAG assistant."
    )

    return root


def test_scanner_discovers_files_and_directories(sample_folder):
    records = scan_directory(sample_folder)

    assert len(records) == 3
    assert sum(r.kind == "file" for r in records) == 2
    assert sum(r.kind == "directory" for r in records) == 1


def test_database_stores_and_searches(sample_folder, tmp_path):
    database = MetadataDatabase(tmp_path / "test.db")

    records = scan_directory(sample_folder)
    database.save_scan(str(sample_folder), records)

    matches = database.search("glue")

    assert len(matches) == 1
    assert matches[0]["name"] == "glue.txt"


def test_rescan_does_not_duplicate(sample_folder, tmp_path):
    database = MetadataDatabase(tmp_path / "test.db")

    for _ in range(2):
        records = scan_directory(sample_folder)
        database.save_scan(str(sample_folder), records)

    total, files, directories = database.count_entries()

    assert (total, files, directories) == (3, 2, 1)


def test_deleted_file_disappears_after_rescan(
    sample_folder, tmp_path
):
    database = MetadataDatabase(tmp_path / "test.db")

    database.save_scan(
        str(sample_folder), scan_directory(sample_folder)
    )

    (sample_folder / "notes.txt").unlink()

    database.save_scan(
        str(sample_folder), scan_directory(sample_folder)
    )

    assert database.search("notes") == []


def test_hidden_files_are_excluded(sample_folder):
    (sample_folder / ".secret").write_text("test")

    records = scan_directory(sample_folder)

    assert all(r.name != ".secret" for r in records)


def test_symlinks_are_not_followed(sample_folder, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "private.txt").write_text("private")

    (sample_folder / "external").symlink_to(
        outside, target_is_directory=True
    )

    records = scan_directory(sample_folder)

    assert all("private.txt" != r.name for r in records)
    assert all("external" != r.name for r in records)
