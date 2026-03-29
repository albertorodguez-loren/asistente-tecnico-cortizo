import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# =================================================================
# CONFIGURACIÓN DE LA INTERFAZ (UI)
# =================================================================
st.set_page_config(page_title="Asistente Cortizo Cloud", page_icon="favicon.png")

# Mostramos el logo centrado y con un ancho que se vea bien (ajusta el width si quieres)
st.image("GetPrefWebHeaderLogo.png", width=350) 

st.title("Asistente Técnico Cortizo Cloud")
st.markdown("---") # Una línea divisoria para dar elegancia
st.markdown("""
Esta herramienta utiliza Inteligencia Artificial para resolver dudas técnicas 
basándose exclusivamente en los manuales oficiales de la plataforma.
""")

# Configuración de la página
#st.set_page_config(page_title="Asistente Cortizo Cloud", page_icon="🤖")
st.set_page_config(page_title="Asistente Cortizo Cloud", page_icon="logo_cortizo_favicon.png") # Sube el logo a tu GitHub
st.title("🤖 Asistente Técnico Cortizo Cloud")

# --- LÓGICA DE IA ---
# Por seguridad, la API KEY no se escribe aquí; se gestiona desde el panel de Secrets de la nube.
api_key_segura = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key_segura)
model = genai.GenerativeModel('gemini-2.5-flash') 

# Usamos @st.cache_resource para que los PDFs solo se lean una vez al arrancar, ahorrando memoria.
@st.cache_resource
def cargar_manuales():
    texto_total = ""  
    for archivo in os.listdir("manuales"):
        if archivo.endswith(".pdf"):
            with open(f"manuales/{archivo}", "rb") as f:
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
