# Decisión de personalización

## 1. El problema
El asistente no siempre devuelve el formato JSON requerido: de 20 respuestas evaluadas en lenguaje natural, 6 (30 %) no incluyeron las claves 'tipo_operacion' y 'prioridad' o agregaron explicaciones no solicitadas. El modelo comprende los cálculos de bits y martillos; la carencia radica en la estricta consistencia del formato de salida.

## 2. Resultado del método de decisión
- PEFT: 5 puntos
- RAG: 2 puntos
- Fine-tuning completo: 1 puntos

## 3. Técnica elegida y por qué
Técnica elegida: **PEFT**.

Se elige PEFT porque enseña al modelo a responder siempre en el formato JSON correcto de forma rápida y barata, sin tener que reentrenar todo el modelo desde cero. Se descarta RAG porque el modelo ya conoce los datos de bits y martillos; lo que falla es el formato de salida, no la información.

## 4. Qué necesitaría para ejecutarla
Actualmente disponemos de un dataset validado de 10 ejemplos etiquetados en `dataset_tuning.py` con 0 errores. Para entrenar un adaptador PEFT confiable en la API de Gemini se requiere un volumen mínimo de 25 a 50 ejemplos. Por lo tanto, se necesitan generar y etiquetar entre 15 y 40 ejemplos adicionales cubriendo las 4 operaciones (cálculo de días, bits por martillo, especificaciones y seguridad). No se requiere indexar ningún corpus documental nuevo.
