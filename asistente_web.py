import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# =================================================================
# CONFIGURACIÓN DE LA INTERFAZ (UI)
# =================================================================
st.set_page_config(page_title="Asistente Cortizo Cloud", page_icon="🤖")
st.title("🤖 Asistente Técnico Cortizo Cloud")
st.markdown("""
Esta herramienta utiliza Inteligencia Artificial para resolver dudas técnicas 
basándose exclusivamente en los manuales oficiales de la plataforma.
""")

# =================================================================
# LÓGICA DE INTELIGENCIA ARTIFICIAL Y SEGURIDAD
# =================================================================

# Recuperamos la API Key de los 'Secrets' de Streamlit para no exponerla en el código
try:
    api_key_segura = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key_segura)
except Exception:
    st.error("Error: No se encontró la API Key en los Secrets de la aplicación.")

# Definimos el modelo Gemini (Versión 2.5 Flash por su velocidad y precisión)
model = genai.GenerativeModel('gemini-2.5-flash') 

@st.cache_resource
def cargar_manuales():
    """
    Función optimizada para leer la base de conocimientos.
    Extrae el texto de todos los PDFs dentro de la carpeta 'manuales'.
    """
    texto_total = ""  
    carpeta_manuales = "manuales" 
    
    if os.path.exists(carpeta_manuales):
        for archivo in os.listdir(carpeta_manuales):
            if archivo.endswith(".pdf"):
                ruta_completa = os.path.join(carpeta_manuales, archivo)
                with open(ruta_completa, "rb") as f:
                    lector = PyPDF2.PdfReader(f)
                    for pagina in lector.pages:
                        # Unimos el contenido de todas las páginas en una sola variable
                        texto_total += pagina.extract_text() + "\n"
    else:
        st.warning(f"Aviso: No se encontró la carpeta '{carpeta_manuales}'.")
        
    return texto_total

# Cargamos el conocimiento (Gracias a @st.cache_resource solo se hace una vez)
conocimiento = cargar_manuales()

# =================================================================
# GESTIÓN DEL CHAT Y MEMORIA (SESSION STATE)
# =================================================================

# Inicializamos el historial si es la primera vez que se abre la app
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # --- CONFIGURACIÓN DE MEMORIA RAG ---
    # Iniciamos el chat y le damos el manual de golpe como instrucción de sistema
    # Esto permite que la IA "sepa" el manual antes de empezar y mantenga el hilo
    st.session_state.chat = model.start_chat(history=[])
    instruccion_maestra = (
        f"Eres un experto técnico en Cortizo Cloud. "
        f"Tu única fuente de verdad es este manual: {conocimiento}. "
        f"Si te preguntan algo que no está en el manual, dilo amablemente. "
        f"Mantén el contexto de la conversación anterior."
    )
    # Enviamos la instrucción inicial de forma silenciosa
    st.session_state.chat.send_message(instruccion_maestra)

# Dibujamos en pantalla los mensajes que ya existen en la memoria
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =================================================================
# INTERACCIÓN CON EL USUARIO
# =================================================================

if prompt := st.chat_input("¿En qué puedo ayudarte con Cortizo Cloud?"):
    # Guardamos y mostramos la pregunta del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generamos la respuesta técnica
    with st.chat_message("assistant"):
        # Enviamos SOLO la pregunta. La IA ya tiene el manual en su memoria de chat.
        response = st.session_state.chat.send_message(prompt)
        
        # Mostramos y guardamos la respuesta
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
