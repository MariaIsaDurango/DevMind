import sys
import math
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.documents import Document  # noqa: E402

from src.ingestion.metadata import build_metadata  # noqa: E402


class FakeEmbeddings:
    """Embeddings deterministas para probar Chroma sin descargar un modelo."""

    _vocabulary = ("despliegue", "kubectl", "facturacion", "usuarios", "serv")

    def _embed(self, text: str) -> list[float]:
        lowered = text.lower()
        vector = [float(word in lowered) for word in self._vocabulary]
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


@pytest.fixture()
def vectorstore_config(tmp_path, monkeypatch):
    """Aísla cada prueba de la base persistente y del modelo real."""
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("COLLECTION_NAME", "test_collection")
    monkeypatch.setattr("src.vectorstore.store.get_embeddings", lambda: FakeEmbeddings())
    from src.vectorstore.store import get_vectorstore

    get_vectorstore.cache_clear()
    return tmp_path


def _documents() -> list[Document]:
    return [
        Document(
            page_content="[Despliegue] Ejecutar kubectl rollout restart para reiniciar el servicio.",
            metadata=build_metadata("runbook.md", "Despliegue", "platform", "Kubernetes", 1)
            | {"chunk_id": "runbook.md::0"},
        ),
        Document(
            page_content="[Facturacion] El cierre mensual se procesa el ultimo dia habil.",
            metadata=build_metadata("finanzas.md", "Facturacion", "finance", "N/A", 1)
            | {"chunk_id": "finanzas.md::0"},
        ),
    ]


def test_indexa_y_recupera_el_fragmento_semanticamente_relevante(vectorstore_config):
    from src.vectorstore.retriever import get_retriever
    from src.vectorstore.store import index_documents

    assert index_documents(_documents()) == 2

    results = get_retriever(k=1).invoke("¿Cómo reinicio el servicio con kubectl?")

    assert len(results) == 1
    assert "kubectl rollout restart" in results[0].page_content


def test_retrieval_conserva_los_metadatos_de_trazabilidad(vectorstore_config):
    from src.vectorstore.retriever import get_retriever
    from src.vectorstore.store import index_documents

    index_documents(_documents())
    result = get_retriever(k=1).invoke("¿Cómo reinicio el servicio?")[0]

    assert result.metadata["source"] == "runbook.md"
    assert result.metadata["section"] == "Despliegue"
    assert result.metadata["repository"] == "platform"
    assert result.metadata["page"] == 1


def test_la_base_persistente_se_puede_reabrir(vectorstore_config):
    from src.vectorstore.retriever import get_retriever
    from src.vectorstore.store import index_documents

    index_documents(_documents())

    from src.vectorstore.store import get_vectorstore

    get_vectorstore.cache_clear()
    result = get_retriever(k=1).invoke("¿Qué comando uso para kubectl?")[0]

    assert result.metadata["source"] == "runbook.md"


def test_reindexar_los_mismos_chunks_no_duplica_documentos(vectorstore_config):
    from src.vectorstore.store import get_collection, index_documents

    documents = _documents()
    assert index_documents(documents) == 2
    assert index_documents(documents) == 2

    assert get_collection().count() == 2


def test_reindexar_un_archivo_elimina_sus_chunks_obsoletos(vectorstore_config):
    from src.vectorstore.store import get_collection, index_documents

    documents = _documents()
    index_documents(documents)
    updated = Document(
        page_content="[Despliegue] Ejecutar kubectl rollout restart --namespace produccion.",
        metadata=build_metadata("runbook.md", "Despliegue", "platform", "Kubernetes", 1)
        | {"chunk_id": "runbook.md::nuevo"},
    )

    index_documents([updated])
    stored = get_collection().get(where={"source": "runbook.md"})

    assert stored["ids"] == ["runbook.md::nuevo"]
    assert get_collection().count() == 2
