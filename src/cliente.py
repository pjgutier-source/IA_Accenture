import os
import time
from typing import Any, Callable

from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
modelo = "gemini-3.5-flash-lite"

URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
)
headers = {"Content-Type": "application/json"}

# Costo de referencia por 1000 tokens y acumulador de sesión
COSTO_POR_1000_TOKENS = 0.0001
costo_total_sesion = 0.0


def armar_peticion(pregunta: str, system_instruction: str = "") -> dict:
    cuerpo = {
        "contents": [{"parts": [{"text": pregunta}]}]
    }
    if system_instruction:
        cuerpo["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
    return cuerpo


def enviar_peticion(cuerpo: dict) -> dict:
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


def costo_pregunta(respuesta: dict) -> float:
    global costo_total_sesion
    try:
        tokens = respuesta["usageMetadata"]["totalTokenCount"]
    except (KeyError, TypeError):
        raise RuntimeError("No se pudo extraer el conteo de tokens de la respuesta.")

    costo = (tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo
    return costo


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            print(f"Intento {intento} de {intentos} falló por límite de uso. Reintentando...")
            time.sleep(espera_segundos)


def consultar_modelo(
    pregunta: str,
    system_instruction: str = "",
) -> str:
    cuerpo = armar_peticion(pregunta, system_instruction)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    return extraer_texto(respuesta)


if __name__ == "__main__":
    respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
    print(respuesta)
