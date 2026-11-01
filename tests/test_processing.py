
import pytest

from mac_local_rag.ingestion.reader import Document
from mac_local_rag.processing.normalizer import normalize_text
from mac_local_rag.processing.chunker import chunk_document


def make_document(content: str) -> Document:
    return Document(
        file_path="/test/example.txt",
        file_name="example.txt",
        file_type=".txt",
        content=content,
    )


def test_normalize_line_endings():
    result = normalize_text("Hello\r\nWorld\rTest")
    assert result == "Hello\nWorld\nTest"


def test_normalize_excessive_blank_lines():
    result = normalize_text("Hello\n\n\n\nWorld")
    assert result == "Hello\n\nWorld"


def test_preserves_technical_identifiers():
    result = normalize_text(
        "account_id = 12345\nAWS-Glue-Prod-01"
    )
    assert "account_id = 12345" in result
    assert "AWS-Glue-Prod-01" in result


def test_small_document_creates_one_chunk():
    chunks = chunk_document(
        make_document("AWS Glue reads data from S3.")
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0


def test_large_document_creates_multiple_chunks():
    document = make_document(
        "AWS Glue processes data from S3.\n\n" * 40
    )

    chunks = chunk_document(document)

    assert len(chunks) > 1
    assert all(len(chunk.content) <= 500 for chunk in chunks)


def test_chunk_source_metadata():
    chunks = chunk_document(
        make_document("Qdrant stores embeddings.")
    )

    assert chunks[0].file_name == "example.txt"
    assert chunks[0].file_path == "/test/example.txt"


def test_invalid_chunk_overlap():
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_document(
            make_document("Test document"),
            chunk_size=100,
            chunk_overlap=100,
        )
