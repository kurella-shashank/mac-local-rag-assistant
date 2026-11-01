
import argparse
from pathlib import Path

from mac_local_rag.ingestion.reader import read_document
from .chunker import chunk_document


def main():
    parser = argparse.ArgumentParser(
        description="Extract and chunk one local document"
    )
    parser.add_argument("file", type=Path)

    args = parser.parse_args()

    document = read_document(args.file)
    chunks = chunk_document(document)

    print(f"File: {document.file_name}")
    print(f"Chunks created: {len(chunks)}")

    for chunk in chunks:
        print(f"\nChunk {chunk.chunk_index}")
        print(chunk.content)


if __name__ == "__main__":
    main()
