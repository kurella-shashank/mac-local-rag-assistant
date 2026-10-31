
import argparse
from pathlib import Path

from mac_local_rag.discovery.scanner import scan_directory
from .reader import read_document, SUPPORTED_EXTENSIONS


def main():
    parser = argparse.ArgumentParser(
        description="Local document ingestion"
    )
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()

    root = args.directory.expanduser().resolve(strict=True)
    records = scan_directory(root)

    success = 0
    failed = 0

    for record in records:
        if record.kind != "file":
            continue

        if record.extension not in SUPPORTED_EXTENSIONS:
            continue

        path = root / record.relative_path

        try:
            document = read_document(path)
            success += 1

            print(f"\nFile: {document.file_name}")
            print(f"Type: {document.file_type}")
            print(f"Characters: {len(document.content)}")
            print(f"Preview: {document.content[:100]}")

        except (OSError, UnicodeError, ValueError) as error:
            failed += 1
            print(f"Failed: {path.name}: {error}")

    print(f"\nSuccessful: {success}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
