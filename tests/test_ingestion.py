
import pytest

from mac_local_rag.ingestion.reader import read_document


def test_txt_extraction(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("AWS Glue processes S3 data.")

    result = read_document(file)

    assert result.content == "AWS Glue processes S3 data."
    assert result.file_type == ".txt"


def test_markdown_extraction(tmp_path):
    file = tmp_path / "notes.md"
    file.write_text("# RAG Architecture")

    result = read_document(file)

    assert result.content == "# RAG Architecture"


def test_unsupported_extension(tmp_path):
    file = tmp_path / "image.png"
    file.write_bytes(b"sample")

    with pytest.raises(ValueError, match="Unsupported"):
        read_document(file)


def test_empty_file(tmp_path):
    file = tmp_path / "empty.txt"
    file.write_text("")

    with pytest.raises(ValueError, match="empty"):
        read_document(file)


def test_invalid_encoding(tmp_path):
    file = tmp_path / "invalid.txt"
    file.write_bytes(b"\xff\xfe")

    with pytest.raises(UnicodeError):
        read_document(file)


def test_symlink_rejected(tmp_path):
    original = tmp_path / "original.txt"
    original.write_text("Private document")

    link = tmp_path / "link.txt"
    link.symlink_to(original)

    with pytest.raises(ValueError, match="Symbolic"):
        read_document(link)
