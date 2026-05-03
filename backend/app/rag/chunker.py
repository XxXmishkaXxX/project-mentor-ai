import re
from dataclasses import dataclass, field
from pathlib import Path

from app.common.config import StaticConfig


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)


def parse_file(file_path: str | Path) -> str:
    p = Path(file_path)
    ext = p.suffix.lower()

    if ext not in StaticConfig.SUPPORTED_EXTENSIONS:
        msg = f"Unsupported file extension: {ext}"
        raise ValueError(msg)

    if ext == ".pdf":
        return _parse_pdf(p)
    if ext == ".docx":
        return _parse_docx(p)
    return _parse_text(p)


def _parse_pdf(file_path: Path) -> str:
    from PyPDF2 import PdfReader

    reader = PdfReader(str(file_path))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _parse_docx(file_path: Path) -> str:
    from docx import Document

    doc = Document(str(file_path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def _parse_text(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def split_into_chunks(
    text: str,
    *,
    chunk_size: int = 512,
    overlap: int = 64,
    file_name: str = "",
) -> list[Chunk]:
    """Split text into overlapping chunks by sentences/paragraphs."""
    if chunk_size <= 0:
        msg = f"chunk_size must be positive, got {chunk_size}"
        raise ValueError(msg)
    if overlap < 0:
        msg = f"overlap must be non-negative, got {overlap}"
        raise ValueError(msg)
    if overlap >= chunk_size:
        msg = f"overlap ({overlap}) must be less than chunk_size ({chunk_size})"
        raise ValueError(msg)

    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks: list[Chunk] = []
    current_parts: list[str] = []
    current_len = 0
    chunk_index = 0

    for sentence in sentences:
        join_cost = 1 if current_parts else 0
        sentence_len = len(sentence) + join_cost

        if current_len + sentence_len > chunk_size and current_parts:
            chunks.append(
                _make_chunk(current_parts, file_name, chunk_index),
            )
            chunk_index += 1

            current_parts = _collect_overlap(current_parts, overlap)
            current_len = _joined_len(current_parts)

        if len(sentence) > chunk_size:
            if current_parts:
                chunks.append(
                    _make_chunk(current_parts, file_name, chunk_index),
                )
                chunk_index += 1
                current_parts = []
                current_len = 0

            for sub in _hard_split(sentence, chunk_size):
                chunks.append(
                    _make_chunk([sub], file_name, chunk_index),
                )
                chunk_index += 1
            continue

        current_parts.append(sentence)
        current_len += sentence_len

    if current_parts:
        chunks.append(
            _make_chunk(current_parts, file_name, chunk_index),
        )

    return chunks


def _make_chunk(
    parts: list[str],
    file_name: str,
    chunk_index: int,
) -> Chunk:
    return Chunk(
        text=" ".join(parts).strip(),
        metadata={
            "file_name": file_name,
            "chunk_index": chunk_index,
        },
    )


def _collect_overlap(parts: list[str], overlap: int) -> list[str]:
    """Pick trailing sentences that fit within the overlap budget."""
    result: list[str] = []
    budget = 0
    for part in reversed(parts):
        cost = len(part) + (1 if result else 0)
        if budget + cost > overlap:
            break
        result.insert(0, part)
        budget += cost
    return result


def _joined_len(parts: list[str]) -> int:
    if not parts:
        return 0
    return sum(len(p) for p in parts) + len(parts) - 1


def _hard_split(text: str, size: int) -> list[str]:
    """Force-split an oversized sentence into pieces."""
    return [text[i : i + size] for i in range(0, len(text), size)]


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n{2,}")


def _split_sentences(text: str) -> list[str]:
    """Split text by sentence boundaries and paragraph breaks."""
    parts = _SENTENCE_SPLIT_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]
