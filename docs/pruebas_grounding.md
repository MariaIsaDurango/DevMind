# Batería de pruebas de grounding (anti-alucinación)

## Objetivo

Verificar que el sistema RAG:

- Utiliza el contexto recuperado por el retriever para generar la respuesta.
- Mantiene la trazabilidad de las fuentes utilizadas.
- Restringe las respuestas a la información disponible en la documentación.
- Evita inventar información cuando la respuesta no está respaldada por el contexto.

## Pruebas automatizadas

Las pruebas automatizadas de grounding se encuentran en:

`tests/test_grounding.py`

Actualmente se validan las siguientes propiedades:

| # | Prueba | Qué verifica | Resultado |
|---|---|---|---|
| 1 | Contexto recuperado enviado al LLM | El contenido recuperado por el retriever se incorpora al prompt enviado al modelo | ✅ PASS |
| 2 | Trazabilidad de fuentes | Las fuentes recuperadas se devuelven junto con la respuesta | ✅ PASS |
| 3 | Restricción al contexto | El prompt indica al LLM que debe utilizar exclusivamente la información recuperada y reconocer cuando no dispone de información suficiente | ✅ PASS |

Resultado actual de la suite:

```
32 passed
```

Comando utilizado:

```
python -m pytest -q
```
