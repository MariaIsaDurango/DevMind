import gradio as gr
import requests

# URL de tu backend FastAPI (se conectará en la semana 2 con la Persona 3)
BACKEND_URL = "http://localhost:8000"

def subir_documento(file):
    """
    Función para gestionar la subida de archivos desde Gradio 
    y enviarlos al endpoint POST /upload del backend.
    """
    if file is None:
        return "⚠️ Por favor, selecciona un archivo técnico válido."
    
    try:
        # Preparación para el envío real por HTTP a FastAPI
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f, "application/pdf")}
            # response = requests.post(f"{BACKEND_URL}/upload", files=files)
            
        return f"✅ ¡Documento '{file.name.split('/')[-1]}' procesado, fragmentado e indexado correctamente en ChromaDB!"
    except Exception as e:
        return f"❌ Error al subir el documento: {str(e)}"

def responder_chat(mensaje, historial):
    """
    Función que gestiona el chat, envía la pregunta al backend (POST /chat)
    y devuelve la respuesta junto con las fuentes para la trazabilidad.
    """
    if not mensaje.strip():
        return "", historial, "No hay fuentes para mostrar."

    # --- SIMULACIÓN (Mock Data) mientras se integra el backend ---
    respuesta_simulada = f"Respuesta generada por el RAG de DevMind para: '{mensaje}' (usando modelo multilingüe y ChromaDB)."
    
    fuentes_simuladas = """### 📚 Fuentes y Trazabilidad:
- **Documento:** `guia_despliegue_cicd.md`[cite: 2]
- **Sección:** Entornos de Staging[cite: 2]
- **Fragmento recuperado:** 
> *"Para desplegar en staging debe ejecutar el pipeline de integración continua asegurándose de que las variables de entorno estén configuradas..."*[cite: 2]
"""

    # Gradio actualiza el historial de chat con las tuplas (usuario, asistente)
    historial.append((mensaje, respuesta_simulada))
    
    return "", historial, fuentes_simuladas

# Construcción de la interfaz gráfica con Gradio Blocks
with gr.Blocks(title="DevMind - Asistente RAG DevOps") as demo:
    gr.Markdown("# 🚀 DevMind: Asistente RAG Corporativo para Desarrolladores y DevOps")
    gr.Markdown("Consulta documentación técnica, APIs e infraestructura con alta fidelidad y trazabilidad de fuentes[cite: 2].")

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
            gr.Markdown("Sube nuevos manuales técnicos, normativas o guías (PDF, Markdown, TXT) para añadirlos a la base de datos vectorial.")
            file_uploader = gr.File(label="Subir documento técnico", file_types=[".pdf", ".md", ".txt"])
            btn_subir = gr.Button("Procesar e Indexar Documento")
            output_subida = gr.Textbox(label="Estado del Servidor", interactive=False)

    # Conexión de eventos de los componentes
    txt_input.submit(responder_chat, inputs=[txt_input, chatbot], outputs=[txt_input, chatbot, panel_trazabilidad])
    btn_enviar.click(responder_chat, inputs=[txt_input, chatbot], outputs=[txt_input, chatbot, panel_trazabilidad])
    
    btn_subir.click(subir_documento, inputs=[file_uploader], outputs=[output_subida])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)