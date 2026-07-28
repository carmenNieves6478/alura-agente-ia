import os
import streamlit as st
from src.agent import AluraAgent
from src.config import DATA_DIR, GEMINI_API_KEY

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Alura Agente - Asistente de Documentación IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        border-radius: 10px;
    }
    .doc-badge {
        background-color: #E2E8F0;
        color: #1E293B;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-right: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Título de la aplicación
st.markdown("<div class='main-header'>🤖 Alura Agente - Asistente IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Respuestas instantáneas en lenguaje natural basadas en tus documentos empresariales (SaaS / Plataforma Digital).</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/bot.png", width=70)
    st.title("⚙️ Configuración")

    # API Key Input
    user_api_key = st.text_input(
        "Clave API de Google Gemini:",
        type="password",
        value=st.session_state.get("api_key", GEMINI_API_KEY or ""),
        help="Obtén tu clave gratuita en Google AI Studio (https://aistudio.google.com/)"
    )
    if user_api_key:
        st.session_state["api_key"] = user_api_key

    st.divider()

    # Documentos Cargados
    st.subheader("📚 Documentos en la Base de Conocimiento")

    # Instanciar el agente
    agent = AluraAgent(api_key=st.session_state.get("api_key", ""), data_dir=DATA_DIR)
    docs_summary = agent.get_loaded_documents_summary()

    if docs_summary:
        for doc in docs_summary:
            st.markdown(f"📄 **{doc['filename']}** ({doc['length']} caracteres)")
    else:
        st.warning("No hay documentos en la carpeta `data/`.")

    st.divider()

    # Cargar nuevo archivo
    st.subheader("📤 Subir Nuevo Documento")
    uploaded_file = st.file_uploader("Añadir PDF, CSV o MD", type=["pdf", "csv", "md", "txt"])
    if uploaded_file is not None:
        os.makedirs(DATA_DIR, exist_ok=True)
        save_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"¡Archivo '{uploaded_file.name}' guardado con éxito! Recargando...")
        st.rerun()

# Inicializar historial de chat en session_state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "¡Hola! Soy **Alura Agente**, tu asistente virtual para la plataforma NexusSaaS. Puedes preguntarme sobre la arquitectura del producto, tarifas, SLA, políticas de privacidad o respuestas de soporte. ¿En qué puedo ayudarte hoy?"
        }
    ]

# Sugerencias rápidas de preguntas
st.markdown("##### 💡 Preguntas sugeridas:")
col1, col2, col3, col4 = st.columns(4)

selected_question = None
with col1:
    if st.button("💻 Stack Backend"):
        selected_question = "¿Qué lenguajes de programación se usan en el backend?"
with col2:
    if st.button("💰 Precios y Planes"):
        selected_question = "¿Cuáles son los planes de precios y límites de la API?"
with col3:
    if st.button("🔒 Cifrado de Datos"):
        selected_question = "¿Cómo se cifran y protegen los datos en OCI?"
with col4:
    if st.button("⏱️ SLA Enterprise"):
        selected_question = "¿Cuál es el tiempo de respuesta y SLA para el plan Enterprise?"

# Renderizar historial de chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Capturar entrada del usuario (vía chat input o botón sugerido)
prompt = st.chat_input("Escribe tu pregunta sobre los documentos...") or selected_question

if prompt:
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta con el agente
    with st.chat_message("assistant"):
        with st.spinner("Buscando en la base de conocimiento y generando respuesta..."):
            response = agent.answer_question(prompt)
            st.markdown(response)

    # Guardar en historial
    st.session_state.messages.append({"role": "assistant", "content": response})
