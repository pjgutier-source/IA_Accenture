from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, decilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}
Respuesta:"""

def formatear_contexto(chunks_recuperados):
    """Arma un bloque de contexto numerado para el prompt, y un mapa
    numero -> fuente para reconstruir la cita despues."""
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    contexto = "\n".join(lineas)
    return contexto, citas

def construir_prompt(pregunta, persist_directory, k=3):
    """Recupera los k chunks mas relevantes para la pregunta y arma
    el prompt dinamico con contexto numerado, listo para pasarle al modelo."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    chunks_recuperados = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks_recuperados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    return prompt, citas

if __name__ == "__main__":
    corpus = [
        "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
        "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un "
        "ValueError.",
        "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa "
        "vigente por cada 1000 tokens.",
        "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la "
        "descripcion de cada una.",
        "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa "
        "corre en menos de un segundo.",
    ]
    metadatas = [{"fuente": f"doc{i}.md"} for i in range(len(corpus))]
    ids = [f"doc{i}" for i in range(len(corpus))]

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
    chunks = splitter.create_documents(corpus, metadatas=metadatas)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=ids,
        persist_directory="vectorstore/",
    )
    print(f"Indexados {len(chunks)} chunks con metadata en vectorstore/")

    preguntas = [
        "Que hace el cliente si hay un TimeoutError?",
        "Como decide el agente que herramienta usar?",
    ]

    for p in preguntas:
        prompt, citas = construir_prompt(p, persist_directory="vectorstore/")
        print("\n" + prompt)
        print(f"citas: {citas}")
