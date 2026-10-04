import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vectorstore import embeddings  # noqa: E402


class FakeEmbeddings:
    calls = 0

    def __init__(self, **kwargs):
        type(self).calls += 1
        self.kwargs = kwargs


def test_get_embeddings_usa_modelo_configurado_y_reutiliza_instancia(monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(embeddings, "HuggingFaceEmbeddings", FakeEmbeddings)
    embeddings.get_embeddings.cache_clear()
    FakeEmbeddings.calls = 0

    first = embeddings.get_embeddings()
    second = embeddings.get_embeddings()

    assert first is second
    assert FakeEmbeddings.calls == 1
    assert first.kwargs == {
        "model_name": "modelo-de-prueba",
        "encode_kwargs": {"normalize_embeddings": True},
    }
