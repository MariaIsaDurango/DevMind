import os
import gradio as gr

# Importamos nuestro motor RAG desde el backend
from src.backend.rag_chain import initialize_index, query_rag, handle_file_upload

# Inicializamos el índice de LlamaIndex al arrancar la app
print("🔄 Inicializando el motor RAG de LlamaIndex...")
rag_index = initialize_index(data_dirs=["data/raw",])


def responder_chat(mensaje, historial):
    """
    Función que gestiona el chat consultando el motor real y manejando el formato de mensajes de Gradio.
    """
    if not mensaje.strip():
        return "", historial, "No hay fuentes para mostrar."

    if historial is None:
        historial = []

    # --- LLAMADA AL MOTOR RAG ---
    respuesta_real, source_nodes = query_rag(mensaje, index=rag_index)
    
    # Formateamos las fuentes para el panel lateral de trazabilidad de forma segura
    if source_nodes:
        fuentes_md = "### 📚 Fuentes y Trazabilidad:\n"
        for i, fuente in enumerate(source_nodes, 1):
            # Intentamos extraer el score de varias formas posibles para que nunca falle
            score_val = 0.0
            try:
                # 1. Si es un diccionario con 'score'
                if isinstance(fuente, dict):
                    score_val = float(fuente.get('score', 0.0) or 0.0)
                # 2. Si el objeto fuente tiene un atributo score (nodo de LlamaIndex)
                elif hasattr(fuente, 'score') and fuente.score is not None:
                    score_val = float(fuente.score)
                # 3. Diccionario dentro de metadatos o similar
                elif hasattr(fuente, 'get'):
                    score_val = float(fuente.get('score', 0.0) or 0.0)
            except (ValueError, TypeError):
                score_val = 0.0
                
            # Si score_val sigue siendo 0.0 pero el objeto trae metadata, comprobamos
            archivo = fuente.get('file_path', 'Desconocido') if isinstance(fuente, dict) else getattr(fuente, 'file_path', 'Desconocido')
            texto_frag = fuente.get('text', '') if isinstance(fuente, dict) else getattr(fuente, 'text', '')

            fuentes_md += f"- **Fuente {i}** (Relevancia: {score_val:.2f}):\n"
            fuentes_md += f"  - *Archivo:* `{archivo}`\n"
            fuentes_md += f"  - *Fragmento:* \n> *\"{texto_frag[:150]}...\"*\n\n"
    else:
        fuentes_md = "### 📚 Fuentes y Trazabilidad:\n⚠ No se encontraron documentos relevantes (umbral de similitud no superado)."
    historial.append({"role": "user", "content": mensaje})
    historial.append({"role": "assistant", "content": respuesta_real})
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

            # Conexión de eventos del chat
            txt_input.submit(responder_chat, inputs=[txt_input, chatbot], outputs=[txt_input, chatbot, panel_trazabilidad])
            btn_enviar.click(responder_chat, inputs=[txt_input, chatbot], outputs=[txt_input, chatbot, panel_trazabilidad])

        # PESTAÑA 2: Ingesta / Carga de Documentos
        with gr.TabItem("📂 Gestión de Documentos (Ingesta)"):
            gr.Markdown("Sube nuevos manuales técnicos, normativas o guías (PDF, Markdown, TXT) para añadirlos al sistema.")
            file_uploader = gr.File(label="Subir documento técnico", file_types=[".pdf", ".md", ".txt"])
            btn_subir = gr.Button("Procesar e Indexar Documento")
            output_subida = gr.Textbox(label="Estado del Servidor", interactive=False)

            # Conexión del botón de subida DENTRO de la pestaña
            btn_subir.click(handle_file_upload, inputs=[file_uploader], outputs=[output_subida])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", inbrowser=True)