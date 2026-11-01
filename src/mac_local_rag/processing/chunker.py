
from dataclasses import dataclass
from langchain_text_splitters import (RecursiveCharacterTextSplitter,)

from mac_local_rag.ingestion.reader import Document
from .normalizer import normalize_text


@dataclass
class DocumentChunk:
    file_path: str
    file_name: str
    chunk_index: int
    content: str


def chunk_document(
    document: Document,
    chunk_size: int = 500,
    chunk_overlap: int = 75,
) -> list[DocumentChunk]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    text = normalize_text(document.content)

    if not text:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    pieces = splitter.split_text(text)

    return [
        DocumentChunk(
            file_path=document.file_path,
            file_name=document.file_name,
            chunk_index=index,
            content=piece,
        )
        for index, piece in enumerate(pieces)
    ]
