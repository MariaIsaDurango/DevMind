"""Configuracion compartida del modelo de embeddings."""
import os
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def get_embedding_model_name() -> str:
    """Devuelve el modelo configurado o el modelo multilingue por defecto."""
    return os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL).strip()


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """Crea y reutiliza la instancia de embeddings para todo el proceso."""
    return HuggingFaceEmbeddings(
        model_name=get_embedding_model_name(),
        encode_kwargs={"normalize_embeddings": True},
    )
