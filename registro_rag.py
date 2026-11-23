import time
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Rutas fijas para vectorstore y el output en prompts/
RUTA_RAIZ = Path(__file__).resolve().parent
RUTA_VECTORSTORE = RUTA_RAIZ / "vectorstore"
RUTA_SALIDA_JSONL = RUTA_RAIZ / "prompts" / "registros_latencia_costo.jsonl"

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def formatear_contexto(chunks_recuperados):
    lineas = []
    for i, doc in enumerate(chunks_recuperados, start=1):
        lineas.append(f"[{i}] {doc.page_content}")
    return "\n\n".join(lineas)


@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def registrar_consulta(pregunta, persist_directory=str(RUTA_VECTORSTORE), k=3):
    """Corre una consulta RAG real, midiendo tiempo por etapa y tokens reales
    de la respuesta del modelo."""
    tiempos = {}

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # Usamos gemini-3.5-flash-lite (o gemini-3.8-flash) disponible en tu cuenta
    chat_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

    with medir(tiempos, "embed_y_busqueda"):
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        chunks = retriever.invoke(pregunta)

    contexto = formatear_contexto(chunks)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(prompt)

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": dict(respuesta.usage_metadata) if respuesta.usage_metadata else None,
    }
    return registro


if __name__ == "__main__":
    pregunta_prueba = "que hace el cliente si una llamada tarda demasiado?"
    registro = registrar_consulta(
        pregunta_prueba,
        persist_directory=str(RUTA_VECTORSTORE),
    )
    print(json.dumps(registro, indent=2, ensure_ascii=False))

    # Guarda el registro en la carpeta prompts/
    with open(RUTA_SALIDA_JSONL, "a", encoding="utf-8") as f:
        f.write(json.d
        umps(registro, ensure_ascii=False) + "\n")

    print(f"\nRegistro guardado en {RUTA_SALIDA_JSONL}")
