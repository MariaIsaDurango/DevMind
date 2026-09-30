"""Estrategia de chunking. Justificación en docs/chunking_justificacion.md.

- Markdown: primero se divide por encabezados (así cada chunk sabe a qué
  sección pertenece) y después por tamaño con separadores que respetan
  bloques de código.
- TXT / PDF: RecursiveCharacterTextSplitter por párrafo > línea > frase > palabra.
"""
import os

from langchain_core.documents import Document
from langchain_text_splitters import (
    Language,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from .metadata import DEFAULT_SECTION, build_metadata, extract_doc_info

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120

_HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4")]


def get_chunk_config() -> tuple[int, int]:
    """Lee CHUNK_SIZE y CHUNK_OVERLAP del entorno (.env) o usa los valores por defecto."""
    size = int(os.getenv("CHUNK_SIZE", DEFAULT_CHUNK_SIZE))
    overlap = int(os.getenv("CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP))
    if overlap >= size:
        raise ValueError("CHUNK_OVERLAP debe ser menor que CHUNK_SIZE")
    return size, overlap


def _deepest_header(meta: dict) -> str:
    for key in ("h4", "h3", "h2", "h1"):
        if meta.get(key):
            return meta[key]
    return DEFAULT_SECTION


def _split_markdown(doc: Document, size: int, overlap: int) -> list[tuple[str, str]]:
    header_splitter = MarkdownHeaderTextSplitter(_HEADERS, strip_headers=False)
    size_splitter = RecursiveCharacterTextSplitter.from_language(
        Language.MARKDOWN, chunk_size=size, chunk_overlap=overlap
    )
    result = []
    for section_doc in header_splitter.split_text(doc.page_content):
        section = _deepest_header(section_doc.metadata)
        for piece in size_splitter.split_text(section_doc.page_content):
            result.append((section, piece))
    return result


def _split_plain(doc: Document, size: int, overlap: int) -> list[tuple[str, str]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [(DEFAULT_SECTION, piece) for piece in splitter.split_text(doc.page_content)]


def split_documents(
    docs: list[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    repository: str | None = None,
    tech_stack: str | None = None,
) -> list[Document]:
    """Divide los documentos en chunks con metadatos completos."""
    default_size, default_overlap = get_chunk_config()
    size = chunk_size or default_size
    overlap = default_overlap if chunk_overlap is None else chunk_overlap

    chunks: list[Document] = []
    for doc in docs:
        source = doc.metadata["source"]
        page = doc.metadata.get("page", 1)
        repo, tech = repository, tech_stack
        if repo is None or tech is None:
            found_repo, found_tech = extract_doc_info(doc.page_content, source)
            repo = repo or found_repo
            tech = tech or found_tech

        splitter = _split_markdown if source.lower().endswith(".md") else _split_plain
        for section, text in splitter(doc, size, overlap):
            text = text.strip()
            if not text:
                continue
            chunks.append(
                Document(
                    page_content=text,
                    metadata=build_metadata(source, section, repo, tech, page),
                )
            )
    return chunks
