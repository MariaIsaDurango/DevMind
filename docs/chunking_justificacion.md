# Justificación de la estrategia de chunking

## Naturaleza de los documentos
Documentación técnica: guías de despliegue, referencias de API y runbooks de infraestructura. Están escritos en Markdown, con encabezados que separan temas, bloques de código (comandos que no deben partirse) y listas de pasos. Cada sección suele responder a una pregunta concreta ("¿cómo despliego a staging?").

## Estrategia (implementada en `src/ingestion/chunking.py`)
1. **Se divide primero por encabezados** (`#` a `####`). Cada chunk pertenece a una sola sección, y esa sección se guarda en el metadato `section` (trazabilidad). Así un chunk nunca mezcla, por ejemplo, staging con producción.
2. **Después se divide por tamaño** con `RecursiveCharacterTextSplitter` en modo Markdown, cuyos separadores respetan párrafos y bloques de código antes de cortar en mitad de una frase.
3. Para `.txt` y `.pdf` (sin encabezados fiables) se usa el mismo splitter recursivo (párrafo → línea → frase → palabra). En PDF se conserva el número de página en `page`.

## Parámetros
| Parámetro | Valor | Justificación |
|---|---|---|
| `chunk_size` | 800 caracteres (~200 tokens) | Cabe un procedimiento completo (título + comando + explicación). Si es más grande, el embedding mezcla temas y baja la precisión; si es más pequeño, se separan los comandos de su explicación. |
| `chunk_overlap` | 120 caracteres (15 %) | Solo actúa cuando una sección larga se parte por tamaño: evita perder el contexto de un paso que cruza el límite entre dos chunks. Se mantiene bajo para no duplicar demasiado texto en el índice. |

Los valores se leen de `CHUNK_SIZE` y `CHUNK_OVERLAP` (`.env`), así se pueden ajustar sin tocar el código.

## Resultado con el dataset de ejemplo
Con los 3 documentos de `data/raw` (documentos cortos) se generan 13 chunks, con una longitud media de 167 caracteres y un máximo de 386. **Los tres tamaños probados (500, 800 y 1200) dan exactamente el mismo resultado**, porque todas las secciones miden menos de 500 caracteres: la división por encabezados manda y el tamaño no llega a intervenir.

Conclusión: el `chunk_size` y el `overlap` solo se pueden validar de verdad con documentos reales más largos. Hasta entonces se mantienen los valores iniciales.

## Experimentos pendientes (Checkpoint 1)
Con documentación real, ejecutar `python scripts/ingest.py --dry-run` con distintos valores y comparar junto con P2 la calidad del retrieval:

| Prueba | chunk_size | overlap | Nº de chunks | ¿El chunk correcto está en el top-k? | Conclusión |
|---|---|---|---|---|---|
| 1 | 500 | 50 | | | |
| 2 | 800 | 120 | | | |
| 3 | 1200 | 200 | | | |

## Limitaciones conocidas
- Una sección con un bloque de código muy largo puede partirse en mitad del bloque.
- Los chunks que solo contienen un título (p. ej. la cabecera con "Repositorio" y "Tecnología") tienen poco valor semántico, pero aportan los metadatos `repository` y `tech_stack`.
