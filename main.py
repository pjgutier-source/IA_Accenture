# importamos funciones de modulo consumir_gemini_refactorizada, revisar modulo para mas detalles
from src import consumir_gemini_refactorizada as cmr

# Definicion de Modelo
modelo = "gemini-3.5-flash-lite"

# Definimos instrucciones, schema y consulta
system_instruction = (
	"Responde únicamente con 20 palabras."
)

response_schema = {
	"type": "OBJECT",
	"properties": {
    	"rta": { "type": "STRING" },
    	"poblacion": { "type": "NUMBER" }
	},
	"required": ["rta", "poblacion"]
}

consulta = "¿Cuál es la mejor ciudad de Chile?"

if __name__ == "__main__":
    cmr.obtener_dato_prueba(consulta, modelo, system_instruction, response_schema)