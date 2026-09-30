"""Script de ingesta por lotes.

Uso (desde la raíz del repo):
    python scripts/ingest.py --dry-run          # solo procesa y muestra estadísticas
    python scripts/ingest.py                    # procesa e indexa en ChromaDB (requiere P2)
    python scripts/ingest.py --path data/raw --show 3
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from src.ingestion import process_directory  # noqa: E402
from src.ingestion.chunking import get_chunk_config  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta de documentos para DevMind")
    parser.add_argument("--path", default=str(ROOT / "data" / "raw"), help="carpeta con documentos")
    parser.add_argument("--dry-run", action="store_true", help="no indexa, solo muestra resultados")
    parser.add_argument("--show", type=int, default=0, help="mostrar N chunks de ejemplo")
    args = parser.parse_args()

    size, overlap = get_chunk_config()
    print(f"Carpeta: {args.path}")
    print(f"Chunking: chunk_size={size}, chunk_overlap={overlap}")

    chunks = process_directory(args.path)
    if not chunks:
        print("No se encontraron documentos (.pdf, .md, .txt).")
        return

    per_file = Counter(c.metadata["source"] for c in chunks)
    lengths = [len(c.page_content) for c in chunks]
    print(f"\nTotal de chunks: {len(chunks)}")
    for name, count in per_file.items():
        print(f"  - {name}: {count} chunks")
    print(f"Longitud (caracteres): mín={min(lengths)}  media={sum(lengths)//len(lengths)}  máx={max(lengths)}")

    for i, chunk in enumerate(chunks[: args.show], start=1):
        print(f"\n--- Chunk {i} ---")
        print(chunk.metadata)
        print(chunk.page_content)

    if args.dry_run:
        print("\n[dry-run] No se indexó nada.")
        return

    try:
        from src.vectorstore.store import index_documents
    except ImportError:
        print("\nAún no existe src/vectorstore/store.py (P2). Ejecuta con --dry-run o espera a P2.")
        return

    total = index_documents(chunks)
    print(f"\nIndexados {total} chunks en la base vectorial.")


if __name__ == "__main__":
    main()
