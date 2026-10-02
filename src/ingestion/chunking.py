"""Estrategia de chunking. Justificación en docs/chunking_justificacion.md.

- Markdown: primero se divide por encabezados (así cada chunk sabe a qué
  sección pertenece) y después por tamaño con separadores que respetan
  bloques de código.
- TXT / PDF: RecursiveCharacterTextSplitter por párrafo > línea > frase > palabra.
- Los fragmentos casi vacíos (solo un encabezado suelto) se fusionan con el
  siguiente para no meter en el índice chunks sin significado.
- Cada chunk lleva la sección como prefijo del texto, para que el embedding
  tenga contexto aunque el fragmento se lea aislado.
"""
import hashlib
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
MIN_CHUNK_CHARS = 50  # por debajo de esto, el chunk se fusiona con el siguiente

_HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4")]


def get_chunk_config() -> tuple[int, int]:
    """Lee CHUNK_SIZE y CHUNK_OVERLAP del entorno (.env) o usa los valores por defecto."""
    size = int(os.getenv("CHUNK_SIZE", DEFAULT_CHUNK_SIZE))
    overlap = int(os.getenv("CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP))
    if overlap >= size:
        raise ValueError("CHUNK_OVERLAP debe ser menor que CHUNK_SIZE")
    return size, overlap


def make_chunk_id(source: str, page: int, index: int, text: str) -> str:
    """ID determinista para cada chunk: mismo archivo + mismo contenido = mismo id.

    P2 debe usarlo como id al indexar en Chroma, así reindexar el mismo
    archivo (por ejemplo, reenviarlo por /upload) sobrescribe en vez de
    duplicar.

    La página forma parte del id porque el índice se reinicia en cada página:
    sin ella, dos páginas de un PDF con el mismo texto (portadas, plantillas,
    pies repetidos) generarían el mismo id.
    """
    digest = hashlib.sha256(f"{source}|{page}|{index}|{text}".encode("utf-8")).hexdigest()[:16]
    return f"{source}::p{page}::{index}::{digest}"


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


def _merge_short_pieces(pieces: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Fusiona con el siguiente fragmento cualquier trozo menor a MIN_CHUNK_CHARS
    (p. ej. una línea de encabezado que quedó sola tras dividir por tamaño).
    Si el último trozo de la lista queda corto, se fusiona con el anterior.
    """
    if not pieces:
        return pieces
    merged: list[tuple[str, str]] = []
    carry_section, carry_text = pieces[0]
    for section, text in pieces[1:]:
        if len(carry_text) < MIN_CHUNK_CHARS:
            carry_text = f"{carry_text}\n\n{text}".strip()
            # conserva la sección del trozo que aporta el contenido real
            carry_section = section if len(text) >= len(carry_text) - len(text) else carry_section
        else:
            merged.append((carry_section, carry_text))
            carry_section, carry_text = section, text
    if merged and len(carry_text) < MIN_CHUNK_CHARS:
        prev_section, prev_text = merged.pop()
        merged.append((prev_section, f"{prev_text}\n\n{carry_text}".strip()))
    else:
        merged.append((carry_section, carry_text))
    return merged


def split_documents(
    docs: list[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    repository: str | None = None,
    tech_stack: str | None = None,
) -> list[Document]:
    """Divide los documentos en chunks con metadatos completos.

    Cada chunk incluye un chunk_id determinista (metadata['chunk_id']) y el
    texto llega prefijado con "[Sección] " para dar contexto al embedding.
    """
    if chunk_size is not None and chunk_overlap is not None:
        size, overlap = chunk_size, chunk_overlap
        if overlap >= size:
            raise ValueError("chunk_overlap debe ser menor que chunk_size")
    else:
        default_size, default_overlap = get_chunk_config()
        size = chunk_size if chunk_size is not None else default_size
        overlap = chunk_overlap if chunk_overlap is not None else default_overlap

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
        raw_pieces = [(s, t.strip()) for s, t in splitter(doc, size, overlap) if t.strip()]
        pieces = _merge_short_pieces(raw_pieces)

        for index, (section, text) in enumerate(pieces):
            prefixed = text if text.startswith(f"[{section}]") else f"[{section}] {text}"
            metadata = build_metadata(source, section, repo, tech, page)
            metadata["chunk_id"] = make_chunk_id(source, page, index, text)
            chunks.append(Document(page_content=prefixed, metadata=metadata))
    return chunks
