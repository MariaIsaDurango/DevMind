# DevMind

Sistema RAG para documentación técnica de desarrollo y DevOps.

## Puesta en marcha

Desde PowerShell, en la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` es local y no debe subirse a Git. La base Chroma se crea automáticamente en `data/processed/chroma`.

## Validación

```powershell
python scripts\ingest.py --dry-run
python scripts\ingest.py
python -m pytest -q
```

La indexación inicial descarga el modelo multilingüe configurado en `EMBEDDING_MODEL`. La consulta y el retriever usan `TOP_K` y `SIMILARITY_THRESHOLD` definidos en `.env`.

## Estado actual

La ingesta, los embeddings, la indexación persistente en Chroma y la búsqueda semántica están implementados. La integración del retriever con el backend RAG queda en `src/backend/rag_chain.py`.
