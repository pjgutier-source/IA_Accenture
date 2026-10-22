import json
import sys
import time
from pathlib import Path

# Definir la raíz del proyecto para importar módulos desde src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src import consumir_gemini_refactorizada as cmr

# Configuración de prueba
consulta = "¿Cuál es la mejor ciudad de Chile?"
system_instruction = "Responde únicamente con 20 palabras."
response_schema = {
    "type": "OBJECT",
    "properties": {
        "rta": {"type": "STRING"},
        "poblacion": {"type": "NUMBER"},
    },
    "required": ["rta", "poblacion"],
}

# Precios reales oficiales por token (Tarifas oficiales Google AI Studio por 1M de tokens / 1.000.000)
modelos = [
    {
        "nombre": "Gemini 3.5 Flash-Lite",
        "id": "gemini-3.5-flash-lite",
        # $0.10 por 1M tokens entrada / $0.40 por 1M tokens salida
        "precio_entrada": 0.10 / 1_000_000,  # 0.00000010 USD por token
        "precio_salida": 0.40 / 1_000_000,   # 0.00000040 USD por token
    },
    {
        "nombre": "Gemini 3.1 Flash-Lite",
        "id": "gemini-3.1-flash-lite",
        # $0.25 por 1M tokens entrada / $1.50 por 1M tokens salida
        "precio_entrada": 0.25 / 1_000_000,  # 0.00000025 USD por token
        "precio_salida": 1.50 / 1_000_000,   # 0.00000150 USD por token
    },
    {
        "nombre": "Gemini 3.8 Flash",
        "id": "gemini-3.8-flash",
        # $0.75 por 1M tokens entrada / $3.75 por 1M tokens salida
        "precio_entrada": 0.75 / 1_000_000,  # 0.00000075 USD por token
        "precio_salida": 3.75 / 1_000_000,   # 0.00000375 USD por token
    },
]

NUMERO_INTENTOS = 2
resumen = []
registro = {}

print("\n")
print(f"PRUEBA DE LATENCIA Y COSTOS ({NUMERO_INTENTOS} intentos por cada modelo)")
print("\n")

for m in modelos:
    print(f"Evaluando: {m['nombre']} ({m['id']})")
    latencias = []
    ultima_respuesta = None

    url, body = cmr.armar_peticion(consulta, m["id"], system_instruction, response_schema)

    i = 0
    reintentos_fallidos = 0
    while i < NUMERO_INTENTOS and reintentos_fallidos < 3:
        inicio = time.perf_counter()
        respuesta_json = cmr.enviar_peticion(url, body)
        fin = time.perf_counter()

        # Verificar si la API devolvió un error de cuota o saturación
        if "error" in respuesta_json:
            reintentos_fallidos += 1
            error_msg = respuesta_json["error"].get("message", "Error en API")
            print(f"  Intento {i + 1} en espera ({error_msg[:45]}...). Pausando 15s (reintento {reintentos_fallidos}/3)...")
            time.sleep(15)
            continue

        duracion = fin - inicio
        latencias.append(duracion)
        ultima_respuesta = respuesta_json
        print(f"  Intento {i + 1}: {duracion:.2f} segundos")
        i += 1
        reintentos_fallidos = 0
        time.sleep(4)  # Pausa preventiva entre llamadas exitosas

    if latencias and ultima_respuesta:
        latencia_promedio = sum(latencias) / len(latencias)
        costo = cmr.costo_pregunta(ultima_respuesta, m["precio_entrada"], m["precio_salida"])
        texto_respuesta = cmr.extraer_texto(ultima_respuesta).replace("\n", " ")

        print(f"  > Latencia promedio: {latencia_promedio:.2f} segundos")
        print(f"  > Costo última petición: {costo:.8f} USD")
        print(f"  > Muestra de respuesta: {texto_respuesta[:70]}...")

        resumen.append({
            "nombre": m["nombre"],
            "id": m["id"],
            "latencia_prom": latencia_promedio,
            "costo": costo,
        })
        registro[m["nombre"]] = {
            "modelo": m["id"],
            "intentos": NUMERO_INTENTOS,
            "latencias": [round(lat, 2) for lat in latencias],
            "latencia_promedio": round(latencia_promedio, 2),
            "costo_ultima_peticion_usd": round(costo, 8),
            "estado": "Exitoso"
        }
    else:
        print(f"  > No se completó la prueba: Cuota diaria/minuto excedida en este modelo (Free Tier).")
        resumen.append({
            "nombre": m["nombre"],
            "id": m["id"],
            "latencia_prom": 0.0,
            "costo": 0.0,
            "estado": "Cuota excedida"
        })
        registro[m["nombre"]] = {
            "modelo": m["id"],
            "intentos": NUMERO_INTENTOS,
            "latencias": [],
            "latencia_promedio": None,
            "costo_ultima_peticion_usd": None,
            "estado": "Cuota excedida en la API (Rate Limit)"
        }

# Tabla comparativa final
print("\n")
print("TABLA COMPARATIVA FINAL")
print("\n")
print(f"{'Modelo':<25} | {'Latencia Prom (s)':<18} | {'Costo Último (USD)':<20}")
print("\n")
for r in resumen:
    print(f"{r['nombre']:<25} | {r['latencia_prom']:<18.2f} | {r['costo']:<20.8f}")

# Guardar resultados en prompts/registro_latencia.json
ruta_salida = BASE_DIR / "prompts" / "registro_latencia.json"
with open(ruta_salida, "w", encoding="utf-8") as archivo:
    json.dump(registro, archivo, indent=2, ensure_ascii=False)

print(f"\nResultados guardados exitosamente en: prompts/registro_latencia.json")
