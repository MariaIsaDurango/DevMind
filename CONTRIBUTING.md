# Guía de colaboración

## Estrategia de ramas
```
main      ← versión estable / entrega final (solo recibe PR desde develop)
  └─ develop   ← rama de integración (aquí se une todo el trabajo)
       ├─ feature/ingesta
       ├─ feature/vectorstore
       ├─ feature/backend
       ├─ feature/frontend
       └─ docs/gobernanza
```
- Las ramas de cada integrante **nacen de `develop`** y se fusionan a `develop` mediante Pull Request.
- `main` solo se actualiza con un PR `develop → main` cuando la integración está probada (Día 9-10).
- `main` y `develop` están protegidas: no se hace commit directo.

## Ramas por integrante

| Persona | Rol | Rama |
|---|---|---|
| P1 | Ingesta y limpieza | `feature/ingesta` |
| P2 | Vector store y embeddings | `feature/vectorstore` |
| P3 | Backend y orquestación RAG | `feature/backend` |
| P4 | Frontend y UX | `feature/frontend` |
| P5 | GitOps, gobernanza y defensa | `docs/gobernanza` |

Ramas adicionales: `fix/<tema>` o `feature/<tema>-<detalle>`.

## Primeros pasos
```bash
git clone <URL_DEL_REPO>
cd DevMind
git switch develop                      # partir SIEMPRE de develop
git switch -c feature/tu-modulo
git push -u origin feature/tu-modulo
```

## Flujo diario
```bash
git switch develop && git pull origin develop   # traer cambios del equipo
git switch feature/tu-modulo
git merge develop                                # mantener tu rama al día
# ... trabajas ...
git add <archivos>
git commit -m "feat(ingesta): add PDF loader"
git push
```
Luego abre un Pull Request hacia **`develop`** en GitHub (no hacia `main`).

## Formato de commits
`tipo(módulo): descripción en imperativo`

Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
Módulos: `ingesta`, `vectorstore`, `backend`, `frontend`, `docs`, `repo`.

Ejemplos:
- `feat(vectorstore): add Chroma retriever with top-k`
- `fix(backend): return default answer when no context found`
- `docs(chunking): justify chunk size and overlap`

## Pull Requests
- Título claro y usa la plantilla del PR.
- Mínimo **1 revisión** de otro compañero antes de fusionar.
- Un PR = un cambio coherente y pequeño.
- Si cambias el contrato de interfaz, avisa a todo el equipo y actualiza `docs/arquitectura.md`.

## Reglas de oro
- Nunca subir `.env`, claves API ni datos sensibles.
- Cada módulo se prueba de forma aislada antes de integrarse.
- No editar archivos de otro módulo sin avisar a su responsable.
