
from dataclasses import dataclass
from pathlib import Path
import os


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "data",
}


@dataclass(frozen=True)
class FileRecord:
    source_root: str
    relative_path: str
    name: str
    kind: str
    extension: str
    size_bytes: int
    modified_at: float


def scan_directory(root: Path) -> list[FileRecord]:
    root = root.expanduser().resolve(strict=True)

    if not root.is_dir():
        raise ValueError("The selected path is not a directory.")

    records = []

    def handle_error(error: OSError) -> None:
        raise error

    for current, directories, files in os.walk(
        root, followlinks=False, onerror=handle_error
    ):
        current_path = Path(current)

        directories[:] = sorted(
            name
            for name in directories
            if not name.startswith(".")
            and name not in EXCLUDED_DIRS
            and not (current_path / name).is_symlink()
        )

        for name in directories:
            path = current_path / name
            info = path.stat(follow_symlinks=False)

            records.append(
                FileRecord(
                    source_root=str(root),
                    relative_path=str(path.relative_to(root)),
                    name=name,
                    kind="directory",
                    extension="",
                    size_bytes=0,
                    modified_at=info.st_mtime,
                )
            )

        for name in sorted(files):
            if name.startswith("."):
                continue

            path = current_path / name

            if path.is_symlink() or not path.is_file():
                continue

            info = path.stat(follow_symlinks=False)

            records.append(
                FileRecord(
                    source_root=str(root),
                    relative_path=str(path.relative_to(root)),
                    name=name,
                    kind="file",
                    extension=path.suffix.lower(),
                    size_bytes=info.st_size,
                    modified_at=info.st_mtime,
                )
            )

    return records
