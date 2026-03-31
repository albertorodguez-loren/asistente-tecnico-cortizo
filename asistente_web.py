import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="Asistente Cortizo Cloud", page_icon="logo_cortizo_favicon.png")

# 2. LOGO Y TÍTULO (Con verificación de archivo)
if os.path.exists("logo_cortizo.png"):
    st.image("logo_cortizo.png", width=350) 
else:
    st.warning("⚠️ Logo no encontrado en el repositorio.")

st.title("🤖 Asistente Técnico Cortizo Cloud")

# 3. LÓGICA DE IA Y SEGURIDAD
try:
    api_key_segura = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key_segura)
except:
    st.error("🔑 Error: Falta la API KEY en los Secrets de Streamlit.")

model = genai.GenerativeModel('gemini-2.5-flash') 

@st.cache_resource
def cargar_manuales():
    texto_total = ""  
    if os.path.exists("manuales"):
        for archivo in os.listdir("manuales"):
            if archivo.endswith(".pdf"):
                with open(os.path.join("manuales", archivo), "rb") as f:
                    lector = PyPDF2.PdfReader(f)
                    for pagina in lector.pages:
                        texto_total += pagina.extract_text() + "\n"
    return texto_total

conocimiento = cargar_manuales()

# 4. INICIALIZAR CHAT CON MEMORIA
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Iniciamos el chat con el manual como instrucción de sistema (Solo una vez)
    st.session_state.chat = model.start_chat(history=[])
    instruccion = f"Eres un experto en Cortizo Cloud. Usa este manual como base: {conocimiento}"
    st.session_state.chat.send_message(instruccion)

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. INPUT Y RESPUESTA
if prompt := st.chat_input("¿En qué puedo ayudarte con Cortizo Cloud?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Enviamos solo el prompt, la IA ya recuerda el manual y el historial
        response = st.session_state.chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
