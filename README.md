# 🧠 DevMind — AI Technical Assistant
<p align="center"> <img src="assets/logo.png" alt="DevMind Logo" width="220"> </p>

<p align="center"> <strong>Asistente inteligente de documentación técnica basado en RAG</strong> </p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?logo=chainlink&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/ChromaDB-FF6F00?logo=database&logoColor=white" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Sentence%20Transformers-FFCC00?logo=huggingface&logoColor=black" alt="Sentence Transformers">
  <img src="https://img.shields.io/badge/Gradio-FF7C00?logo=gradio&logoColor=white" alt="Gradio">
  <img src="https://img.shields.io/badge/Groq-F55036?logo=groq&logoColor=white" alt="Groq">
</p>

> 🧠 **DevMind** | AI Technical Assistant  
> 📚 **Propósito:** Convertir nuestra documentación técnica en conocimiento consultable mediante lenguaje natural  
> 🔎 **Tecnología:** Retrieval-Augmented Generation (RAG)  
> 🚀 **Uso:** Herramienta de apoyo y ampliación para nuestro día a día  
> 👥 **Equipo:** Squad de 5 integrantes

---

## 📌 Sobre el proyecto

**DevMind** es un asistente de documentación técnica basado en **Retrieval-Augmented Generation (RAG)**.

Permite procesar documentación, generar *embeddings*, almacenarlos en una base de datos vectorial y realizar consultas mediante lenguaje natural.

Ante una pregunta, DevMind recupera los fragmentos más relevantes de la documentación y los utiliza como contexto para generar una respuesta fundamentada, mostrando además las fuentes utilizadas.

---

## 🏗️ Arquitectura

DevMind está compuesto por varios componentes que trabajan conjuntamente para implementar el flujo **RAG (Retrieval-Augmented Generation)** de consulta y generación de respuestas.

- **Ingesta:** procesa los documentos, extrae su contenido y genera los *chunks*.
- **Embeddings:** transforma los *chunks* en representaciones vectoriales para permitir la búsqueda semántica.
- **ChromaDB:** almacena los *embeddings* junto con los metadatos necesarios para mantener la trazabilidad.
- **Retriever:** recupera los fragmentos más relevantes en función de la consulta del usuario.
- **RAG Chain:** construye el contexto a partir de los fragmentos recuperados y prepara la consulta para el LLM.
- **Groq:** proporciona el modelo de lenguaje encargado de generar la respuesta utilizando el contexto recuperado.
- **FastAPI:** proporciona la API backend y expone la lógica necesaria para interactuar con el sistema RAG.
- **Gradio:** proporciona la interfaz web para realizar consultas, visualizar respuestas, consultar fuentes y subir documentos.

---

## 🎯 Objetivo

Resolver la dificultad de encontrar información relevante dentro de grandes cantidades de documentación técnica.

**DevMind permite:**

- Consultar documentación mediante lenguaje natural.
- Realizar búsquedas semánticas.
- Recuperar información relevante de diferentes documentos.
- Generar respuestas utilizando el contexto recuperado.
- Consultar las fuentes que respaldan cada respuesta.
- Evitar respuestas no fundamentadas cuando no existe información suficiente.

---

## 🤖 ¿Qué es RAG?

**Retrieval-Augmented Generation (RAG)** combina la recuperación de información con la generación de texto mediante modelos de lenguaje.

En DevMind, la pregunta del usuario se utiliza para recuperar información relevante de la documentación almacenada. Estos fragmentos se incorporan como contexto para que el LLM genere una respuesta fundamentada en la información recuperada.

Esto permite trabajar con información específica de nuestra documentación sin depender únicamente del conocimiento previo del modelo.

---

## ⚙️ Funcionamiento

### 1. 📥 Ingesta

DevMind procesa documentos `.pdf`, `.md` y `.txt`, extrae su contenido y lo divide en *chunks*.

### 2. 🧠 Embeddings

Cada *chunk* se transforma en una representación vectorial para permitir búsquedas por similitud semántica.

### 3. 🗄️ Vector Store

Los embeddings y sus metadatos se almacenan en **ChromaDB**, permitiendo conservar la trazabilidad de cada fragmento.

### 4. 🔎 Retrieval

La consulta del usuario se transforma en un embedding y se utiliza para recuperar los fragmentos más relevantes.

### 5. 🤖 Generación

El **RAG Chain** combina la pregunta con el contexto recuperado y lo envía al LLM proporcionado por **Groq**.

### 6. 🔗 Trazabilidad

La interfaz muestra las fuentes, fragmentos y relevancia utilizados para generar cada respuesta.

---

## 🛡️ Grounding y prevención de alucinaciones

DevMind incorpora un **prompt de grounding** que instruye al LLM a responder basándose únicamente en la información recuperada de la documentación.

Cuando el contexto recuperado no contiene información suficiente, el sistema está diseñado para indicarlo en lugar de inventar información.

> 💡 El grounding reduce el riesgo de respuestas no respaldadas, pero las respuestas generadas deben contrastarse con las fuentes originales cuando la precisión sea importante.

---

## 🖥️ Interfaz

DevMind proporciona una interfaz web basada en Gradio que permite:

- Realizar consultas al asistente.
- Visualizar las respuestas generadas.
- Consultar las fuentes y fragmentos recuperados.
- Revisar los metadatos asociados a los documentos.
- Subir documentos PDF, Markdown y TXT.
- Procesar e indexar automáticamente los documentos subidos.

---

## 🧰 Tecnologías utilizadas

| Tecnología | Uso en DevMind |
|---|---|
| **Python** | Lenguaje principal |
| **LangChain** | Integración y componentes del pipeline RAG |
| **ChromaDB** | Almacenamiento y búsqueda vectorial |
| **Sentence Transformers** | Generación de embeddings |
| **Hugging Face** | Modelos de embeddings |
| **FastAPI** | Backend y API |
| **Uvicorn** | Servidor ASGI |
| **Groq** | Proveedor del modelo de lenguaje |
| **Gradio** | Interfaz web |
| **PyPDF** | Procesamiento de documentos PDF |
| **Pydantic** | Validación de datos |
| **Pytest** | Testing |
| **Git / GitHub** | Control de versiones y colaboración |

---

## 📂 Estructura del repositorio

```
DevMind/ 
├── .github/                              # Configuración y automatizaciones de GitHub 
|
├── data/                                 # Datos y documentos utilizados por el sistema  
|    ├── raw/                             # Documentos originales 
│    └── processed/                       # Documentos procesados y datos generados 
│         └── chroma/                     # Persistencia de ChromaDB generada por la aplicación
|
├── docs/                                 # Documentación técnica del proyecto 
|
├── frontend/                             # Interfaz web de usuario de DevMind 
|
├── scripts/                              # Scripts auxiliares del proyecto 
│    └── ingest.py                        # Script de ingesta e indexación de documentos 
|
├── src/                                  # Código fuente principal de la aplicación 
│    └── backend/                         # Lógica del backend y sistema RAG 
|
├── tests/                                # Pruebas automatizadas del proyecto 
|
├── .env.example                          # Plantilla de variables de entorno 
|
├── .gitignore                            # Archivos y carpetas ignorados por Git 
| 
├── README.md                             # Documentación principal del proyecto 
|
└── requirements.txt                      # Dependencias necesarias para ejecutar DevMind
```

---

## 🚀 Puesta en marcha

Desde **PowerShell**, en la raíz del repositorio:

### 1. Crear el entorno virtual

```
python -m venv .venv ..venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```
python -m pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear el archivo `.env` a partir de la plantilla:

```
Copy-Item .env.example .env
```

Configurar en `.env` las variables necesarias para el proyecto.

> ⚠️ **Importante:** `.env` es un archivo local y no debe subirse al repositorio.

La base de datos vectorial de **ChromaDB** se crea automáticamente en:

```
data/processed/chroma
```

### 4. Ejecutar la ingesta

Primero puede comprobarse el proceso mediante un **dry-run**:

```
python scripts\ingest.py --dry-run
```

Para realizar la indexación:

```
python scripts\ingest.py
```

> 💡 La primera ejecución descarga el modelo multilingüe configurado en `EMBEDDING_MODEL`.

### 5. Ejecutar las pruebas

```
python -m pytest -q
```

### 6. Ejecutar la aplicación

DevMind utiliza **FastAPI** como backend y **Gradio** como interfaz web.

#### Iniciar el backend con FastAPI

Desde la raíz del proyecto:

```
$env:PYTHONPATH="." uvicorn src.backend.api:app --reload
```

El backend estará disponible en la dirección indicada por Uvicorn.

#### Iniciar la interfaz de Gradio

En otra terminal, con el entorno virtual activado:

```
$env:PYTHONPATH="." python frontend/app.py
```

---

## ⚙️ Configuración

La configuración principal del sistema se gestiona mediante **variables de entorno** definidas en el archivo `.env`.

Entre ellas se encuentran:

- `EMBEDDING_MODEL`: modelo utilizado para generar los *embeddings*.
- `TOP_K`: número de fragmentos recuperados durante la búsqueda.
- `SIMILARITY_THRESHOLD`: umbral mínimo de similitud para considerar relevante un fragmento.

Estos parámetros afectan directamente al **proceso de recuperación** y al funcionamiento del **retriever**.

---

## 💬 Ejemplo de uso

### Pregunta

> ¿Cuántos días de vacaciones corresponden?

### DevMind

La respuesta se genera utilizando la información recuperada de la documentación disponible.

### 📚 Fuentes y trazabilidad

Para cada respuesta, DevMind muestra las fuentes recuperadas por el sistema, incluyendo:

- **Archivo de origen**
- **Relevancia del fragmento**
- **Fragmento utilizado como contexto**

En este ejemplo, la interfaz muestra **3 fuentes recuperadas**, procedentes de `Prueba.txt` y `api_usuarios.md`, junto con su nivel de relevancia y el contenido utilizado para generar la respuesta.

---

## 🧪 Validación

DevMind incorpora pruebas automatizadas para validar diferentes componentes del sistema:

- **Ingesta:** procesamiento y generación de chunks.
- **Embeddings:** configuración y reutilización del modelo.
- **Retrieval:** recuperación de fragmentos relevantes.
- **Persistencia:** almacenamiento y reapertura de ChromaDB.
- **Metadatos:** conservación de información de trazabilidad.
- **Reindexación:** actualización de chunks y eliminación de contenido obsoleto.
- **IDs de chunks:** generación de identificadores deterministas y únicos, incluidos PDFs con páginas repetidas.

La validación del flujo completo con el LLM puede realizarse mediante la interfaz de Gradio.

---

## 📌 Estado actual

Actualmente están implementados:

- Ingesta de documentos PDF, Markdown y TXT.
- Generación de embeddings multilingües.
- Indexación persistente en ChromaDB.
- Recuperación semántica mediante retriever configurable.
- Generación de respuestas mediante Groq.
- Prompt de grounding para reducir respuestas no respaldadas.
- Trazabilidad de las fuentes recuperadas.
- Subida y persistencia de documentos mediante la interfaz Gradio.
- Reindexación idempotente y eliminación de chunks obsoletos.
- Tests automatizados de ingesta, embeddings, persistencia y retrieval.

El flujo principal se orquesta desde:

```
src/backend/rag_chain.py
```

---

## 🔐 Seguridad y privacidad

No se deben introducir documentos que contengan:

- **Contraseñas.**
- **API Keys.**
- **Tokens.**
- **Credenciales.**
- **Información personal innecesaria.**
- **Información confidencial sin autorización.**

Las credenciales y variables sensibles deben mantenerse en el archivo `.env` y **nunca almacenarse directamente en el repositorio**.

> ⚠️ **Importante:** el archivo `.env` debe estar incluido en `.gitignore` para evitar que las credenciales sean subidas accidentalmente al repositorio.

Cuando se utilizan **APIs externas para el LLM**, debe tenerse en cuenta el tratamiento y la posible transferencia de la información enviada al proveedor.

Por ello, antes de utilizar información sensible o confidencial, es necesario comprobar las **políticas de privacidad, tratamiento de datos y condiciones del proveedor**.

---

## ⚠️ Limitaciones

**DevMind** es una herramienta de apoyo y **no debe considerarse una fuente única de verdad**.

La calidad de las respuestas depende, entre otros factores, de:

- **Calidad de la documentación.**
- **Estrategia de chunking.**
- **Calidad de los embeddings.**
- **Relevancia del retrieval.**
- **Calidad del contexto recuperado.**
- **Modelo de lenguaje utilizado.**

> ⚠️ **Importante:** las respuestas deben contrastarse con la **documentación original** cuando la precisión de la información sea relevante.

---

## 🔮 Futuras mejoras

Entre las posibles líneas de evolución de **DevMind** se encuentran:

- **Búsqueda híbrida:** combinación de búsqueda semántica y búsqueda por *keywords*.
- **Reranking de resultados:** mejora de la relevancia de los fragmentos recuperados.
- **Evaluación automática:** incorporación de métricas y mecanismos para evaluar la calidad de las respuestas.
- **Más formatos documentales:** soporte para nuevos tipos de documentos y fuentes de información.
- **Autenticación y permisos:** gestión de usuarios, roles y acceso a diferentes fuentes de documentación.
- **Historial de conversaciones:** almacenamiento y consulta de conversaciones anteriores.
- **Modelos locales:** utilización de modelos locales para trabajar con documentación sensible sin depender de servicios externos.
- **Observabilidad y métricas:** monitorización del sistema, rendimiento, consultas y calidad del retrieval.
- **Mejora de la interfaz:** optimización de la experiencia de usuario (UI/UX).
- **Rediseño visual:** mejora de la usabilidad, accesibilidad y aspecto general de la aplicación.

---

## 👥 Equipo

| Integrante | Área | Contacto |
|---|---|---|
| 👩‍💻 **Maria Isabel** | Data / Ingesta | @MariaIsaDurango |
| 👨‍💻 **Jose Melo** | Vector Store / Embeddings | @GregDev08 |
| 👩‍💻 **Elizabeth** | Backend / RAG | @adryeli |
| 👩‍💻 **Vanessa** | Frontend / UX | @garciaguadalupevanessa-bit |
| 👩‍💻 **Isabela** | DevOps / Documentación / Gobernanza |	@Isabela-Tellez|

---

## 📄 Disclaimer

**DevMind** ha sido desarrollado con fines **educativos** y como herramienta de apoyo para la consulta de documentación técnica.

No está destinado a tomar **decisiones críticas de forma autónoma**.

---