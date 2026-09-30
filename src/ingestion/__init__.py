"""Módulo de ingesta (MariaI).

Función pública acordada en docs/arquitectura.md:
    process_file(path) -> list[Document]
"""
import logging
from pathlib import Path

from langchain_core.documents import Document

from .chunking import split_documents
from .errors import IngestionError
from .loaders import SUPPORTED_EXTENSIONS, load_file
from .metadata import extract_doc_info

logger = logging.getLogger(__name__)


def process_file(path: str | Path) -> list[Document]:
    """Carga + limpia + divide en chunks + añade metadatos de un archivo.

    Lanza IngestionError si el archivo no existe, tiene una extensión no
    soportada, o está corrupto (p. ej. un PDF dañado). El backend (P3) debe
    capturar IngestionError y devolver 400 con el mensaje.

    Devuelve una lista vacía si el archivo es válido pero no tiene texto
    extraíble (archivo vacío o PDF escaneado sin OCR); no es un error.
    """
    docs = load_file(path)
    if not docs:
        return []
    # Repositorio y tecnología se deducen del documento completo (no página a página)
    full_text = "\n".join(d.page_content for d in docs)
    repository, tech_stack = extract_doc_info(full_text, Path(path).name)
    return split_documents(docs, repository=repository, tech_stack=tech_stack)


def process_directory(directory: str | Path) -> list[Document]:
    """Procesa todos los archivos soportados de una carpeta, incluidas subcarpetas.

    Si un archivo falla (IngestionError), se registra un aviso y se sigue
    con el resto en vez de detener todo el lote.

    Nota: si dos archivos en subcarpetas distintas tienen el mismo nombre,
    su metadato 'source' será idéntico (solo se usa el nombre, no la ruta
    completa). Evita nombres de archivo repetidos entre subcarpetas de
    data/raw para no mezclar sus fuentes en la trazabilidad.
    """
    chunks: list[Document] = []
    for file in sorted(Path(directory).rglob("*")):
        if not (file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS):
            continue
        try:
            chunks.extend(process_file(file))
        except IngestionError as e:
            logger.warning("Se omitió '%s': %s", file, e)
    return chunks
