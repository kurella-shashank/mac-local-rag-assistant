
import argparse
from pathlib import Path

from .scanner import scan_directory
from .database import MetadataDatabase


DEFAULT_DB = Path("data/indexes/metadata.db")


def main():
    parser = argparse.ArgumentParser(
        description="Mac Local RAG — Filesystem Discovery"
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="SQLite database location",
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True
    )

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("directory", type=Path)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("keyword")

    subparsers.add_parser("stats")

    args = parser.parse_args()

    db = MetadataDatabase(args.db)

    if args.command == "scan":
        records = scan_directory(args.directory)

        root = str(
            args.directory.expanduser().resolve(strict=True)
        )

        db.save_scan(root, records)

        print(f"Scan completed: {root}")
        print(f"Indexed entries: {len(records)}")

    elif args.command == "search":
        results = db.search(args.keyword)

        if not results:
            print("No matching filenames found.")

        for result in results:
            location = (
                Path(result["source_root"])
                / result["relative_path"]
            )
            print(f'{result["kind"]}: {location}')

    elif args.command == "stats":
        total, files, directories = db.count_entries()

        print(f"Total entries: {total}")
        print(f"Files: {files}")
        print(f"Directories: {directories}")


if __name__ == "__main__":
    main()
