"""Retriever semantico sobre la coleccion persistente de Chroma."""
import os

from langchain_core.retrievers import BaseRetriever

from .store import get_vectorstore

DEFAULT_TOP_K = 4
DEFAULT_SIMILARITY_THRESHOLD = 0.30


def _configured_top_k() -> int:
    value = int(os.getenv("TOP_K", str(DEFAULT_TOP_K)))
    if value < 1:
        raise ValueError("TOP_K debe ser mayor que cero")
    return value


def _configured_threshold() -> float:
    value = float(os.getenv("SIMILARITY_THRESHOLD", str(DEFAULT_SIMILARITY_THRESHOLD)))
    if not 0 <= value <= 1:
        raise ValueError("SIMILARITY_THRESHOLD debe estar entre 0 y 1")
    return value


def get_retriever(k: int | None = None) -> BaseRetriever:
    """Crea un retriever por similitud con limite de resultados y umbral."""
    top_k = _configured_top_k() if k is None else k
    if top_k < 1:
        raise ValueError("k debe ser mayor que cero")
    return get_vectorstore().as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": top_k,
            "score_threshold": _configured_threshold(),
        },
    )
