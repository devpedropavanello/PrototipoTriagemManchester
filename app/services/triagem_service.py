sintomas_info = {
    "dor_no_peito": {
        "titulo": "Dor no peito",
        "perguntas": [
            {"id": "p1", "texto": "A dor começou de repente?"},
            {"id": "p2", "texto": "Está com suor, enjoo ou falta de ar?"},
            {"id": "p3", "texto": "A dor irradia para braço, mandíbula ou costas?"}
        ],
        "criticos": ["p2", "p3"],
        "urgente": ["p1"]
    },
    "falta_de_ar": {
        "titulo": "Falta de ar",
        "perguntas": [
            {"id": "p1", "texto": "A dificuldade é ao falar ou respirar mesmo em repouso?"},
            {"id": "p2", "texto": "Tem histórico de asma/ DPOC e piora significativa?"},
            {"id": "p3", "texto": "A cor dos lábios ou pele está azulada?"}
        ],
        "criticos": ["p1", "p3"],
        "urgente": ["p2"]
    },
    "febre": {
        "titulo": "Febre",
        "perguntas": [
            {"id": "p1", "texto": "A febre está muito alta (>39°C)?"},
            {"id": "p2", "texto": "Há manchas na pele ou rigidez de nuca?"},
            {"id": "p3", "texto": "Tem dificuldade para respirar ou confusão?"}
        ],
        "criticos": ["p2", "p3"],
        "urgente": ["p1"]
    },
    "queda_acidente": {
        "titulo": "Queda ou acidente",
        "perguntas": [
            {"id": "p1", "texto": "Há sangramento intenso?"},
            {"id": "p2", "texto": "Perda de consciência ou confusão?"},
            {"id": "p3", "texto": "Fratura aparente ou dor intensa?"}
        ],
        "criticos": ["p1", "p2"],
        "urgente": ["p3"]
    },
    "dor_abdominal": {
        "titulo": "Dor abdominal",
        "perguntas": [
            {"id": "p1", "texto": "A dor está muito intensa e súbita?"},
            {"id": "p2", "texto": "Tem vômito persistente ou sangramento?"}
        ],
        "criticos": ["p1", "p2"],
        "urgente": []
    },
    "outros": {
        "titulo": "Outros sintomas",
        "perguntas": [
            {"id": "p1", "texto": "É um sintoma novo e muito intenso?"},
            {"id": "p2", "texto": "Há sangramento ou sinal de gravidade?"}
        ],
        "criticos": ["p2"],
        "urgente": ["p1"]
    },
    "sintoma_leve": {
        "titulo": "Sintoma leve",
        "perguntas": [
            {"id": "p1", "texto": "Está presente, mas não é grave?"},
            {"id": "p2", "texto": "É incômodo, mas não prejudica atividades?"}
        ],
        "criticos": [],
        "urgente": []
    }
}

def aplicar_regras_sintoma(sintoma_key, respostas):
    info = sintomas_info.get(sintoma_key)
    if not info:
        return "verde", "Sintom não encontrado - avaliação padrão"

    criticos = info.get("criticos", [])
    urgente = info.get("urgente", [])

    if not isinstance(respostas, list) or not respostas:
        return "verde", "Sem resposta válidas."

    if any(r["resposta"] == "sim" and r["id"] in criticos for r in respostas):
        return "vermelho", f"{info['titulo']}: Condição crítica - atendimento imediato."

    if any(r["resposta"] == "sim" and r["id"] in urgente for r in respostas):
        return "laranja", f"{info['titulo']}: Situação muito urgente - avaliação rápida necessária."

    if any(r["resposta"] == "sim" for r in respostas):
        return "amarelo", f"{info['titulo']}: Condição moderada - aguardar atendimento."

    return "verde", f"{info['titulo']}: Sem sinais de gravidade."

def classificar_triagem(sintoma_key, respostas):
    prioridade = {"vermelho": 4, "laranja": 3, "amarelo": 2, "verde": 1}

    # MULTI: avalia cada sintoma separadamente e pega o mais grave
    if sintoma_key == "_multi_":
        pior_cor = "verde"
        pior_texto = "Condição estável — sem risco imediato."

        # agrupa respostas por sintoma_key
        respostas_por_sintoma = {}
        for r in respostas:
            k = r.get("sintoma_key")
            if not k:
                continue
            respostas_por_sintoma.setdefault(k, []).append(r)

        for sintoma_nome, respostas_do_sintoma in respostas_por_sintoma.items():
            cor, texto = aplicar_regras_sintoma(sintoma_nome, respostas_do_sintoma)

            if prioridade.get(cor, 0) > prioridade.get(pior_cor, 0):
                pior_cor, pior_texto = cor, texto

        return pior_cor, pior_texto

    # sintoma único
    return aplicar_regras_sintoma(sintoma_key, respostas)