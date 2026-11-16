from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

K = 3  # cuantos chunks recupera el retriever y cuantos evalua la funcion

# Ruta al vectorstore en la raíz y salida a la carpeta prompts/
RUTA_RAIZ = Path(__file__).resolve().parent.parent
RUTA_VECTORSTORE = RUTA_RAIZ / "vectorstore"
RUTA_SALIDA_TXT = RUTA_RAIZ / "prompts" / "resultados_evaluacion.txt"

casos_evaluacion = [
    {
        "pregunta": "que hace el cliente si una llamada tarda demasiado",
        "ids_relevantes": {"doc0"},
    },
    {
        "pregunta": "que pasa si la clave de api es invalida",
        "ids_relevantes": {"doc1"},
    },
    {
        "pregunta": "como se calcula el costo de una llamada",
        "ids_relevantes": {"doc2"},
    },
    {
        "pregunta": "como decide el agente que herramienta usar",
        "ids_relevantes": {"doc3"},
    },
]


def precision_at_k(ids_recuperados, ids_relevantes):
    """Fraccion de los ids recuperados que son relevantes (0.0 si no hay ninguno)."""
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(ids_recuperados, ids_relevantes):
    """Fraccion de los ids relevantes que se recuperaron (None si el caso no tiene ninguno)."""
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def promediar(valores):
    """Promedio que ignora los None y evita dividir por cero."""
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0


def evaluar_recuperacion(retriever, casos, k=3):
    """Corre cada caso contra el retriever real y promedia precision y recall."""
    resultados = []
    for caso in casos:
        chunks = retriever.invoke(caso["pregunta"])
        # Soporta id directo o extraído de la metadata 'docX.md'
        ids_recuperados = []
        for c in chunks[:k]:
            doc_id = getattr(c, "id", None)
            if not doc_id and hasattr(c, "metadata") and "fuente" in c.metadata:
                doc_id = c.metadata["fuente"].replace(".md", "")
            ids_recuperados.append(doc_id)

        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({"pregunta": caso["pregunta"], "precision": p, "recall": r})

    precision_promedio = promediar(x["precision"] for x in resultados)
    recall_promedio = promediar(x["recall"] for x in resultados)
    return resultados, precision_promedio, recall_promedio


if __name__ == "__main__":
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(
        persist_directory=str(RUTA_VECTORSTORE),
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": K})

    resultados, precision_promedio, recall_promedio = evaluar_recuperacion(
        retriever, casos_evaluacion, k=K
    )

    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        print(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}")
    print(f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}")

    # Paso 3: guarda el resultado en prompts/resultados_evaluacion.txt
    with open(RUTA_SALIDA_TXT, "w", encoding="utf-8") as archivo:
        archivo.write(f"Fecha: {date.today()}\n")
        archivo.write(f"Configuracion: k={K}, chunk_size=200, chunk_overlap=30\n\n")
        for r in resultados:
            recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
            archivo.write(f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}\n")
        archivo.write(
            f"\npromedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}\n"
        )
    print(f"Resultados guardados en {RUTA_SALIDA_TXT}")
