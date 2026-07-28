import os
import streamlit as st
from src.agent import AluraAgent
from src.config import DATA_DIR, GEMINI_API_KEY

# Configuración de página de Streamlit
st.set_page_config(
    page_title="NexusMind AI - Asistente de Documentación",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado CSS en tonos celestes / cian (Sky Blue & Cyan Theme)
st.markdown("""
    <style>
    /* Fondo principal y fuentes */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Header principal */
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0284C7 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.8rem;
    }
    
    /* Sidebar personalizado */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F0F9FF 0%, #E0F2FE 100%);
        border-right: 1px solid #BAE6FD;
    }
    
    /* Tarjetas de mensajes */
    .stChatMessage {
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(14, 165, 233, 0.05);
    }
    
    /* Botones de sugerencias */
    .stButton>button {
        background: linear-gradient(135deg, #38BDF8 0%, #0284C7 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Título y Marca de la Aplicación
st.markdown("<div class='main-header'>⚡ NexusMind AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Asistente de Inteligencia Artificial para consulta de documentos empresariales (SaaS & Plataforma Digital).</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Cargar logo celeste personalizado
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=160)
    elif os.path.exists("assets/logo.jpg"):
        st.image("assets/logo.jpg", width=160)
    else:
        st.image("https://img.icons8.com/isometric-folders/100/bot.png", width=70)
        
    st.title("⚙️ Configuración")

    # API Key Input
    user_api_key = st.text_input(
        "Clave API de Google Gemini:",
        type="password",
        value=st.session_state.get("api_key", GEMINI_API_KEY or ""),
        help="Obtén tu clave gratuita en Google AI Studio"
    )
    if user_api_key:
        st.session_state["api_key"] = user_api_key

    st.divider()

    # Documentos Cargados
    st.subheader("📚 Base de Conocimiento")

    # Instanciar el agente
    agent = AluraAgent(api_key=st.session_state.get("api_key", ""), data_dir=DATA_DIR)
    docs_summary = agent.get_loaded_documents_summary()

    if docs_summary:
        for doc in docs_summary:
            st.markdown(f"📄 **{doc['filename']}** ({doc['length']} chars)")
    else:
        st.warning("No hay documentos en la carpeta `data/`.")

    st.divider()

    # Cargar nuevo archivo
    st.subheader("📤 Subir Documento")
    uploaded_file = st.file_uploader("Añadir PDF, CSV, MD o TXT", type=["pdf", "csv", "md", "txt"])
    if uploaded_file is not None:
        os.makedirs(DATA_DIR, exist_ok=True)
        save_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"¡Archivo '{uploaded_file.name}' cargado! Recargando...")
        st.rerun()

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "¡Hola! Soy **NexusMind AI**, tu asistente inteligente para la plataforma NexusSaaS. Puedo resolver preguntas sobre arquitectura técnica, planes de precios, políticas de privacidad, SLA y soporte. ¿En qué te ayudo hoy?"
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

# Capturar entrada del usuario
prompt = st.chat_input("Escribe tu pregunta sobre los documentos...") or selected_question

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando la base de conocimiento y generando respuesta..."):
            response = agent.answer_question(prompt)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
