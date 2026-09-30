import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion import process_directory, process_file  # noqa: E402
from src.ingestion.chunking import split_documents  # noqa: E402
from src.ingestion.loaders import clean_text, load_file  # noqa: E402
from src.ingestion.metadata import build_metadata, extract_doc_info  # noqa: E402

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
REQUIRED_KEYS = {"source", "section", "repository", "tech_stack", "page"}


def test_clean_text_normaliza_saltos_y_espacios():
    assert clean_text("hola  \r\n\r\n\r\n\r\nmundo\x00  \n") == "hola\n\nmundo"


def test_markdown_genera_chunks_con_metadatos_completos():
    chunks = process_file(RAW / "guia_despliegue_cicd.md")
    assert chunks
    for c in chunks:
        assert REQUIRED_KEYS <= set(c.metadata)
        assert c.metadata["source"] == "guia_despliegue_cicd.md"
        assert isinstance(c.metadata["page"], int)


def test_seccion_y_cabecera_detectadas():
    chunks = process_file(RAW / "guia_despliegue_cicd.md")
    staging = [c for c in chunks if c.metadata["section"] == "Entornos de Staging"]
    assert staging, "Debe existir un chunk de la sección 'Entornos de Staging'"
    assert "git push origin develop" in staging[0].page_content
    assert staging[0].metadata["repository"] == "backend-core"
    assert staging[0].metadata["tech_stack"] == "GitLab CI"


def test_chunks_respetan_tamano_maximo():
    texto = "Párrafo de prueba sobre despliegue. " * 200
    from langchain_core.documents import Document
    doc = Document(page_content=texto, metadata=build_metadata("largo.txt"))
    chunks = split_documents([doc], chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 1
    assert all(len(c.page_content) <= 500 for c in chunks)


def test_overlap_mayor_o_igual_al_tamano_falla(monkeypatch):
    monkeypatch.setenv("CHUNK_SIZE", "100")
    monkeypatch.setenv("CHUNK_OVERLAP", "100")
    with pytest.raises(ValueError):
        process_file(RAW / "api_usuarios.md")


def test_txt_usa_seccion_general(tmp_path):
    f = tmp_path / "nota.txt"
    f.write_text("Instrucciones de reinicio del servicio.\n\nUsar kubectl rollout restart.", encoding="utf-8")
    chunks = process_file(f)
    assert chunks and chunks[0].metadata["section"] == "General"
    assert chunks[0].metadata["tech_stack"] == "Kubernetes"


def test_extension_no_soportada(tmp_path):
    f = tmp_path / "datos.docx"
    f.write_text("x")
    with pytest.raises(ValueError):
        load_file(f)


def test_archivo_inexistente():
    with pytest.raises(FileNotFoundError):
        load_file("no_existe.md")


def test_archivo_vacio_devuelve_lista_vacia(tmp_path):
    f = tmp_path / "vacio.md"
    f.write_text("   \n\n", encoding="utf-8")
    assert process_file(f) == []


def test_pdf_con_texto(tmp_path):
    reportlab = pytest.importorskip("reportlab")
    from reportlab.pdfgen import canvas

    f = tmp_path / "manual.pdf"
    c = canvas.Canvas(str(f))
    c.drawString(72, 750, "Pagina uno: para reiniciar use kubectl.")
    c.showPage()
    c.drawString(72, 750, "Pagina dos: los logs estan en Grafana.")
    c.save()
    chunks = process_file(f)
    assert {c.metadata["page"] for c in chunks} == {1, 2}
    assert all(c.metadata["source"] == "manual.pdf" for c in chunks)


def test_process_directory_procesa_todos_los_documentos():
    chunks = process_directory(RAW)
    fuentes = {c.metadata["source"] for c in chunks}
    assert {"api_usuarios.md", "guia_despliegue_cicd.md", "runbook_infraestructura.md"} <= fuentes


def test_extract_doc_info_sin_cabecera():
    repo, tech = extract_doc_info("Usar docker compose up", "guia.md")
    assert repo == "N/A" and tech == "Docker"
