import os
import requests
from dotenv import load_dotenv
import json
import re

 # Carga de variables de entorno  
load_dotenv()

# Instrucciones para pruebas
system_instruction = (
	"Responde únicamente con 20 palabras."
)

# Schema de la respuesta para pruebas
response_schema = {
	"type": "OBJECT",
	"properties": {
    	"rta": { "type": "STRING" },
    	"poblacion": { "type": "NUMBER" }
	},
	"required": ["rta", "poblacion"]
}

# Modelo para pruebas
modelo = "gemini-3.5-flash-lite"

# arma la peticion hacia API gemini
def armar_peticion(consulta, modelo, system_instruction, response_schema=None):
	if not consulta:
		raise ValueError("Error: Favor incluir consulta")
	if not modelo:
		raise ValueError("Error: Favor incluir modelo")
	api_key = os.getenv("GEMINI_API_KEY")
	url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
	body = {
    	"systemInstruction": {
        	"parts": [ { "text": system_instruction } ]
    	},
    	"contents": [
        	{ "parts": [ { "text": consulta } ] }
    	]
	}
	
	if response_schema is not None:
		body["generationConfig"] = {
			"responseMimeType": "application/json",
			"responseSchema": response_schema
		}
	return url, body

# envia peticion a API gemini
def enviar_peticion(url, body):
	try:
		respuesta = requests.post(url, json=body)
	except requests.exceptions.ConnectionError:
		raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
	try:
		return respuesta.json()
	except requests.exceptions.JSONDecodeError:
		raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")

# extrae texto de la respuesta de API gemini
def extraer_texto(datos):
	try:
		return datos["candidates"][0]["content"]["parts"][0]["text"]
	except (KeyError, IndexError):
		raise RuntimeError("No se pudo extraer el texto de la respuesta.")

# calcula costo en base a modelo utilizado
def costo_pregunta(datos, precio_entrada, precio_salida):
	try:
		uso = datos["usageMetadata"]
		token_input = uso.get("promptTokenCount", 0)
		token_output_count = uso.get("candidatesTokenCount", uso.get("outputTokenCount", 0))
		costo = (token_input * precio_entrada) + (token_output_count * precio_salida) 
		return costo 
	except (KeyError, IndexError):
		raise RuntimeError("No se pudo extraer el conteo de tokens.")

def obtener_dato_prueba(consulta, modelo, system_instruction, response_schema):
    url, body = armar_peticion(consulta, modelo, system_instruction, response_schema)
    datos = enviar_peticion(url, body)
    texto = extraer_texto(datos)
    costo = costo_pregunta(datos, 0.30 / 1000000, 2.5 / 1000000)

    # impresion de resultados
    print("Respuesta del modelo:", texto)
    print("Costo de la pregunta:", costo, "USD")
    print("Proceso terminado sin errores.")

    return texto, costo


def parsear_respuesta_json(texto, claves_esperadas=None):
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.")
    
    if claves_esperadas and not all(clave in datos for clave in claves_esperadas):
        raise ValueError("La respuesta no tiene la estructura esperada.")
    return datos

if __name__ == "__main__":
    obtener_dato_prueba("¿Cuál es la mejor ciudad de Argentina?", modelo, system_instruction, response_schema)