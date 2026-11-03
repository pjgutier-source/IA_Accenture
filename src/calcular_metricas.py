import json
import time
from collections import Counter
from pipeline_texto import procesar_texto
from cliente import consultar_modelo
from pathlib import Path


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las coincidencias entre referencia y respuesta."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())

def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 de dos listas de tokens."""
    coincidencias = contar_coincidencias(
        tokens_referencia, tokens_respuesta
    )

    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    resultado = {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }

    return resultado

def calcular_metricas(texto_referencia, texto_respuesta):

    tokens_referencia = procesar_texto(texto_referencia)

    tokens_respuesta = procesar_texto(texto_respuesta)

    return calcular_precision_cobertura_f1(
        tokens_referencia, tokens_respuesta
    )  

def resumir_metricas(resultados):

    if not resultados:
        return {
            "precision_promedio": 0,
            "cobertura_promedio": 0,
            "f1_promedio": 0,
        }

    n = len(resultados)

    return {
        "precision_promedio": sum(
            r["precision"] for r in resultados
        ) / n,

        "cobertura_promedio": sum(
            r["cobertura"] for r in resultados
        ) / n,

        "f1_promedio": sum(r["f1"] for r in resultados) / n,
    } 

if __name__ == "__main__":
    casos = [
        ("¿Qué es Python?", "Python es un lenguaje de programación interpretado."),
        ("¿Cuándo se creó Python?", "Python fue creado en 1991."),
        ("¿Qué es una lista en Python?", "Una lista es una colección ordenada y modificable."),
        ("¿Quién creó el lenguaje Python?", "Python fue creado por Guido van Rossum."),
        ("¿Qué es una tupla en Python?", "Una tupla es una colección ordenada e inmutable."),
        ("¿Qué es un diccionario en Python?", "Un diccionario es una colección de pares clave y valor."),
        ("¿Qué función se utiliza para mostrar texto en pantalla en Python?", "Se utiliza la función print."),
        ("¿Cómo se define una función en Python?", "Una función se define con la palabra clave def."),
        ("¿Qué es la indentación en Python?", "La indentación es el espacio al inicio de una línea que define bloques de código."),
        ("¿Qué tipo de dato representa valores de verdadero o falso en Python?", "El tipo de dato booleano o bool."),
        ("¿Cómo se escribe un comentario de una sola línea en Python?", "Se escribe usando el símbolo numeral al inicio."),
        ("¿Qué método se usa para agregar un elemento al final de una lista?", "Se utiliza el método append."),
        ("¿Para qué se utiliza la función len en Python?", "La función len devuelve la longitud o cantidad de elementos de un objeto."),
        ("¿Qué palabras clave se usan para el manejo de excepciones en Python?", "Se utilizan las palabras clave try y except."),
        ("¿Qué es un conjunto o set en Python?", "Es una colección no ordenada de elementos únicos."),
        ("¿Cómo se importa un módulo o librería en Python?", "Se utiliza la palabra clave import."),
        ("¿Qué representa el valor None en Python?", "None representa la ausencia de un valor o la nada."),
        ("¿Cómo se convierte un texto a número entero en Python?", "Se convierte utilizando la función int."),
        ("¿Qué instrucción se usa para salir de un bucle antes de tiempo?", "Se utiliza la instrucción break."),
        ("¿Qué es una función lambda en Python?", "Es una función anónima definida en una sola línea."),
    ]


    resultados = []

    # incluimos instruccion para evitar respuestas largas.
    instruccion = (
        "Responde de forma directa, concisa y precisa en una sola oración. "
        "No des explicaciones adicionales ni ejemplos de código."
    )

    for i, (consulta, referencia) in enumerate(casos, 1):
        print(f"Procesando caso {i}/{len(casos)}: {consulta}")
        respuesta = consultar_modelo(consulta, instruccion)
        metricas = calcular_metricas(referencia, respuesta)
        resultados.append({
            "consulta": consulta,
            "respuesta": respuesta,
            **metricas,
        })
        # Pausa de 5 segundos para mantenerse por debajo del límite de 15 RPM
        time.sleep(5)

    ruta_archivo = Path(__file__).parent / "resultados_metricas.json" # grabamos en misma carpeta

    with open(
        ruta_archivo, "w", encoding="utf-8"
    ) as archivo:

        json.dump(resultados, archivo, indent=2, ensure_ascii=False)