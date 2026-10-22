# Decisión de arquitectura: elección de modelo

## Modelo elegido

**Gemini 3.5 Flash-Lite** (`gemini-3.5-flash-lite`), para la funcionalidad principal de la miniaplicación.

## Diagrama de arquitectura

![Diagrama de arquitectura de la miniaplicación](./diagrama_flujo.drawio.png)

El flujo completo va desde la pregunta del usuario hasta la respuesta final, pasando por `obtener_dato_prueba`, `armar_peticion`, `enviar_peticion` (con la credencial `GEMINI_API_KEY` leída desde `.env` y el manejo de errores en `try/except`), `extraer_texto` y `costo_pregunta` (que calcula el costo a partir de `usageMetadata`). El diagrama completo está en `docs/diagrama_flujo.drawio.png`.

## Comparación de candidatos

| Criterio | Gemini 3.5 Flash-Lite | Gemini 3.1 Flash-Lite | Gemini 3.8 Flash |
|---|---|---|---|
| Costo por 1000 tokens de entrada | 0,000100 USD | 0,000250 USD | 0,000750 USD |
| Costo por 1000 tokens de salida | 0,000400 USD | 0,001500 USD | 0,003750 USD |
| Latencia promedio observada | 2,0 segundos | 12,0 segundos | 65,8 segundos |
| Cuota diaria disponible (RPD) | 500 peticiones/día | 500 peticiones/día | 20 peticiones/día |
| Calidad de respuesta para el caso | Buena: concisa, rápida y cumple con el límite de 20 palabras | Buena: redacción correcta pero con demora perceptible | Muy buena: amplio detalle, pero con severa demora por saturación |
| Fecha de medición | 2026-10-22 | 2026-10-22 | 2026-10-22 |

## Justificación

Para esta aplicación, un asistente simple y ágil que responda de forma concisa y directa es suficiente para la experiencia del usuario, el criterio decisivo fue la combinación de **latencia, costo y cuota operativa (RPD)**:
- **Latencia:** `gemini-3.5-flash-lite` responde en ~2,0 segundos, siendo **6 veces más veloz** que `gemini-3.1-flash-lite` (~12,0 s) y **más de 30 veces más rápido** que `gemini-3.8-flash` (~65,8 s bajo alta demanda).
- **Costo:** `gemini-3.5-flash-lite` es 2,5 veces más económico que `gemini-3.1-flash-lite` y 7,5 veces más barato en entrada respecto a `gemini-3.8-flash`.
- **Cuota operativa (RPD):** `gemini-3.5-flash-lite` cuenta con **500 peticiones diarias (RPD)** frente a las escasas **20 RPD** de los modelos Flash estándar como `gemini-3.8-flash`, otorgando 25 veces más disponibilidad diaria sin riesgos de bloqueo por saturación de cuota.

Por lo tanto, `gemini-3.5-flash-lite` ofrece la mejor relación costo-rendimiento, menor latencia y la mayor estabilidad operativa para este caso de uso.

## Alternativas descartadas y por qué

Considerar que todo este análisis es bajo una licencia gratuita de API de Gemini. Probablemente si fuera pagada las limitaciones serían distintas tanto de la cuota como la prioridad de procesamiento, lo que afecta finalmente los tiempos.

- **Gemini 3.1 Flash-Lite:** Aunque dispone de una buena cuota diaria (500 RPD), su latencia promedio observada (~12 segundos) resulta excesiva para una miniaplicación interactiva de respuestas breves.
- **Gemini 3.8 Flash:** A pesar de su excelente calidad de redacción, presentó tiempos de respuesta críticos (~65,8 segundos debido a alta demanda en los servidores) y una cuota muy limitada de solo 20 peticiones diarias, lo que inviabiliza su uso regular en este entorno.
