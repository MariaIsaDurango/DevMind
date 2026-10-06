import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture()
def rag_module(monkeypatch):
    """Carga rag_chain sin necesitar una API key real de Groq."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    import src.backend.rag_chain as rag_chain

    return rag_chain


def test_grounding_envia_al_llm_el_contexto_recuperado(
    rag_module, monkeypatch
):
    """El contexto recuperado debe formar parte del prompt enviado al LLM."""

    recovered_document = SimpleNamespace(
        page_content=(
            "[Despliegue] Ejecutar kubectl rollout restart "
            "deployment/api para reiniciar el servicio."
        ),
        metadata={
            "source": "runbook.md",
            "score": 0.95,
        },
    )

    class FakeRetriever:
        def invoke(self, prompt):
            assert prompt == "¿Cómo reinicio el servicio?"
            return [recovered_document]

    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["request"] = kwargs

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=(
                                "Puedes reiniciar el servicio con "
                                "kubectl rollout restart deployment/api."
                            )
                        )
                    )
                ]
            )

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(rag_module, "client", FakeClient())

    answer, sources = rag_module.query_rag(
        "¿Cómo reinicio el servicio?",
        retriever=FakeRetriever(),
    )

    system_message = captured["request"]["messages"][0]["content"]

    assert "kubectl rollout restart deployment/api" in system_message
    assert answer.startswith("Puedes reiniciar")
    assert sources[0]["file_path"] == "runbook.md"


def test_grounding_conserva_la_trazabilidad_de_las_fuentes(
    rag_module, monkeypatch
):
    """Las fuentes recuperadas deben devolverse para permitir trazabilidad."""

    documents = [
        SimpleNamespace(
            page_content="El despliegue utiliza Kubernetes.",
            metadata={
                "source": "guia_despliegue.md",
                "score": 0.91,
            },
        ),
        SimpleNamespace(
            page_content="El servicio se ejecuta en producción.",
            metadata={
                "source": "runbook.md",
                "score": 0.87,
            },
        ),
    ]

    class FakeRetriever:
        def invoke(self, prompt):
            return documents

    class FakeCompletions:
        def create(self, **kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content="La información está respaldada por la documentación."
                        )
                    )
                ]
            )

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(rag_module, "client", FakeClient())

    answer, sources = rag_module.query_rag(
        "¿Cómo se despliega el servicio?",
        retriever=FakeRetriever(),
    )

    assert answer == "La información está respaldada por la documentación."
    assert len(sources) == 2
    assert sources[0]["file_path"] == "guia_despliegue.md"
    assert sources[1]["file_path"] == "runbook.md"

def test_grounding_prompt_restringe_la_respuesta_al_contexto(
    rag_module, monkeypatch
):
    """El prompt debe restringir la respuesta a la información recuperada."""

    recovered_document = SimpleNamespace(
        page_content="El servicio utiliza Kubernetes para sus despliegues.",
        metadata={
            "source": "runbook.md",
            "score": 0.90,
        },
    )

    class FakeRetriever:
        def invoke(self, prompt):
            return [recovered_document]

    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["request"] = kwargs

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=(
                                "No dispongo de suficiente información "
                                "en la documentación para responder."
                            )
                        )
                    )
                ]
            )

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(rag_module, "client", FakeClient())

    answer, _ = rag_module.query_rag(
        "¿Cuál es el precio de la licencia Enterprise?",
        retriever=FakeRetriever(),
    )

    system_message = captured["request"]["messages"][0]["content"]

    assert "Utiliza exclusivamente" in system_message
    assert "Si la respuesta no se encuentra en el contexto" in system_message
    assert "indícalo educadamente" in system_message
    assert "No dispongo de suficiente información" in answer
