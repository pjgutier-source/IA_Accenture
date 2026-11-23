from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


def proponer(estado: EstadoDespliegue):
    return {}


def supervisar(estado: EstadoDespliegue):
    decision = interrupt({
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"],
    })
    return {"aprobado": decision}


def aplicar(estado: EstadoDespliegue):
    if estado["aprobado"]:
        print("version", estado["huella_nueva"], "activada")
    else:
        print("version", estado["huella_nueva"], "rechazada, se mantiene la anterior")
    return {}


grafo = StateGraph(EstadoDespliegue)
grafo.add_node("proponer", proponer)
grafo.add_node("supervisar", supervisar)
grafo.add_node("aplicar", aplicar)
grafo.add_edge(START, "proponer")
grafo.add_edge("proponer", "supervisar")
grafo.add_edge("supervisar", "aplicar")
grafo.add_edge("aplicar", END)

app_despliegue = grafo.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    from registro_prompts import registro

    ultima_version = registro.ultima("prompt_asistente_perforacion")
    huella = ultima_version["huella"]

    print("=== Camino 1: Aprobacion de despliegue ===")
    config1 = {"configurable": {"thread_id": "despliegue-aprobado-1"}}
    res1 = app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config1)
    print("1) tras invocar (interrumpido):", res1)
    print("2) pendiente de revision:", app_despliegue.get_state(config1).interrupts[0].value)
    res_aprobado = app_despliegue.invoke(Command(resume=True), config=config1)
    print("3) tras aprobar:", res_aprobado)

    print("\n=== Camino 2: Rechazo de despliegue ===")
    config2 = {"configurable": {"thread_id": "despliegue-rechazado-2"}}
    app_despliegue.invoke({"huella_nueva": huella, "aprobado": False}, config=config2)
    res_rechazado = app_despliegue.invoke(Command(resume=False), config=config2)
    print("4) tras rechazar:", res_rechazado)
