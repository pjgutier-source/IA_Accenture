from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from agente_con_herramientas import (
    calcular_dias_prueba_bits,
    calcular_bits_por_martillo,
    herramientas,
    prompt_sistema,
)
from langchain.agents import create_agent


class ModeloFalsoConHerramientas(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def test_calcular_dias_prueba_bits_directo():
    resultado = calcular_dias_prueba_bits.invoke({
        "cantidad_bits": 4,
        "durabilidad_bit": "medio",
        "rendimiento_diario_m": 120,
    })
    assert "20 día(s)" in resultado
    assert "2400 m" in resultado


def test_calcular_bits_por_martillo_directo():
    resultado = calcular_bits_por_martillo.invoke({
        "vida_util_martillo_m": 4000,
        "durabilidad_bit": "medio",
    })
    assert "7 bit(s)" in resultado


def test_agente_no_usa_herramienta_para_pregunta_general():
    modelo_falso = ModeloFalsoConHerramientas(
        responses=[
            AIMessage(content="Para contactar a soporte puedes escribir a soporte@empresa.com.")
        ]
    )

    agente = create_agent(
        model=modelo_falso,
        tools=herramientas,
        system_prompt=prompt_sistema,
    )

    resultado = agente.invoke({
        "messages": [{"role": "user", "content": "¿Cómo puedo contactar a soporte?"}]
    })

    llamadas_herramientas = [
        tc
        for msg in resultado["messages"]
        if hasattr(msg, "tool_calls") and msg.tool_calls
        for tc in msg.tool_calls
    ]

    assert llamadas_herramientas == []
    assert "soporte@empresa.com" in resultado["messages"][-1].content


def test_agente_dispara_herramienta_cuando_hay_calculo():
    modelo_falso = ModeloFalsoConHerramientas(
        responses=[
            AIMessage(
                content="",
                tool_calls=[{
                    "name": "calcular_bits_por_martillo",
                    "args": {"vida_util_martillo_m": 4000, "durabilidad_bit": "medio"},
                    "id": "call_123",
                }],
            ),
            AIMessage(content="Necesitarás 7 bits para completar la vida útil del martillo."),
        ]
    )

    agente = create_agent(
        model=modelo_falso,
        tools=herramientas,
        system_prompt=prompt_sistema,
    )

    resultado = agente.invoke({
        "messages": [{"role": "user", "content": "¿Cuántos bits medio necesito para un martillo de 4000 m?"}]
    })

    llamadas_herramientas = [
        tc
        for msg in resultado["messages"]
        if hasattr(msg, "tool_calls") and msg.tool_calls
        for tc in msg.tool_calls
    ]

    assert len(llamadas_herramientas) == 1
    assert llamadas_herramientas[0]["name"] == "calcular_bits_por_martillo"
    assert "7 bits" in resultado["messages"][-1].content
