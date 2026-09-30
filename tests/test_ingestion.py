import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.documents import Document  # noqa: E402

from src.ingestion import process_directory, process_file  # noqa: E402
from src.ingestion.chunking import (  # noqa: E402
    MIN_CHUNK_CHARS,
    make_chunk_id,
    split_documents,
)
from src.ingestion.errors import IngestionError  # noqa: E402
from src.ingestion.loaders import clean_text, load_file  # noqa: E402
from src.ingestion.metadata import build_metadata, extract_doc_info  # noqa: E402

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
REQUIRED_KEYS = {"source", "section", "repository", "tech_stack", "page", "chunk_id"}


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
    doc = Document(page_content=texto, metadata=build_metadata("largo.txt"))
    chunks = split_documents([doc], chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 1
    # el prefijo "[Sección] " se suma al tamaño del splitter, por eso el margen
    assert all(len(c.page_content) <= 500 + 20 for c in chunks)


def test_overlap_mayor_o_igual_al_tamano_falla(monkeypatch):
    monkeypatch.setenv("CHUNK_SIZE", "100")
    monkeypatch.setenv("CHUNK_OVERLAP", "100")
    with pytest.raises(ValueError):
        process_file(RAW / "api_usuarios.md")


def test_overlap_explicito_mayor_al_tamano_tambien_falla():
    doc = Document(page_content="texto de prueba", metadata=build_metadata("x.txt"))
    with pytest.raises(ValueError):
        split_documents([doc], chunk_size=100, chunk_overlap=100)


def test_parametros_explicitos_ignoran_el_env(monkeypatch):
    # Si se pasan chunk_size/overlap explícitos, NO deben leer el .env
    monkeypatch.setenv("CHUNK_SIZE", "99999")
    monkeypatch.setenv("CHUNK_OVERLAP", "1")
    texto = "Palabra " * 100
    doc = Document(page_content=texto, metadata=build_metadata("x.txt"))
    chunks = split_documents([doc], chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 1  # con 99999 hubiera dado un solo chunk


def test_txt_usa_seccion_general(tmp_path):
    f = tmp_path / "nota.txt"
    f.write_text("Instrucciones de reinicio del servicio.\n\nUsar kubectl rollout restart.", encoding="utf-8")
    chunks = process_file(f)
    assert chunks and chunks[0].metadata["section"] == "General"
    assert chunks[0].metadata["tech_stack"] == "Kubernetes"


def test_extension_no_soportada(tmp_path):
    f = tmp_path / "datos.docx"
    f.write_text("x")
    with pytest.raises(IngestionError):
        load_file(f)


def test_archivo_inexistente():
    with pytest.raises(IngestionError):
        load_file("no_existe.md")


def test_archivo_vacio_devuelve_lista_vacia(tmp_path):
    f = tmp_path / "vacio.md"
    f.write_text("   \n\n", encoding="utf-8")
    assert process_file(f) == []


def test_pdf_con_texto(tmp_path):
    pytest.importorskip("reportlab")
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


def test_pdf_corrupto_lanza_ingestion_error(tmp_path):
    f = tmp_path / "roto.pdf"
    f.write_bytes(b"esto no es un pdf valido")
    with pytest.raises(IngestionError):
        load_file(f)


def test_process_directory_procesa_todos_los_documentos():
    chunks = process_directory(RAW)
    fuentes = {c.metadata["source"] for c in chunks}
    assert {"api_usuarios.md", "guia_despliegue_cicd.md", "runbook_infraestructura.md"} <= fuentes


def test_process_directory_entra_en_subcarpetas(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nota.md").write_text("# Nota\n\nContenido de prueba en subcarpeta.", encoding="utf-8")
    chunks = process_directory(tmp_path)
    assert any(c.metadata["source"] == "nota.md" for c in chunks)


def test_process_directory_continua_si_un_archivo_falla(tmp_path, caplog):
    (tmp_path / "bueno.md").write_text("# Bueno\n\nTexto valido.", encoding="utf-8")
    (tmp_path / "malo.pdf").write_bytes(b"no es un pdf")
    chunks = process_directory(tmp_path)
    fuentes = {c.metadata["source"] for c in chunks}
    assert "bueno.md" in fuentes
    assert "malo.pdf" not in fuentes


def test_extract_doc_info_sin_cabecera():
    repo, tech = extract_doc_info("Usar docker compose up", "guia.md")
    assert repo == "N/A" and tech == "Docker"


def test_extract_doc_info_evita_falsos_positivos_por_subcadena():
    # "helmets" no debe detectar Kubernetes (helm), "laws" no debe detectar AWS
    repo, tech = extract_doc_info("Uso obligatorio de cascos y helmets de seguridad", "x.md")
    assert tech == "N/A"
    repo, tech = extract_doc_info("Revisar las laws de trafico locales", "x.md")
    assert tech == "N/A"


def test_chunks_cortos_se_fusionan_con_el_siguiente():
    texto = "# Doc\n\n## Larga\n\n" + ("Paso de configuración del despliegue. " * 60)
    doc = Document(page_content=texto, metadata=build_metadata("x.md"))
    chunks = split_documents([doc])
    cortos = [c for c in chunks if len(c.page_content) < MIN_CHUNK_CHARS]
    assert cortos == [], f"No debería haber chunks menores a {MIN_CHUNK_CHARS} chars: {cortos}"


def test_chunk_lleva_prefijo_de_seccion():
    chunks = process_file(RAW / "guia_despliegue_cicd.md")
    staging = [c for c in chunks if c.metadata["section"] == "Entornos de Staging"][0]
    assert staging.page_content.startswith("[Entornos de Staging]")


def test_chunk_id_es_determinista_y_unico():
    id1 = make_chunk_id("x.md", 0, "mismo texto")
    id2 = make_chunk_id("x.md", 0, "mismo texto")
    id3 = make_chunk_id("x.md", 1, "mismo texto")
    assert id1 == id2          # mismo input -> mismo id (permite sobrescribir al reindexar)
    assert id1 != id3          # distinto índice -> distinto id

    chunks = process_file(RAW / "api_usuarios.md")
    ids = [c.metadata["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids)), "Todos los chunk_id de un archivo deben ser únicos"


def test_reindexar_mismo_archivo_da_los_mismos_chunk_ids():
    # Simula relanzar ingest.py o resubir el mismo archivo por /upload
    chunks_1 = process_file(RAW / "runbook_infraestructura.md")
    chunks_2 = process_file(RAW / "runbook_infraestructura.md")
    ids_1 = [c.metadata["chunk_id"] for c in chunks_1]
    ids_2 = [c.metadata["chunk_id"] for c in chunks_2]
    assert ids_1 == ids_2, "P2 puede usar chunk_id como id en Chroma para evitar duplicados"
