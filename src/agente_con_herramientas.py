import math
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=api_key)

@tool
def calcular_dias_prueba_bits(
    cantidad_bits: int,
    durabilidad_bit: str,
    rendimiento_diario_m: int = 120,
) -> str:
    """Calcula cuántos días tomará probar una cantidad de bits de perforación en terreno.
    Usar cuando el usuario pregunte por plazos, días de prueba, cronograma o duración
    a partir de la cantidad de bits, su durabilidad (poco: 200m, medio: 600m, mucho: 2000m) y avance diario en metros."""
    durabilidades = {
        "poco": 200,
        "medio": 600,
        "mucho": 1000,
    }
    dur_normalizada = durabilidad_bit.lower().strip()
    metros_por_bit = durabilidades.get(dur_normalizada, 600)
    
    metros_totales = cantidad_bits * metros_por_bit
    rendimiento = max(1, rendimiento_diario_m)
    dias = math.ceil(metros_totales / rendimiento)

    return (
        f"Planificación de días de prueba:\n"
        f"- Cantidad de bits: {cantidad_bits}\n"
        f"- Durabilidad por bit: {metros_por_bit} m ({dur_normalizada})\n"
        f"- Metros totales a perforar: {metros_totales} m\n"
        f"- Rendimiento diario: {rendimiento} m/día\n"
        f"- Días estimados de prueba: {dias} día(s)"
    )

@tool
def calcular_bits_por_martillo(
    vida_util_martillo_m: int,
    durabilidad_bit: str,
) -> str:
    """Calcula cuántos bits se consumen o necesitan durante la vida útil de un martillo de perforación hasta darle de baja.
    Usar exclusivamente cuando el usuario pregunte cuántos bits necesita un martillo, o la relación entre la vida del martillo
    (que dura 2000 m, 4000 m o 6000 m) y la durabilidad del bit (poco: 200m, medio: 600m, mucho: 1000m)."""
    durabilidades = {
        "poco": 200,
        "medio": 600,
        "mucho": 1000,
    }
    dur_normalizada = durabilidad_bit.lower().strip()
    metros_bit = durabilidades.get(dur_normalizada, 600)

    bits_necesarios = math.ceil(vida_util_martillo_m / metros_bit)

    return (
        f"Cálculo de bits por ciclo de vida de martillo:\n"
        f"- Vida útil del martillo: {vida_util_martillo_m} m hasta darlo de baja\n"
        f"- Durabilidad de cada bit: {metros_bit} m ({dur_normalizada})\n"
        f"- Total de bits necesarios por martillo: {bits_necesarios} bit(s)"
    )

herramientas = [calcular_dias_prueba_bits, calcular_bits_por_martillo]

prompt_sistema = (
    "Eres un asistente técnico de operaciones y planificación de perforación en terreno. "
    "Responde a las solicitudes usando las herramientas disponibles para: "
    "1) Calcular los días estimados de prueba según la cantidad de bits, su durabilidad y el rendimiento diario. "
    "2) Calcular cuántos bits se necesitan a lo largo de la vida útil de un martillo (2000, 4000 o 6000 metros) antes de darlo de baja."
)

agente = create_agent(
    model=modelo,
    tools=herramientas,
    system_prompt=prompt_sistema,
)

if __name__ == "__main__":
    print("=== PRUEBA 1: Calcular bits necesarios por martillo ===")
    res1 = agente.invoke(
        {"messages": [{"role": "user", "content": "Tenemos un martillo que dura 4000 metros antes de darlo de baja y usamos bits de durabilidad medio. ¿Cuántos bits vamos a necesitar para ese martillo?"}]}
    )
    for msg in res1["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"-> Herramienta elegida: {tc['name']}")
                print(f"-> Argumentos enviados: {tc['args']}")
    print("Respuesta final:\n", res1["messages"][-1].content)

    print("\n" + "=" * 50 + "\n")

    print("=== PRUEBA 2: Calcular días de prueba en terreno ===")
    res2 = agente.invoke(
        {"messages": [{"role": "user", "content": "Vamos a probar 5 bits de durabilidad poco avanzando a 60 metros por día. ¿Cuántos días dura la prueba?"}]}
    )
    for msg in res2["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"-> Herramienta elegida: {tc['name']}")
                print(f"-> Argumentos enviados: {tc['args']}")
    print("Respuesta final:\n", res2["messages"][-1].content)
