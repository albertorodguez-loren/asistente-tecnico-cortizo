import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# Configuración de la página
st.set_page_config(page_title="Asistente Cortizo Cloud", page_icon="🤖")
st.title("🤖 Asistente Técnico Cortizo Cloud")

# --- LÓGICA DE IA ---
# Cambiamos la clave fija por una variable de sistema segura
api_key_segura = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key_segura)
model = genai.GenerativeModel('gemini-2.5-flash') 

@st.cache_resource
def cargar_manuales():
    """
    Lee todos los PDFs de la carpeta 'manuales' y extrae el texto.
    Usamos cache_resource para que solo se ejecute una vez y la web vaya rápida.
    """
    texto_total = ""  
    carpeta_objetivo = "manuales" 
    
    # Verificamos que la carpeta existe para evitar que la app de error
    if os.path.exists(carpeta_objetivo):
        for archivo in os.listdir(carpeta_objetivo):
            if archivo.endswith(".pdf"):
                # Unimos la ruta de la carpeta con el nombre del archivo
                ruta_completa = os.path.join(carpeta_objetivo, archivo)
                with open(ruta_completa, "rb") as f:
                    lector = PyPDF2.PdfReader(f)
                    for pagina in lector.pages:
                        texto_total += pagina.extract_text() + "\n"
    return texto_total

conocimiento = cargar_manuales()

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat = model.start_chat(history=[])

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("¿En qué puedo ayudarte con Cortizo Cloud?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta de la IA
    with st.chat_message("assistant"):
        contexto_instruccion = f"Eres un experto en Cortizo Cloud. Usa este manual: {conocimiento}. Responde a: {prompt}"
        response = st.session_state.chat.send_message(contexto_instruccion)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
