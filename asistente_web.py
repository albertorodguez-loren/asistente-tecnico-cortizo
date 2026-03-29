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
    texto_total = ""  
    for archivo in os.listdir("."):
        if archivo.endswith(".pdf"):
            with open(archivo, "rb") as f:
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