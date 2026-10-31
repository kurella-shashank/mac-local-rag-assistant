
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@dataclass
class Document:
    file_path: str
    file_name: str
    file_type: str
    content: str


def read_document(file_path: Path) -> Document:
    path = Path(file_path).expanduser()

    if path.is_symlink():
        raise ValueError("Symbolic links are not supported")

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 5 MB limit")

    content = path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError("Document is empty")

    return Document(
        file_path=str(path.resolve()),
        file_name=path.name,
        file_type=path.suffix.lower(),
        content=content,
    )
