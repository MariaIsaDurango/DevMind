"""
Función pública acordada en docs/arquitectura.md:
    process_file(path) = list[Document]
"""
from pathlib import Path

from langchain_core.documents import Document

from .chunking import split_documents
from .loaders import SUPPORTED_EXTENSIONS, load_file
from .metadata import extract_doc_info


def process_file(path: str | Path) -> list[Document]:
    """Carga + limpia + divide en chunks + añade metadatos de un archivo."""
    docs = load_file(path)
    if not docs:
        return []
    # Repositorio y tecnología se deducen del documento completo (no página a página)
    full_text = "\n".join(d.page_content for d in docs)
    repository, tech_stack = extract_doc_info(full_text, Path(path).name)
    return split_documents(docs, repository=repository, tech_stack=tech_stack)


def process_directory(directory: str | Path) -> list[Document]:
    """Procesa todos los archivos soportados de una carpeta (no recursivo en subcarpetas ocultas)."""
    chunks: list[Document] = []
    for file in sorted(Path(directory).rglob("*")):
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            chunks.extend(process_file(file))
    return chunks
