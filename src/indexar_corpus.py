import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Guardamos en ruta vectorstore/ de la raíz del proyecto
RUTA_VECTORSTORE = Path(__file__).resolve().parent.parent / "vectorstore"

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

def indexar_corpus():
    load_dotenv()
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
    chunks = splitter.create_documents(corpus)

    api_key = os.getenv("GEMINI_API_KEY")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key,
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(RUTA_VECTORSTORE),
    )

    print(f"Indexados {len(chunks)} chunks en {RUTA_VECTORSTORE}")
    return vectorstore, embeddings


if __name__ == "__main__":
    # Indexamos
    _, embeddings = indexar_corpus()

    # Confirmamos persistencia en disco
    print("\n--- Verificando persistencia en disco ---")
    vectorstore_recargado = Chroma(
        persist_directory=str(RUTA_VECTORSTORE),
        embedding_function=embeddings,
    )
    total_guardado = vectorstore_recargado._collection.count()
    print(f"Documentos confirmados en disco (count): {total_guardado}")