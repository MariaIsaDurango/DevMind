"""Almacenamiento persistente de documentos en ChromaDB."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document

from .embeddings import get_embeddings

DEFAULT_CHROMA_PATH = "./data/processed/chroma"
DEFAULT_COLLECTION_NAME = "devmind_docs"


def _l2_relevance_score(distance: float) -> float:
    """Convierte la distancia L2 de Chroma normalizada en score [0, 1]."""
    return max(0.0, 1.0 - distance / 2.0)


def _chroma_path() -> str:
    return os.getenv("CHROMA_PATH", DEFAULT_CHROMA_PATH)


def _collection_name() -> str:
    return os.getenv("COLLECTION_NAME", DEFAULT_COLLECTION_NAME)


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    """Devuelve la instancia persistente de Chroma para el proceso actual."""
    Path(_chroma_path()).mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=_collection_name(),
        embedding_function=get_embeddings(),
        persist_directory=_chroma_path(),
        relevance_score_fn=_l2_relevance_score,
    )


def get_collection() -> Any:
    """Expone la colección nativa para inspecciones y comprobaciones de conteo."""
    return get_vectorstore()._collection  # type: ignore[reportPrivateUsage]


def _existing_ids_by_source(source: str) -> set[str]:
    result = get_collection().get(where={"source": source})
    return set(result.get("ids", []))


def index_documents(docs: list[Document]) -> int:
    """Inserta o actualiza chunks y elimina los obsoletos del mismo archivo."""
    if not docs:
        return 0

    ids = [str(doc.metadata.get("chunk_id", "")) for doc in docs]
    if any(not chunk_id for chunk_id in ids):
        raise ValueError("Cada documento debe incluir metadata['chunk_id']")
    if len(ids) != len(set(ids)):
        raise ValueError("Los chunk_id deben ser únicos dentro de una indexación")

    vectorstore = get_vectorstore()
    collection = get_collection()
    existing_ids = set(collection.get().get("ids", []))

    docs_by_source: dict[str, list[tuple[str, Document]]] = {}
    for chunk_id, doc in zip(ids, docs):
        source = str(doc.metadata.get("source", ""))
        docs_by_source.setdefault(source, []).append((chunk_id, doc))

    for source, source_docs in docs_by_source.items():
        source_ids = {chunk_id for chunk_id, _ in source_docs}
        stale_ids = _existing_ids_by_source(source) - source_ids
        if stale_ids:
            vectorstore.delete(ids=list(stale_ids))

    existing_docs = [doc for chunk_id, doc in zip(ids, docs) if chunk_id in existing_ids]
    existing_doc_ids = [chunk_id for chunk_id in ids if chunk_id in existing_ids]
    new_docs = [doc for chunk_id, doc in zip(ids, docs) if chunk_id not in existing_ids]
    new_doc_ids = [chunk_id for chunk_id in ids if chunk_id not in existing_ids]

    if existing_docs:
        vectorstore.update_documents(existing_doc_ids, existing_docs)
    if new_docs:
        vectorstore.add_documents(new_docs, ids=new_doc_ids)
    return len(docs)
