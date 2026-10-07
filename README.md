# 🧠 DevMind — AI Technical Assistant
<p align="center"> <img src="assets/logo.png" alt="DevMind Logo" width="220"> </p>

<p align="center"> <strong>Asistente inteligente de documentación técnica basado en RAG</strong> </p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?logo=chainlink&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/ChromaDB-FF6F00?logo=database&logoColor=white" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Sentence%20Transformers-FFCC00?logo=huggingface&logoColor=black" alt="Sentence Transformers">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
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

### 🔄 Flujo general

```
Documentos
    ↓
Ingesta + Chunking
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Búsqueda semántica
    ↓
Contexto relevante
    ↓
LLM
    ↓
Respuesta + Fuentes
```

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

**Retrieval-Augmented Generation (RAG)** combina la **recuperación de información** y la **generación de texto** mediante modelos de lenguaje.

En lugar de enviar directamente una pregunta al LLM, **DevMind** primero busca información relevante en nuestra documentación:

```
Pregunta
   ↓
Retriever
   ↓
Fragmentos relevantes
   ↓
Contexto + Pregunta
   ↓
LLM
   ↓
Respuesta + Fuentes
```

Esto permite trabajar con información específica de nuestra propia documentación y generar respuestas fundamentadas en el contexto recuperado.

---

## ⚙️ Funcionamiento

### 1. 📥 Ingesta

DevMind procesa documentos en formatos como:

- `.pdf`
- `.md`
- `.txt`

Durante la ingesta se extrae el contenido, se divide en *chunks* y se generan los *embeddings* correspondientes.

### 2. 🧠 Embeddings

Cada fragmento se transforma en una representación vectorial que permite realizar búsquedas por **similitud semántica**.

### 3. 🗄️ Vector Store

Los *embeddings* se almacenan en **ChromaDB**, junto con sus metadatos para mantener la trazabilidad.

```
{ "source": "guia_despliegue.md", "section": "Entornos de Staging", "page": 1 }
```

### 4. 🔎 Retrieval

La pregunta del usuario se convierte en un *embedding* y se utiliza para recuperar los fragmentos más relevantes de la documentación.

### 5. 🤖 Generación

El **LLM** recibe la pregunta junto con el contexto recuperado y genera la respuesta basándose en la información proporcionada.

### 6. 🔗 Trazabilidad

Las respuestas incluyen información sobre las **fuentes y fragmentos utilizados**, permitiendo revisar el origen de la información y comprobar en qué documentación se basa cada respuesta.

---

## 🛡️ Grounding y prevención de alucinaciones

DevMind está diseñado para responder utilizando **únicamente la información recuperada de la documentación**.

Cuando el contexto disponible no contiene información suficiente, el sistema debe indicarlo en lugar de generar una respuesta no respaldada.

> 💡 Es preferible reconocer que no existe información suficiente antes que proporcionar una respuesta que no pueda ser respaldada por las fuentes.

---

## 🖥️ Interfaz

DevMind proporciona una **interfaz web** desde la que el usuario puede:

- Realizar consultas mediante chat.
- Interactuar con la documentación.
- Consultar las respuestas generadas.
- Revisar las fuentes recuperadas.
- Consultar los metadatos asociados.

---

## 🧰 Tecnologías utilizadas

| Tecnología | Uso en DevMind |
|---|---|
| **Python** | Lenguaje principal |
| **LangChain** | Orquestación del pipeline RAG |
| **ChromaDB** | Almacenamiento y búsqueda vectorial |
| **Sentence Transformers** | Generación de embeddings |
| **Hugging Face** | Modelos de embeddings |
| **Groq** | Proveedor del modelo de lenguaje |
| **FastAPI** | Backend y API |
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
├── data/                                 # Datos y documentos utilizados por el sistema 
│ 
├── raw/                                  # Documentos originales 
│    └── processed/                       # Documentos procesados y datos generados 
│         └── chroma/                     # Base de datos vectorial de ChromaDB 
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
python -m venv .venv 
.\.venv\Scripts\Activate.ps1
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

Una consulta típica podría ser:

> **¿Cómo se despliega el servicio en staging?**

### 🔄 Flujo de procesamiento

```
Pregunta 
   ↓ 
Embedding de la consulta
   ↓
Búsqueda semántica
   ↓
Fragmentos relevantes
   ↓ 
Contexto
   ↓
LLM
   ↓
Respuesta + Fuentes
```

### ✅ Resultado esperado

> Para desplegar el servicio en staging debe ejecutarse el pipeline correspondiente al entorno de staging.

### 📚 Fuente

- **Documento:** `guia_despliegue.md`
- **Sección:** `Entornos de Staging`

---

## 🧪 Validación

DevMind incorpora pruebas automatizadas y funcionales para validar el comportamiento del sistema RAG en los siguientes aspectos:

- **Retrieval:** relevancia de los fragmentos recuperados.
- **Grounding:** respaldo de las respuestas en el contexto recuperado.
- **Preguntas sin respuesta:** capacidad de reconocer cuándo no existe información suficiente.
- **Trazabilidad:** correspondencia entre las respuestas generadas y las fuentes utilizadas.

---

### ⚙️ Comandos de validación

Comprobar el proceso de ingesta mediante un *dry-run*:

```
python scripts\ingest.py --dry-run
```

Ejecutar la ingesta y generar los índices:

```
python scripts\ingest.py
```

Ejecutar las pruebas automatizadas:

```
python -m pytest -q
```

---

## 📌 Estado actual

Actualmente están implementados:

- **Ingesta de documentación** en PDF, Markdown y TXT.
- **Generación de embeddings** mediante el modelo configurado.
- **Indexación persistente en ChromaDB.**
- **Búsqueda semántica y recuperación de contexto**.
- **Configuración mediante variables de entorno**.
- **Tests automatizados**.

La integración del **retriever con la cadena RAG del backend** se encuentra en:

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

> ⚠️ Las respuestas generadas deben revisarse y contrastarse con las **fuentes originales** cuando sea necesario.

---