import os
import requests
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env (por ejemplo GEMINI_API_KEY)
# hacia el entorno del proceso. Sin esta línea, os.getenv("GEMINI_API_KEY")
# devolvería None aunque el .env exista, porque nada lo habría leído todavía.
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
# api_key = "555Ab8RN6JiQr55555ay38iRS0JKTFLueVxo5eQqfdNcI-JUdauSQ" # prueba key erronea

# El documento de la lección usa "gemini-2.0-flash", pero ese modelo ya fue
# dado de baja por Google (aparece como "Shut down" en su documentación).
# Usamos "gemini-3.8-flash", el modelo Flash vigente más reciente.

# Modelo para pruebas
modelo = "gemini-3.5-flash-lite"

URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
)
headers = {"Content-Type": "application/json"}


def armar_peticion(pregunta: str, system_instruction: str = "") -> dict:
    cuerpo = {
        "contents": [{"parts": [{"text": pregunta}]}]
    }
    if system_instruction:
        cuerpo["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
    return cuerpo


def enviar_peticion(cuerpo):
    try:
        respuesta = requests.post(URL, json=cuerpo, headers=headers, timeout=10)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al proveedor. Puede ser momentáneo.")
    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY.")
    if respuesta.status_code == 429 or respuesta.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintentar.")
    respuesta.raise_for_status()
    return respuesta.json()


def extraer_texto(datos: dict) -> str:
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("No se pudo extraer el texto de la respuesta.")


if __name__ == "__main__":
    cuerpo = armar_peticion("Hola")
    resultado = enviar_peticion(cuerpo)
    print(extraer_texto(resultado))

