
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from docx import Document as WordDocument
from docx.table import Table
from docx.text.paragraph import Paragraph


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@dataclass
class Document:
    file_path: str
    file_name: str
    file_type: str
    content: str


def extract_pdf(path: Path) -> str:
    reader = PdfReader(path, strict=False)

    if reader.is_encrypted:
        raise ValueError("Password-protected PDF is not supported")

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)

    return "\n\n".join(pages)


def extract_docx(path: Path) -> str:
    document = WordDocument(path)
    sections = []

    for block in document.iter_inner_content():
        if isinstance(block, Paragraph):
            if block.text.strip():
                sections.append(block.text)

        elif isinstance(block, Table):
            for row in block.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                ]
                sections.append(" | ".join(cells))

    return "\n".join(sections)


def read_document(file_path: Path) -> Document:
    path = Path(file_path).expanduser()

    if path.is_symlink():
        raise ValueError("Symbolic links are not supported")

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 5 MB limit")

    if extension in {".txt", ".md"}:
        content = path.read_text(encoding="utf-8")
    elif extension == ".pdf":
        content = extract_pdf(path)
    else:
        content = extract_docx(path)

    if not content.strip():
        raise ValueError(
            "No extractable text found in document"
        )

    return Document(
        file_path=str(path.resolve()),
        file_name=path.name,
        file_type=extension,
        content=content,
    )
