# Justificación de la estrategia de chunking

## Naturaleza de los documentos
Documentación técnica: guías de despliegue, referencias de API, runbooks de infraestructura. Estructura en Markdown con encabezados, bloques de código y listas de pasos.

## Configuración inicial (a validar en el Checkpoint 1)
| Parámetro | Valor | Justificación |
|---|---|---|
| Splitter | `RecursiveCharacterTextSplitter` (separadores por encabezado, párrafo, línea) | Respeta la estructura del texto antes de cortar |
| `chunk_size` | 800 caracteres | Suficiente para un procedimiento completo sin diluir el significado del embedding |
| `chunk_overlap` | 120 (~15 %) | Evita perder contexto en pasos que cruzan el límite entre chunks |

## Cuidados específicos
- No partir bloques de código a la mitad.
- Conservar el encabezado de sección como metadato `section`.

## Experimentos
| Prueba | chunk_size | overlap | Resultado del retrieval | Conclusión |
|---|---|---|---|---|
| 1 | 500 | 50 | | |
| 2 | 800 | 120 | | |
| 3 | 1200 | 200 | | |

_Rellenar con los resultados del Retrieval Check (fin de semana 1)._
