from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver # usamos en vez de RunnableWithMessageHistory
from langchain.agents import create_agent

import json # para grabar trazas
from pathlib import Path
from datetime import datetime, timezone
 
registro_aprobaciones = []

load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


"--- Funciones ----"

def esperar_aprobacion(mensaje: str) -> bool:
    respuesta = input(mensaje)
    return respuesta.strip().lower() == "s"
def registrar_aprobacion(
    herramienta: str,
    argumentos: dict,
    aprobado: bool,
) -> None:
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "aprobado": aprobado,
        "momento": datetime.now().isoformat(),
    })

# Sube de 'src/' a la raíz del proyecto y entra a 'prompts/'
RUTA_TRAZAS = Path(__file__).resolve().parent.parent / "prompts" / "trazas_agente.jsonl"
set
def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict,
    archivo: Path = RUTA_TRAZAS,
) -> None:
    """Guarda una interacción del agente como una línea JSON en trazas_agente.jsonl.
    Compatible tanto con resultados de AgentExecutor como de create_agent."""
    
    # Soporte para formato clásico (intermediate_steps) o moderno (messages con tool_calls)
    acciones = []
    if "intermediate_steps" in resultado:
        acciones = [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ]
    elif "messages" in resultado:
        for msg in resultado.get("messages", []):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    acciones.append({
                        "herramienta": tc.get("name"),
                        "argumentos": tc.get("args"),
                        "observacion": None,
                    })

    # Extraer texto de respuesta final
    if "output" in resultado:
        respuesta_final = resultado["output"]
    elif "messages" in resultado and resultado["messages"]:
        ultimo = resultado["messages"][-1].content
        respuesta_final = ultimo[0]["text"] if isinstance(ultimo, list) else str(ultimo)
    else:
        respuesta_final = ""

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": acciones,
        "respuesta_final": respuesta_final,
    }

    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def marcar_repeticiones_sospechosas(
    archivo: Path = RUTA_TRAZAS,
) -> None:
    """Recorre un archivo de trazas y marca las sesiones donde la misma
    herramienta se invocó varias veces seguidas."""
    try:
        with open(archivo, encoding="utf-8") as f:
            registros = [json.loads(linea) for linea in f]
    except FileNotFoundError:
        print(
            f"No se encontró '{archivo}'. Corre "
            "registrar_traza al menos una vez antes "
            "de revisar repeticiones."
        )
        return

    for registro in registros:
        herramientas = [
            a["herramienta"]
            for a in registro.get("acciones", [])
        ]

        for i in range(1, len(herramientas)):
            if herramientas[i] == herramientas[i - 1]:
                print(
                    f"Revisar: {registro['session_id']} usó "
                    f"'{herramientas[i]}' dos veces seguidas"
                )
                break

"--- Herramientas ----"

@tool
def generar_reembolso(numero_pedido: str, monto: float) -> str:
    """Genera un reembolso para un pedido. Acción irreversible:
    requiere aprobación humana antes de ejecutarse."""
    mensaje = (
        f"El agente quiere reembolsar ${monto} "
        f"para el pedido {numero_pedido}. "
        f"¿Aprobar? (s/n): "
    )
    aprobado = esperar_aprobacion(mensaje)
    registrar_aprobacion(
        herramienta="generar_reembolso",
        argumentos={"numero_pedido": numero_pedido, "monto": monto},
        aprobado=aprobado,
    )

    if not aprobado:
        return "Reembolso no aprobado por el supervisor humano."

    return f"Reembolso de ${monto} generado para el pedido {numero_pedido}."

class ArgumentosConsultaEnvio(BaseModel):
    numero_seguimiento: str = Field(
        description="Número de seguimiento del envío."
    )
    incluir_historial: bool = Field(
        default=False,
        description="Si es True, incluye el historial completo."
    )

ESTADOS = {
    "AR12345": {
        "actual": "en tránsito, llega en 2 días",
        "historial": [
            "recibido en depósito",
            "en tránsito",
        ],
    },
}

@tool(
    "consultar_estado_envio_con_historial",
    args_schema=ArgumentosConsultaEnvio,
)
def consultar_estado_envio_detallado(
    numero_seguimiento: str,
    incluir_historial: bool = False,
) -> str:
    """Consulta el estado de un envío, con la
    opción de incluir su historial completo."""
    envio = ESTADOS.get(numero_seguimiento)
    if envio is None:
        return (
            f"No se encontró un envío con el "
            f"número {numero_seguimiento}."
        )
    if not incluir_historial:
        return envio["actual"]
    historial = ", ".join(envio["historial"])
    return f"{envio['actual']} (historial: {historial})"

@tool
def buscar_en_documentacion(consulta: str) -> str:
    """Busca información relevante en la documentación interna del producto.
    Usar cuando la pregunta es sobre cómo funciona algo del sistema."""
    documentacion = {
        "reintentos": (
            "El cliente reintenta hasta 3 veces "
            "ante un TimeoutError, con espera "
            "creciente."
        ),
        "costos": (
            "El costo se calcula a partir de "
            "totalTokenCount, según la tarifa "
            "vigente."
        ),
    }
    for clave, texto in documentacion.items():
        if clave in consulta.lower():
            return texto
    return (
        "No se encontró información sobre esa "
        "consulta en la documentación."
    )

@tool
def calcular_costo_envio(
    peso_kg: float,
    distancia_km: float
) -> str:
    """Calcula el costo estimado de un envío
    según su peso y la distancia a recorrer.
    Usar cuando el usuario pregunta cuánto va a
    costar enviar algo."""
    costo = 500 + (peso_kg * 120) + (distancia_km * 3)
    return f"El costo estimado es de ${costo:.2f}"

herramientas = [consultar_estado_envio_detallado, buscar_en_documentacion, calcular_costo_envio, generar_reembolso]

prompt_sistema = (
    "Eres un asistente que responde preguntas usando las herramientas "
    "disponibles cuando las necesites."
)

checkpointer = MemorySaver()
app_agente = create_agent(
    model=modelo,
    tools=herramientas,
    system_prompt=prompt_sistema,
    checkpointer=checkpointer,  # <-- Habilita la memoria por sesión en vez de RunnableWithMessageHistory
)

if __name__ == "__main__":
    
    config = {"configurable": {"thread_id": "cliente_123"}} # identificador de sesion
    
    # Pregunta 1
    res1 = app_agente.invoke(
        {"messages": [{"role": "user", "content": "¿Cuánto es 340 más 215?"}]},
        config=config
    )
    print("Turno 1:", res1["messages"][-1].content[0]["text"]) # extraemos solo respuesta
    registrar_traza("cliente_123", "¿Cuánto es 340 más 215?", res1)
    # Pregunta 2 (el agente recuerda el cálculo anterior sin repetir los números)
    res2 = app_agente.invoke(
        {"messages": [{"role": "user", "content": "Y si le sumas 100 más a ese resultado?"}]},
        config=config
    )
    print("Turno 2:", res2["messages"][-1].content[0]["text"]) # extraemos solo respuesta
    registrar_traza("cliente_123", "Y si le sumas 100 más a ese resultado?", res2)
    # Pregunta 3
    res3 = app_agente.invoke(
        {"messages": [{"role": "user", "content": "¿Cuál es el estado del envío AR12345, con su historial?"}]},
        config=config,
    )
    print("Turno 3:", res3["messages"][-1].content[0]["text"]) # extraemos solo respuesta
    registrar_traza("cliente_123", "¿Cuál es el estado del envío AR12345, con su historial?", res3)
    # Prueba directa de la herramienta:
    res4 = generar_reembolso.invoke({"numero_pedido": "PED789", "monto": 1500.0})
    print("Turno 4:", res4)
    # Revisión de repeticiones sospechosas
    marcar_repeticiones_sospechosas()
