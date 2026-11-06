from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)

plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte en una sola "
    "palabra: pregunta, queja, sugerencia o elogio. Responde solo "
    "con esa palabra.\n\n{mensaje}"
)

respuesta_generica = RunnableLambda(
    lambda x: (
        "Gracias por tu mensaje. Un miembro de nuestro "
        "equipo te va a responder pronto."
    )
)

def construir_paso_clasificacion(modelo):
    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip().lower())
    )
 
def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
    cadena_elogio=None,
):
    cadena_queja = cadena_queja or RunnablePassthrough()
    cadena_sugerencia = cadena_sugerencia or RunnablePassthrough()
    cadena_pregunta = cadena_pregunta or RunnablePassthrough()
    cadena_elogio = cadena_elogio or RunnablePassthrough()

    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        (lambda x: x["categoria"] == "elogio", cadena_elogio),
        cadena_pregunta,
    )
    return (
        RunnablePassthrough.assign(categoria=paso_clasificacion)
        | bifurcacion
    )

def construir_cadena_queja_segura(cadena_queja):
    return cadena_queja.with_fallbacks([respuesta_generica])
 
def procesar_mensaje_seguro(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        print(f"Error procesando mensaje: {error}")
        return (
            "No pudimos procesar tu mensaje en este "
            "momento. Intenta de nuevo más tarde."
        )


if __name__ == "__main__":

    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    modelo_secundario = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash-lite"
    )

    cadena_pregunta = (
        PromptTemplate.from_template(
            "Responde esta pregunta técnica con precisión:\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )
    cadena_queja = (
        PromptTemplate.from_template(
            "Responde a esta queja con empatía, reconociendo el "
            "problema antes de ofrecer una solución:\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )
    cadena_queja_con_modelo_secundario = (
        PromptTemplate.from_template(
            "Responde a esta queja con empatía, reconociendo "
            "el problema antes de ofrecer una solución:\n\n{mensaje}"
        )
        | modelo_secundario
        | StrOutputParser()
    )
    cadena_queja_segura = cadena_queja.with_fallbacks(
        [cadena_queja_con_modelo_secundario, respuesta_generica]
    )
    cadena_sugerencia = (
        PromptTemplate.from_template(
            "Agradece esta sugerencia y explica cómo se evaluará "
            "dentro del producto:\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )
    cadena_elogio = (
        PromptTemplate.from_template(
            "Agradece este elogio con calidez y amabilidad en una "
            "sola frase breve, sin ofrecer soporte ni soluciones:\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    paso_clasificacion = construir_paso_clasificacion(modelo)
    cadena_con_enrutamiento = construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasificacion,
        cadena_queja=cadena_queja_segura,
        cadena_sugerencia=cadena_sugerencia,
        cadena_pregunta=cadena_pregunta,
        cadena_elogio=cadena_elogio,
    )

    resultado = procesar_mensaje_seguro(
        cadena_con_enrutamiento,
        "La app se cierra cada vez que subo una foto.",
    )
    print(resultado)