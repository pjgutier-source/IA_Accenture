# Límites de la métrica de evaluación

## Qué mide

Coincidencia exacta de palabras/tokens entre una respuesta generada y una referencia esperada, contando repeticiones mediante normalización (precisión, cobertura y F1-score).

## Modos de falla conocidos

- Respuestas completamente correctas pero más detalladas o formales.
- Variaciones léxicas válidas (ej. "almohadilla" vs. "numeral", "palabra reservada" vs. "palabra clave", "objeto nulo" vs. "la nada") no hacen coincidencia exacta y bajan la métrica.
- Elementos como comillas invertidas, paréntesis (ej. `print()` vs. `print`, `def` vs. `palabra clave def`) pueden alterar la tokenización y la cobertura.


## Muestra revisada

Se evaluó un lote de **20 consultas técnicas sobre Python** utilizando respuestas concisas generadas por el modelo y comparadas contra sus referencias:

- **Casos evaluados**: 20
- **F1 promedio**: 0.5552
- **Precisión promedio**: 0.4270
- **Cobertura promedio**: 0.8583


## Recomendación de uso

1. **Uso de F1 / Cobertura**: Utilizar la cobertura para verificar si los conceptos y términos clave fueron cubiertos, y F1 para comparar versiones del modelo o prompts.
2. **Revisión manual obligatoria**:
   - Casos con **F1 < 0.50** causados comúnmente por estilo/longitud pero conceptualmente correctos.
   - Datos críticos como fechas, cifras, nombres propios o código sintáctico donde un F1 alto no garantiza corrección factual total.