import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import shutil
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Importamos los módulos oficiales del equipo para ingesta y vector store
from src.ingestion import process_file
from src.vectorstore.store import index_documents
from src.vectorstore.retriever import get_retriever
from src.backend.prompts import SYSTEM_PROMPT_ES, SYSTEM_PROMPT_EN

# --- CONFIGURACIÓN CENTRALIZADA PARA GROQ ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")

# Modelo exacto verificado disponible en tu cuenta de Groq
GROQ_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

if not GROQ_API_KEY:
    raise ValueError("⚠️️ No se ha encontrado la clave API de Groq en el archivo .env (revisa GROQ_API_KEY).")

# Inicializamos el cliente oficial de Groq
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Carpeta de destino para archivos subidos desde la UI
RAW_DATA_DIR = os.path.join("data", "raw")


def initialize_index(data_dirs: list = ["data/raw", "docs"]):
    """
    Procesa los documentos de múltiples carpetas (data/raw y docs) usando el módulo de ingesta,
    ignorando archivos ocultos como .gitkeep e indexando los chunks en ChromaDB.
    """
    all_docs = []

    for directory in data_dirs:
        if not os.path.exists(directory):
            print(f"⚠️ Advertencia: La carpeta {directory} no existe.")
            continue

        for filename in os.listdir(directory):
            # Ignoramos archivos ocultos como .gitkeep
            if filename.startswith(".") or filename == "pruebas_grounding.md":
                continue

            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    docs = process_file(file_path)
                    all_docs.extend(docs)
                except Exception as e:
                    print(f"Error procesando {filename} en {directory}: {e}")

    if all_docs:
        indexed_count = index_documents(all_docs)
        print(f"✅ Indexados {indexed_count} chunks correctamente desde {data_dirs} en ChromaDB.")
    else:
        print("⚠️ No se encontraron documentos válidos para indexar.")
    
    return get_retriever(k=4)


def query_rag(prompt: str, retriever=None, index=None, language="es"):
    """
    Ejecuta una consulta usando el retriever del equipo y genera
    la respuesta consultando a la API de Groq.
    """
    if retriever is None:
        retriever = get_retriever(k=4)

    source_documents = retriever.invoke(prompt)

    source_nodes = []
    context_text = ""

    for doc in source_documents:
        source_info = {
            "file_path": doc.metadata.get("source", "Desconocido"),
            "score": doc.metadata.get("score", 0.0),
            "text": doc.page_content,
        }
        source_nodes.append(source_info)
        context_text += f"\n---\n{doc.page_content}\n"

    if not client:
        return "⚠️ Error: Cliente de Groq no inicializado (falta la clave API).", source_nodes

    if language == "en":
        prompt_template = SYSTEM_PROMPT_EN
    else:
        prompt_template = SYSTEM_PROMPT_ES

    system_prompt = prompt_template.format(
        context_str=context_text,
        query_str=prompt,
    )

    try:
        chat_completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        respuesta_real = chat_completion.choices[0].message.content
    except Exception as e:
        respuesta_real = f"❌ Error al consultar la API de Groq: {str(e)}"

    return respuesta_real, source_nodes


def handle_file_upload(file_obj):
    """
    Recibe el archivo subido desde la interfaz, lo guarda permanentemente
    en la carpeta data/raw/ e indexa su contenido en ChromaDB.
    """
    if file_obj is None:
        return "⚠️ Por favor, selecciona un archivo primero."

    try:
        # 1. Asegurar que la carpeta data/raw existe
        os.makedirs(RAW_DATA_DIR, exist_ok=True)

        # 2. Copiar el archivo desde la carpeta temporal de Gradio a data/raw/
        filename = os.path.basename(file_obj.name)
        destination_path = os.path.join(RAW_DATA_DIR, filename)
        
        shutil.copy(file_obj.name, destination_path)

        # 3. Procesar e indexar en ChromaDB el nuevo archivo desde data/raw/
        docs = process_file(destination_path)
        if docs:
            indexed_count = index_documents(docs)
            return f"✅ Archivo '{filename}' guardado en 'data/raw/' e indexado ({indexed_count} fragmentos)."
        else:
            return f"⚠️ Se guardó '{filename}' en 'data/raw/', pero no se pudo extraer texto legible."

    except Exception as e:
        return f"❌ Error procesando el archivo: {str(e)}"