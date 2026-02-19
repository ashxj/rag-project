from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class SearchResult:
    category: str
    source: str
    chunk: str
    score: float


_WORD_RE = re.compile(r"[\w]+", re.UNICODE)
_LV_NORMALIZE_MAP = str.maketrans(
    {
        "ā": "a",
        "č": "c",
        "ē": "e",
        "ģ": "g",
        "ī": "i",
        "ķ": "k",
        "ļ": "l",
        "ņ": "n",
        "š": "s",
        "ū": "u",
        "ž": "z",
    }
)


def list_categories() -> list[str]:
    if not DATA_DIR.exists():
        return []
    return sorted([p.name for p in DATA_DIR.iterdir() if p.is_dir()])


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]


def _normalize_lv_token(token: str) -> str:
    return token.lower().translate(_LV_NORMALIZE_MAP)


def _chunks(text: str, chunk_size: int = 500, overlap: int = 120) -> Iterable[str]:
    if not text:
        return

    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end == text_len:
            break
        start = max(0, end - overlap)


def _score_chunk(query_tokens: list[str], chunk: str) -> float:
    chunk_tokens = _tokenize(chunk)
    if not chunk_tokens:
        return 0.0

    normalized_query = [_normalize_lv_token(token) for token in query_tokens]
    chunk_set = {_normalize_lv_token(token) for token in chunk_tokens}
    matched = sum(1 for token in normalized_query if token in chunk_set)
    density = matched / max(1, len(chunk_tokens))
    coverage = matched / max(1, len(set(normalized_query)))
    return coverage * 2.0 + density


def _iter_category_files(category: str | None) -> Iterable[tuple[str, Path]]:
    categories = [category] if category else list_categories()
    for cat in categories:
        if not cat:
            continue
        cat_path = DATA_DIR / cat
        if not cat_path.exists() or not cat_path.is_dir():
            continue
        for file_path in cat_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md"}:
                yield cat, file_path


def search(query: str, category: str | None = None, top_k: int = 5) -> list[SearchResult]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    ranked: list[SearchResult] = []

    for cat, file_path in _iter_category_files(category):
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="latin-1", errors="ignore")

        for chunk in _chunks(text):
            score = _score_chunk(query_tokens, chunk)
            if score <= 0:
                continue
            ranked.append(
                SearchResult(
                    category=cat,
                    source=file_path.name,
                    chunk=chunk,
                    score=score,
                )
            )

    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:top_k]
