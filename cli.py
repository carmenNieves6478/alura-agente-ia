import sys
from src.agent import AluraAgent

def main():
    print("=" * 60)
    print("🤖 ALURA AGENTE - CONSOLA DE PRUEBAS LOCAL")
    print("=" * 60)

    agent = AluraAgent()
    summary = agent.get_loaded_documents_summary()
    print(f"\n[+] Documentos cargados ({len(summary)}):")
    for doc in summary:
        print(f"  - {doc['filename']} ({doc['length']} caracteres)")

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"\n[?] Pregunta: {question}")
        print("-" * 60)
        answer = agent.answer_question(question)
        print(f"[🤖 Respuesta]:\n{answer}")
        print("=" * 60)
    else:
        print("\nModo Interactivo. Escribe 'salir' para terminar.\n")
        while True:
            try:
                question = input("\n[?] Pregunta: ").strip()
                if question.lower() in ["salir", "exit", "quit"]:
                    break
                if not question:
                    continue
                answer = agent.answer_question(question)
                print(f"\n[🤖 Respuesta]:\n{answer}")
            except (KeyboardInterrupt, EOFError):
                break

if __name__ == "__main__":
    main()
