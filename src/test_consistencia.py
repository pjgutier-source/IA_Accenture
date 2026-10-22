import consumir_gemini_refactorizada as cmr
import json
import time

registro = {}

with open("src/banco_de_prompts.json", "r", encoding="utf-8") as archivo_prompts:
    banco_de_prompts = json.load(archivo_prompts)

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

with open("prompts/registro_resultados.json", "w", encoding="utf-8") as archivo:
    json.dump(registro, archivo, indent=2, ensure_ascii=False)