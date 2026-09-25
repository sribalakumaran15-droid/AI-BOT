import json
import pickle
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "uploads" / "rag_store.pkl"


def _load() -> list[dict[str, Any]]:
    if not STORE.exists():
        return []
    try:
        with STORE.open("rb") as file:
            return pickle.load(file)
    except (pickle.PickleError, EOFError):
        return []


def _save(documents: list[dict[str, Any]]) -> None:
    STORE.parent.mkdir(exist_ok=True)
    with STORE.open("wb") as file:
        pickle.dump(documents, file)


def _chunks(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    words = text.split()
    return [" ".join(words[start:start + size]) for start in range(0, len(words), size - overlap) if words[start:start + size]]


def index_document(source: str, text: str) -> int:
    documents = [item for item in _load() if item["source"] != source]
    documents.extend({"source": source, "text": chunk} for chunk in _chunks(text))
    _save(documents)
    return len([item for item in documents if item["source"] == source])


def search_documents(query: str, limit: int = 3) -> list[dict[str, Any]]:
    documents = _load()
    if not documents or not query.strip():
        return []
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([item["text"] for item in documents])
    scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
    ranked = scores.argsort()[::-1]
    return [documents[index] | {"score": float(scores[index])} for index in ranked[:limit] if scores[index] >= 0.08]


def clear_index() -> None:
    if STORE.exists():
        STORE.unlink()
