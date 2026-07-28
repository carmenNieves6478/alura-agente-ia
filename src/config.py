import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
