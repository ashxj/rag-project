from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.rag import list_categories, search

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="RAG Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    category: str | None = None
    top_k: int = 5


@app.get("/api/categories")
def get_categories() -> dict[str, list[str]]:
    return {"categories": list_categories()}


@app.post("/api/search")
def search_endpoint(payload: SearchRequest) -> dict[str, list[dict[str, str | float]]]:
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Meklesanas pieprasijums nedrikst but tuks")

    if payload.category and payload.category not in list_categories():
        raise HTTPException(status_code=400, detail="Nezinama kategorija")

    results = search(
        query=payload.query,
        category=payload.category,
        top_k=max(1, min(payload.top_k, 20)),
    )

    return {
        "results": [
            {
                "category": item.category,
                "source": item.source,
                "score": round(item.score, 4),
                "chunk": item.chunk,
            }
            for item in results
        ]
    }


@app.get("/")
def root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
