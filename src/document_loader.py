import os
import pandas as pd
from pypdf import PdfReader

class DocumentLoader:
    def __init__(self, data_folder: str):
        self.data_folder = data_folder

    def load_all_documents(self) -> list[dict]:
        """
        Lee todos los documentos (.md, .txt, .csv, .pdf) en la carpeta data
        y devuelve una lista de fragmentos con metadata (archivo de origen).
        """
        documents = []
        if not os.path.exists(self.data_folder):
            return documents

        for root, _, files in os.walk(self.data_folder):
            for file in files:
                file_path = os.path.join(root, file)
                ext = file.lower().split('.')[-1]

                if ext in ['md', 'txt']:
                    content = self._read_text_file(file_path)
                    documents.append({
                        "filename": file,
                        "path": file_path,
                        "content": content
                    })
                elif ext == 'csv':
                    content = self._read_csv_file(file_path)
                    documents.append({
                        "filename": file,
                        "path": file_path,
                        "content": content
                    })
                elif ext == 'pdf':
                    content = self._read_pdf_file(file_path)
                    documents.append({
                        "filename": file,
                        "path": file_path,
                        "content": content
                    })
        return documents

    def _read_text_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[Error leyendo archivo de texto: {e}]"

    def _read_csv_file(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            try:
                return df.to_markdown(index=False)
            except Exception:
                return df.to_string(index=False)
        except Exception as e:
            return f"[Error leyendo CSV: {e}]"

    def _read_pdf_file(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"--- Página {i+1} ---\n{page_text}")
            return "\n".join(text)
        except Exception as e:
            return f"[Error leyendo PDF: {e}]"

    def get_combined_context(self) -> str:
        """
        Combina todo el contenido cargado en un solo contexto estructurado con etiquetas.
        """
        docs = self.load_all_documents()
        context_parts = []
        for doc in docs:
            context_parts.append(
                f"=========================================\n"
                f"DOCUMENTO: {doc['filename']}\n"
                f"=========================================\n"
                f"{doc['content']}\n"
            )
        return "\n\n".join(context_parts)
