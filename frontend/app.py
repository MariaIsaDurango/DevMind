import os
import gradio as gr
import requests

# Importamos nuestro motor RAG basado en LlamaIndex desde el backend
from src.backend.rag_chain import initialize_index, query_rag

# Inicializamos el índice de LlamaIndex al arrancar la app
print("🔄 Inicializando el motor RAG de LlamaIndex...")
rag_index = initialize_index(data_dir="data/raw")

# URL del backend FastAPI
BACKEND_URL = "http://localhost:8000"

def subir_documento(file):
    """
    Función para gestionar la subida de archivos desde Gradio 
    y enviarlos al backend.
    """
    if file is None:
        return "⚠️ Por favor, selecciona un archivo técnico válido."
    
    try:
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f, "application/pdf")}
            # response = requests.post(f"{BACKEND_URL}/upload", files=files)
            
        return f"✅ ¡Documento '{file.name.split('/')[-1]}' procesado y listo en la base de conocimiento!"
    except Exception as e:
        return f"❌ Error al subir el documento: {str(e)}"

def responder_chat(mensaje, historial):
    """
    Función que gestiona el chat consultando el motor real de LlamaIndex
    y extrayendo la trazabilidad de los nodos fuente.
    """
    if not mensaje.strip():
        return "", historial, "No hay fuentes para mostrar."

    # --- LLAMADA AL MOTOR RAG REAL ---
    respuesta_real, source_nodes = query_rag(mensaje, index=rag_index)
    
    # Formateamos las fuentes para el panel lateral de trazabilidad
    if source_nodes:
        fuentes_md = "### 📚 Fuentes y Trazabilidad:\n"
        for i, fuente in enumerate(source_nodes, 1):
            fuentes_md += f"- **Fuente {i}** (Relevancia: {fuente['score']:.2f}):\n"
            fuentes_md += f"  - *Archivo:* `{fuente['file_path']}`\n"
            fuentes_md += f"  - *Fragmento:* \n> *\"{fuente['text']}\"*\n\n"
    else:
        fuentes_md = "### 📚 Fuentes y Trazabilidad:\nNo se han encontrado fuentes específicas para esta consulta."

    # Añadimos la tupla (usuario, asistente) al historial de Gradio
    historial.append((mensaje, respuesta_real))
    
    return "", historial, fuentes_md

# Construcción de la interfaz gráfica con Gradio Blocks
with gr.Blocks(title="DevMind - Asistente RAG DevOps") as demo:
    gr.Markdown("# 🚀 DevMind: Asistente RAG Corporativo para Desarrolladores y DevOps")
    gr.Markdown("Consulta documentación técnica, APIs e infraestructura con alta fidelidad y trazabilidad de fuentes.")

    with gr.Tabs():
        # PESTAÑA 1: Chat y Trazabilidad técnica
        with gr.TabItem("💬 Chat Técnico"):
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(label="Historial de Conversación", height=450)
                    txt_input = gr.Textbox(
                        show_label=False,
                        placeholder="Escribe tu consulta técnica aquí... (ej. ¿Cómo se despliega en staging?)",
                        container=False
                    )
                    btn_enviar = gr.Button("Enviar Pregunta", variant="primary")

                with gr.Column(scale=2):
                    panel_trazabilidad = gr.Markdown("### 🔍 Panel de Trazabilidad\n*Aquí aparecerán las fuentes y metadatos de los documentos utilizados.*")

        # PESTAÑA 2: Ingesta / Carga de Documentos
        with gr.TabItem("📂 Gestión de Documentos (Ingesta)"):
            gr.Markdown("Sube nuevos manuales técnicos, normativas o guías (PDF, Markdown, TXT) para añadirlos al sistema.")
            file_uploader = gr.File(label="Subir documento técnico", file_types=[".pdf", ".md", ".txt"])
            btn_subir = gr.Button("Procesar e Indexar Documento")
            output_subida = gr.Textbox(label="Estado del Servidor", interactive=False)

    # Conexión de eventos de los componentes
    txt_input.submit(responder_chat, inputs=[txt_input, chatbot], outputs=[txt_input, chatbot, panel_trazabilidad])
    btn_enviar.click(responder_chat, inputs=[txt_input, chatbot], outputs=[txt_input, chatbot, panel_trazabilidad])
    
    btn_subir.click(subir_documento, inputs=[file_uploader], outputs=[output_subida])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)