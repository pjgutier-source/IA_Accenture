# Límites de autonomía: Agente de Envíos y Soporte

## Herramientas y nivel de riesgo

- **consultar_estado_envio_con_historial**: bajo (solo lee información del paquete, no cambia nada).

- **calcular_costo_envio**: bajo (solo hace una cuenta matemática, no cobra dinero ni toca sistemas externos).

- **buscar_en_documentacion**: bajo (solo busca y lee texto de ayuda interno).

- **generar_reembolso**: alto (mueve dinero de verdad y no se puede deshacer; si el agente se equivoca, se pierde dinero).

## Herramientas que requieren aprobación humana

- **generar_reembolso**:
  - Requiere que una persona autorice la operación con `s/n` antes de pagar, para evitar que el agente devuelva dinero por error o ante engaños del usuario.

## Revisión de trazas

- **Frecuencia**: Una vez por semana, o al final de cada día si hay mucho uso.

- **Qué se busca**:
  - Herramientas usadas dos o más veces seguidas (señal de que el agente se quedó pegado o la herramienta falló).
  - Herramientas usadas sin necesidad (por ejemplo, hacer cálculos ante un simple saludo).
  - Casos donde el usuario intentó pedir un reembolso sin cumplir las condiciones.

## Qué hacer ante un comportamiento inesperado

1. **Frenar la herramienta peligrosa**: Quitar `generar_reembolso` del código para que el agente solo pueda responder preguntas informativas.
2. **Revisar el archivo de trazas**: Abrir `trazas_agente.jsonl` y buscar qué preguntó el usuario y qué intentó responder el agente.
3. **Corregir el problema**: Mejorar las instrucciones del agente o la validación de datos para que no vuelva a equivocarse.
4. **Probar antes de volver a activar**: Correr las pruebas locales y recién ahí reactivar la herramienta.
