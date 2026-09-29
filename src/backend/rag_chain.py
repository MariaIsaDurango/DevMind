import os
from dotenv import load_dotenv

load_dotenv()

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI
# ¡Usamos el paquete oficial de HuggingFace para los embeddings locales!
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- CONFIGURACIÓN CENTRALIZADA SEGÚN EL EQUIPO ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")

if not API_KEY and LLM_PROVIDER != "ollama":
    raise ValueError("⚠️ No se ha encontrado ninguna clave API válida en el archivo .env (revisa LLM_API_KEY).")

# 1. Configuramos el LLM (para generar las respuestas del chat)
if LLM_PROVIDER == "openai":
    Settings.llm = OpenAI(model=LLM_MODEL, api_key=API_KEY)

# 2. Configuramos los EMBEDDINGS en local (Respetando el .env.example del equipo y sin gastar créditos)
# Esto lee el modelo multilingüe que vuestro equipo dejó estipulado en la plantilla
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)


def initialize_index(data_dir: str = "data/raw"):
    """
    Inicializa el índice de LlamaIndex cargando los documentos de la ruta especificada.
    """
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print(f"⚠️ Advertencia: La carpeta {data_dir} está vacía o no existe.")
        return None

    documents = SimpleDirectoryReader(data_dir).load_data()
    index = VectorStoreIndex.from_documents(documents)
    return index


def query_rag(prompt: str, index=None):
    """
    Ejecuta una consulta sobre el motor RAG de LlamaIndex asegurando la trazabilidad.
    """
    if index is None:
        return "El índice de LlamaIndex no está inicializado o no hay documentos cargados.", []

    query_engine = index.as_query_engine(response_mode="compact")
    response = query_engine.query(prompt)

    source_nodes = []
    for node in getattr(response, "source_nodes", []):
        source_info = {
            "file_path": node.node.metadata.get("file_path", "Desconocido"),
            "score": node.score,
            "text": node.node.get_text()[:200] + "..."
        }
        source_nodes.append(source_info)

    return str(response), source_nodes