import os
import streamlit as st
from src.agent import AluraAgent
from src.config import DATA_DIR, GEMINI_API_KEY

# Configuración de página de Streamlit
st.set_page_config(
    page_title="NexusMind AI - Asistente IA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado CSS: TEMA OSCURO PREMIUM CON ACENTOS CELESTE NEÓN
st.markdown("""
    <style>
    /* Fondo principal Oscuro */
    .stApp {
        background-color: #090D16 !important;
        color: #F1F5F9 !important;
    }
    
    /* Encabezados y títulos con degradado Celeste Neón */
    .main-header {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 25px rgba(0, 242, 254, 0.2);
    }
    .sub-header {
        font-size: 1.1rem;
        color: #94A3B8 !important;
        margin-bottom: 2rem;
    }

    /* Sidebar Oscuro */
    [data-testid="stSidebar"] {
        background-color: #060911 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Textos en Sidebar */
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    /* Estilo de los Chat Messages (Burbujas en Tema Oscuro) */
    .stChatMessage {
        background-color: #111827 !important;
        border: 1px solid #1E293B !important;
        border-radius: 12px !important;
        color: #F8FAFC !important;
        margin-bottom: 1rem !important;
    }
    
    .stChatMessage[data-testimonial="user"] {
        background-color: #0F172A !important;
        border: 1px solid #0284C7 !important;
    }

    /* Inputs de texto */
    .stTextInput input, .stFileUploader section {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #00F2FE !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.4) !important;
    }

    /* Botones de sugerencia con resplandor Celeste Neón */
    .stButton>button {
        background: linear-gradient(135deg, #0284C7 0%, #06B6D4 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 0 12px rgba(6, 182, 212, 0.3) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00F2FE 0%, #0284C7 100%) !important;
        border-color: #00F2FE !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.6) !important;
    }

    /* Divisores y markdown */
    hr {
        border-color: #1E293B !important;
    }
    p, li, span, h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
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

    # Estado y gestión segura de API Key
    st.subheader("🔑 Clave API de Gemini")
    
    current_key = st.session_state.get("api_key", GEMINI_API_KEY or "")
    if current_key:
        st.success("🟢 API Key Conectada (Segura)")
    else:
        st.warning("⚠️ Sin API Key (Ejecutando en Modo Local)")

    user_api_key = st.text_input(
        "Modificar o ingresar API Key:",
        type="password",
        value="",
        placeholder="Introduce nueva clave (opcional)...",
        help="En el deploy, la clave se configura de forma segura en las variables de entorno del servidor OCI."
    )
    if user_api_key:
        st.session_state["api_key"] = user_api_key
        st.rerun()

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
