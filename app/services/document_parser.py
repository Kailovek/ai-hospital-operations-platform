from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from app.core.errors import AppError

MAX_DOCUMENT_BYTES = 15 * 1024 * 1024


def parse_document(filename: str, content: bytes) -> str:
    if len(content) > MAX_DOCUMENT_BYTES:
        raise AppError(413, "document_too_large", "Document exceeds the 15 MB limit")
    suffix = Path(filename).suffix.lower()
    try:
        if suffix in {".txt", ".md"}:
            return content.decode("utf-8-sig")
        if suffix == ".docx":
            document = Document(BytesIO(content))
            return "\n\n".join(
                paragraph.text for paragraph in document.paragraphs if paragraph.text
            )
        if suffix == ".pdf":
            reader = PdfReader(BytesIO(content))
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    except (UnicodeDecodeError, OSError, ValueError) as exc:
        raise AppError(
            400, "document_parse_failed", "Document content could not be parsed"
        ) from exc
    raise AppError(
        415, "unsupported_document_format", "Supported formats are PDF, DOCX, TXT, and Markdown"
    )


def chunk_document(text: str, maximum_characters: int = 800, overlap: int = 120) -> list[str]:
    paragraphs = [part.strip() for part in text.replace("\r\n", "\n").split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip()
        if current and len(candidate) > maximum_characters:
            chunks.append(current)
            current = f"{current[-overlap:]}\n\n{paragraph}".strip()
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
