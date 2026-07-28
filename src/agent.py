import os
from src.document_loader import DocumentLoader
from src.config import DATA_DIR, GEMINI_API_KEY

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class AluraAgent:
    def __init__(self, api_key: str = None, data_dir: str = DATA_DIR):
        self.api_key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.loader = DocumentLoader(data_dir)
        self.context = self.loader.get_combined_context()
        self.client = None

        if self.api_key and HAS_GENAI:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Advertencia] Error al inicializar cliente Gemini: {e}")

    def get_loaded_documents_summary(self) -> list[dict]:
        """Devuelve una lista de archivos cargados con sus tamaños."""
        docs = self.loader.load_all_documents()
        return [{"filename": d["filename"], "length": len(d["content"])} for d in docs]

    def answer_question(self, question: str) -> str:
        """
        Responde a la pregunta del usuario utilizando la información de los documentos.
        """
        if not self.context or len(self.context.strip()) == 0:
            return "⚠️ No se encontraron documentos en la carpeta `data/`. Por favor añade archivos CSV, PDF o Markdown."

        system_instruction = (
            "Eres el asistente inteligente oficial de NexusSaaS (Alura Agente). "
            "Tu misión es responder las preguntas del usuario utilizando ÚNICAMENTE la información proporcionada "
            "en el siguiente CONTEXTO DE DOCUMENTOS INTERNOS. "
            "Si la respuesta no se encuentra expresamente en la documentación, responde cortésmente que "
            "no posees esa información en la base de datos interna actual.\n\n"
            "Reglas de respuesta:\n"
            "1. Sé claro, profesional y estructurado (utiliza viñetas o tablas cuando corresponda).\n"
            "2. Cita el documento de origen cuando menciones datos específicos (ej: 'Según la Política de Privacidad...').\n"
            "3. Responde siempre en español."
        )

        prompt = f"CONTEXTO DE DOCUMENTOS INTERNOS:\n{self.context}\n\nPREGUNTA DEL USUARIO:\n{question}"

        # Si tenemos cliente Gemini configurado
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                    )
                )
                return response.text
            except Exception as e:
                return f"❌ Error al consultar la API de Gemini: {str(e)}\n\n(Revisa tu API Key en el archivo .env o en la interfaz)."

        # Si no hay API Key configurada todavía, proveer una búsqueda basada en coincidencia directa de contexto / fallback
        return self._local_fallback_answer(question)

    def _local_fallback_answer(self, question: str) -> str:
        """
        Método de respaldo local en caso de no contar aún con API Key configurada.
        """
        q_lower = question.lower()
        matched_lines = []
        for line in self.context.splitlines():
            if any(term in line.lower() for term in q_lower.split() if len(term) > 3):
                matched_lines.append(line)

        snippet = "\n".join(matched_lines[:10]) if matched_lines else "No se encontraron coincidencias exactas."

        return (
            "⚠️ **Nota**: No se ha detectado una `GEMINI_API_KEY` válida configurada.\n\n"
            "Sin embargo, he analizado los documentos locales cargados en `data/` y este es el contenido relevante encontrado:\n\n"
            f"```text\n{snippet}\n```\n\n"
            "💡 *Para habilitar respuestas con lenguaje natural completo, agrega tu `GEMINI_API_KEY` en la barra lateral o en el archivo `.env`.*"
        )
