"""Cargadores de documentos (.pdf, .md, .txt) y limpieza de texto."""
import re
from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader

from .metadata import build_metadata

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}


def clean_text(text: str) -> str:
    """Normaliza el texto sin alterar la indentación (importante en bloques de código)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+$", "", text, flags=re.M)   # espacios al final de línea
    text = re.sub(r"\n{3,}", "\n\n", text)             # máximo una línea en blanco
    return text.strip()


def _clean_pdf_text(text: str) -> str:
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)       # une palabras cortadas por guion
    return clean_text(text)


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _load_pdf(path: Path) -> list[Document]:
    reader = PdfReader(str(path))
    docs = []
    for number, page in enumerate(reader.pages, start=1):
        text = _clean_pdf_text(page.extract_text() or "")
        if text:
            docs.append(
                Document(page_content=text, metadata=build_metadata(path.name, page=number))
            )
    return docs


def load_file(path: str | Path) -> list[Document]:
    """Carga un archivo y devuelve una lista de Document (uno por página en PDF)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Extensión no soportada: '{ext}'. Permitidas: {sorted(SUPPORTED_EXTENSIONS)}"
        )
    if ext == ".pdf":
        return _load_pdf(path)

    text = clean_text(_read_text_file(path))
    if not text:
        return []
    return [Document(page_content=text, metadata=build_metadata(path.name))]
