from pathlib import Path
import json

revision_manual = [
   {
    "consulta": "¿Qué método se usa para agregar un elemento al final de una lista?",
    "respuesta": "El método utilizado para agregar un elemento al final de una lista es `append()`.",
    "precision": 0.21428571428571427,
    "cobertura": 0.6,
    "f1": 0.3157894736842105,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "respuesta mas completa")
   },
   {
    "consulta": "¿Cómo se importa un módulo o librería en Python?",
    "respuesta": "Se importa un módulo o librería en Python utilizando la palabra reservada `import` seguida del nombre del módulo.",
    "precision": 0.2222222222222222,
    "cobertura": 0.6666666666666666,
    "f1": 0.3333333333333333,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "respuesta mas completa")
  },
   {
    "consulta": "¿Qué instrucción se usa para salir de un bucle antes de tiempo?",
    "respuesta": "La instrucción que se usa para salir de un bucle antes de tiempo es `break`.",
    "precision": 0.26666666666666666,
    "cobertura": 0.8,
    "f1": 0.4,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "respuesta mas detallada")
  },
   {
    "consulta": "¿Qué es un diccionario en Python?",
    "respuesta": "Un diccionario en Python es una estructura de datos mutable que almacena pares de clave-valor de manera desordenada y optimizada para búsquedas rápidas.",
    "precision": 0.30434782608695654,
    "cobertura": 0.7,
    "f1": 0.42424242424242425,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "no menciona concepto de coleccion")
  },   
   {
    "consulta": "¿Qué es una función lambda en Python?",
    "respuesta": "Una función lambda en Python es una función anónima y de una sola línea definida mediante la palabra reservada `lambda`.",
    "precision": 0.45,
    "cobertura": 1.0,
    "f1": 0.6206896551724138,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "respuesta mas completa")
  },
   {
    "consulta": "¿Cómo se escribe un comentario de una sola línea en Python?",
    "respuesta": "Se escribe utilizando el símbolo de almohadilla (#) al inicio del comentario.",
    "precision": 0.5454545454545454,
    "cobertura": 0.75,
    "f1": 0.631578947368421,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "es mas detallado indicando el simbolo")
  },
  {
    "consulta": "¿Qué representa el valor None en Python?",
    "respuesta": "El valor `None` en Python representa la ausencia de un valor o un objeto nulo.",
    "precision": 0.5333333333333333,
    "cobertura": 0.8,
    "f1": 0.64,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "explicado distinto pero mismo significado")
  },
  {
    "consulta": "¿Cuándo se creó Python?",
    "respuesta": "Python fue creado en 1991 por Guido van Rossum.",
    "precision": 0.5555555555555556,
    "cobertura": 1.0,
    "f1": 0.7142857142857143,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "la respuesta agrega al creador")
  },
  {
    "consulta": "¿Quién creó el lenguaje Python?",
    "respuesta": "El lenguaje Python fue creado por Guido van Rossum.",
    "precision": 0.7777777777777778,
    "cobertura": 1.0,
    "f1": 0.8750000000000001,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "la respuesta incluye palabra adicional lenguaje")
  },
  {
    "consulta": "¿Cómo se convierte un texto a número entero en Python?",
    "respuesta": "Se convierte utilizando la función `int()`.",
    "precision": 1.0,
    "cobertura": 1.0,
    "f1": 1.0,
    "correccion_factual": "si",
    "completitud": "si",
    "contradiccion": "no",
    "nota": (
        "misma respuesta, detalle de parentesis adicional")
  }
]

# Guarda en la misma carpeta
ruta_archivo = Path(__file__).parent / "revision_manual.json"

with open(ruta_archivo, "w", encoding="utf-8") as archivo:
    json.dump(revision_manual, archivo, indent=2, ensure_ascii=False)
