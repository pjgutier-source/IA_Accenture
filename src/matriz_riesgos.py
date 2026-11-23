def puntaje_riesgo(probabilidad, impacto):
    return probabilidad * impacto


def categoria_riesgo(puntaje):
    if puntaje >= 15:
        return "CRÍTICO"
    elif puntaje >= 9:
        return "ALTO"
    elif puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad, impacto):
    """
    Retorna True si una variación de +-1 en probabilidad o impacto
    provoca que el puntaje cambie de categoría de riesgo.
    """
    cat_original = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dp, di in deltas:
        p_vecino = probabilidad + dp
        i_vecino = impacto + di
        if 1 <= p_vecino <= 5 and 1 <= i_vecino <= 5:
            if categoria_riesgo(puntaje_riesgo(p_vecino, i_vecino)) != cat_original:
                return True
    return False


mis_riesgos = [
    {
        "nombre": "Inyección indirecta en notas de campo recuperadas",
        "probabilidad": 3,
        "impacto": 4,
        "mitigacion": "Filtro regex de patrones sospechosos previo a inyectar contexto en prompt",
    },
    {
        "nombre": "Alucinación en cálculo de desgaste o bits por martillo",
        "probabilidad": 2,
        "impacto": 5,
        "mitigacion": "Validación determinista post-generación de cotas numéricas y rangos de fatiga",
    },
    {
        "nombre": "Fuga de coordenadas georreferenciadas de yacimientos",
        "probabilidad": 2,
        "impacto": 4,
        "mitigacion": "Anonimización y enmascaramiento de UTM y nombres de pozos antes del envío al LLM",
    },
    {
        "nombre": "Fallo de conexión o indisponibilidad de API en faena aislada",
        "probabilidad": 4,
        "impacto": 2,
        "mitigacion": "Caché local con fallback a reglas tabuladas estándar sin inferencia online",
    },
    {
        "nombre": "Desviación de formato JSON en respuestas automáticas de terreno",
        "probabilidad": 3,
        "impacto": 3,
        "mitigacion": "Esquema estructurado Pydantic con reintento y personalización PEFT (LoRA)",
    },
]

if __name__ == "__main__":
    print(f"=== Matriz de Riesgos ({len(mis_riesgos)} riesgos evaluados) ===\n")

    riesgos_calculados = []
    for r in mis_riesgos:
        p = r["probabilidad"]
        i = r["impacto"]
        puntaje = puntaje_riesgo(p, i)
        cat = categoria_riesgo(puntaje)
        limite = esta_en_el_limite(p, i)
        riesgos_calculados.append({**r, "puntaje": puntaje, "categoria": cat, "limite": limite})

    # Ordenar de mayor a menor puntaje
    riesgos_calculados.sort(key=lambda x: x["puntaje"], reverse=True)

    for r in riesgos_calculados:
        alerta_limite = " [AL LÍMITE]" if r["limite"] else ""
        print(f"[{r['categoria']}] {r['nombre']} (Puntaje: {r['puntaje']}){alerta_limite}")
        print(f"  - P={r['probabilidad']} | I={r['impacto']}")
        print(f"  - Mitigación: {r['mitigacion']}\n")
