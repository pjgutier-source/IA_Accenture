import json
import time
import sys
from pathlib import Path

# Definir raiz de proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# ruta de modulos (carpeta src)
sys.path.append(str(BASE_DIR))
from src import consumir_gemini_refactorizada as cmr

registro = {}

# usamos rutas absolutas
ruta_prompts = BASE_DIR / "src" / "banco_de_prompts.json"
ruta_resultados = BASE_DIR / "prompts" / "registro_resultados.json"

# abrimos banco de promppts json
with open(ruta_prompts, "r", encoding="utf-8") as archivo_prompts:
    banco_de_prompts = json.load(archivo_prompts)

# ejecutamos test
for prompt in banco_de_prompts:
    exitos = 0
    intentos = 3
    for intento in range(intentos):
        url, body = cmr.armar_peticion(
            prompt["ejemplo_usuario"],
            prompt["system_instruction"],
            prompt.get("response_schema"),
        )
        respuesta = cmr.enviar_peticion(url, body)
        texto = cmr.extraer_texto(respuesta)
        try:
            datos = cmr.parsear_respuesta_json(texto)
            if all(clave in datos for clave in prompt["claves_esperadas"]):
                exitos += 1
        except ValueError as error:
            print(f"  intento {intento + 1} falló: {error}")
        time.sleep(1)
    print(f"{prompt['nombre']}: {exitos}/{intentos} respuestas válidas")
    registro[prompt["nombre"]] = {"exitos": exitos, "intentos": intentos}

# grabamos resultados
with open(ruta_resultados, "w", encoding="utf-8") as archivo:
    json.dump(registro, archivo, indent=2, ensure_ascii=False)