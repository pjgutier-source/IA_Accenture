import json
import time
from collections import Counter
from google import genai
from google.genai import types

# Dataset de tuning adaptado a tu proyecto: Planificación y desarrollo de pruebas en terreno (Perforación / Bits y Martillos).
# Entrada en lenguaje natural -> JSON estructurado con (tipo_operacion, prioridad).
ejemplos_raw = [
    (
        "Tenemos que probar 4 bits de durabilidad media con avance de 120 metros diarios, ¿cuántos días nos toma la prueba?",
        {"tipo_operacion": "calculo_dias_prueba", "prioridad": "alta"},
    ),
    (
        "Si usamos bits de durabilidad poco y avanzamos a 60 m al día con 3 bits, ¿cuántos días de terreno necesitamos?",
        {"tipo_operacion": "calculo_dias_prueba", "prioridad": "alta"},
    ),
    (
        "¿Cuántos días durará la campaña de prueba si enviamos 6 bits de durabilidad mucho a 250 metros por día?",
        {"tipo_operacion": "calculo_dias_prueba", "prioridad": "media"},
    ),
    (
        "El martillo tiene una vida útil de 4000 metros antes de darlo de baja y los bits duran medio, ¿cuántos bits se consumen?",
        {"tipo_operacion": "calculo_bits_martillo", "prioridad": "alta"},
    ),
    (
        "Para un martillo nuevo de 6000 m con bits de baja durabilidad (poco), ¿cuántos bits tenemos que despachar?",
        {"tipo_operacion": "calculo_bits_martillo", "prioridad": "alta"},
    ),
    (
        "Necesito calcular cuántos bits de durabilidad mucho entran en un martillo de 2000 metros.",
        {"tipo_operacion": "calculo_bits_martillo", "prioridad": "media"},
    ),
    (
        "¿Cuáles son los metros de durabilidad de referencia para los bits poco, medio y mucho?",
        {"tipo_operacion": "consulta_especificaciones", "prioridad": "baja"},
    ),
    (
        "¿Cuál es el rendimiento estándar recomendado en metros diarios para roca de abrasividad media?",
        {"tipo_operacion": "consulta_especificaciones", "prioridad": "baja"},
    ),
    (
        "Se detectó desgaste prematuro en el vástago del martillo en la prueba de hoy, ¿qué EPP y protocolo de detención aplica?",
        {"tipo_operacion": "seguridad_terreno", "prioridad": "alta"},
    ),
    (
        "¿Qué checklist de inspección previa a la salida a terreno debemos completar para la cuadrilla de sondaje?",
        {"tipo_operacion": "seguridad_terreno", "prioridad": "media"},
    ),
]

examples = [
    types.TuningExample(text_input=texto, output=json.dumps(salida, ensure_ascii=False))
    for texto, salida in ejemplos_raw
]


def chequear_balance(ejemplos_raw: list[tuple[str, dict]], clave: str) -> Counter:
    categorias = Counter(salida[clave] for _, salida in ejemplos_raw)
    return categorias


def validar_dataset(
    examples: list[types.TuningExample], claves_esperadas: tuple[str, ...]
) -> list[str]:
    problemas = []
    vistos = set()
    for i, ej in enumerate(examples):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ej.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ej.text_input)
        try:
            salida = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')
    return problemas


def esperar_a_que_termine(
    client: genai.Client, nombre_trabajo: str, intervalo_segundos: int = 30
) -> types.TuningJob:
    estados_finales = {
        types.JobState.JOB_STATE_SUCCEEDED,
        types.JobState.JOB_STATE_FAILED,
        types.JobState.JOB_STATE_CANCELLED,
        types.JobState.JOB_STATE_PARTIALLY_SUCCEEDED,
    }
    while True:
        trabajo = client.tunings.get(name=nombre_trabajo)
        print(f"estado actual: {trabajo.state}")
        if trabajo.state in estados_finales:
            return trabajo
        time.sleep(intervalo_segundos)


if __name__ == "__main__":
    print(f"{len(examples)} ejemplos construidos")
    print(examples[0])

    balance_operacion = chequear_balance(ejemplos_raw, "tipo_operacion")
    for cat, cuenta in balance_operacion.most_common():
        print(f"{cat}: {cuenta}")

    problemas = validar_dataset(
        examples, claves_esperadas=("tipo_operacion", "prioridad")
    )
    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
    for p in problemas:
        print(" -", p)
