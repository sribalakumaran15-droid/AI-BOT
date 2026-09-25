import re
from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument

def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    if path.suffix.lower() == ".docx":
        return "\n".join(paragraph.text for paragraph in DocxDocument(str(path)).paragraphs)
    return ""

def clean_and_chunk(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    words = re.sub(r"\s+", " ", text).strip().split(" ")
    step = max(1, size - overlap)
    return [" ".join(words[start:start + size]) for start in range(0, len(words), step) if words[start:start + size]]

def retrieve(chunks, query: str, limit: int = 3):
    terms = {term.lower() for term in re.findall(r"[a-zA-Z]{3,}", query)}
    ranked = []
    for chunk in chunks:
        words = set(re.findall(r"[a-zA-Z]{3,}", chunk.content.lower()))
        score = len(terms & words) / max(1, len(terms))
        ranked.append((score, chunk))
    return [chunk for score, chunk in sorted(ranked, key=lambda pair: pair[0], reverse=True)[:limit] if score > 0]
