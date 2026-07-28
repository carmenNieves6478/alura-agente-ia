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
            models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
            errors = []
            for model_name in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.2,
                        )
                    )
                    return response.text
                except Exception as e:
                    errors.append(f"[{model_name}]: {e}")

            # Si falla con la API Key configurada, usar búsqueda local y mostrar la nota
            fallback_res = self._local_fallback_answer(question)
            return f"❌ **Error al autenticar en Google Gemini API**:\n{errors[0]}\n\n---\n{fallback_res}"

        # Si no hay API Key configurada todavía, proveer una búsqueda basada en coincidencia directa de contexto / fallback
        return self._local_fallback_answer(question)

    def _local_fallback_answer(self, question: str) -> str:
        """
        Método de respaldo local en caso de no contar aún con API Key configurada.
        """
        q_words = [w.lower().strip("?,.¿¡") for w in question.split() if len(w) > 2]
        matches = []
        
        for doc in self.loader.load_all_documents():
            for line in doc["content"].splitlines():
                if line.strip() and any(w in line.lower() for w in q_words if w not in ["que", "para", "como", "usan", "cual", "donde"]):
                    matches.append(f"• [{doc['filename']}] {line.strip()}")

        if matches:
            snippet = "\n".join(matches[:10])
        else:
            snippet = "Se encontraron documentos cargados pero no hubo coincidencia directa de términos en el texto."

        return (
            "⚠️ **Modo Local (Sin GEMINI_API_KEY)**\n\n"
            "Información relevante extraída directamente de los documentos:\n\n"
            f"{snippet}\n\n"
            "💡 *Para obtener respuestas completas con Inteligencia Artificial y lenguaje natural, ingresa tu `GEMINI_API_KEY` en `.env` o en la app web.*"
        )
