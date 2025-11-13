from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "troque_esta_chave_em_producao"

pacientes = {}
triagens = []

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

def classificar_triagem(sintoma_key, respostas):
    prioridade = {"vermelho": 4, "laranja": 3, "amarelo": 2, "verde": 1}

    if sintoma_key == "_multi_":
        niveis_detectados = []
        sintomas_avaliados = set()

        for resposta in respostas:
            sintoma_nome = resposta.get("sintoma_key")
            if sintoma_nome in sintomas_info and sintoma_nome not in sintomas_avaliados:
                respostas_do_sintoma = [r for r in respostas if r.get("sintoma_key") == sintoma_nome]
                cor, texto = aplicar_regras_sintoma(sintoma_nome, respostas_do_sintoma)
                niveis_detectados.append((cor, texto))
                sintomas_avaliados.add(sintoma_nome)

        if not niveis_detectados:
            return "verde", "Condição estável — sem risco imediato."

        cor_final, texto_final = max(niveis_detectados, key=lambda x: prioridade.get(x[0], 0))
        return cor_final, texto_final

    return aplicar_regras_sintoma(sintoma_key, respostas)


def aplicar_regras_sintoma(sintoma_key, respostas):
    info = sintomas_info.get(sintoma_key)
    if not info:
        return "verde", "Sintoma não encontrado - avaliação padrão."

    criticos = info.get("criticos", [])
    urgentes = info.get("urgente", [])

    if not isinstance(respostas, list) or not respostas:
        return "verde", "Sem respostas válidas."

    if any(r["resposta"] == "sim" and r["id"] in criticos for r in respostas):
        return "vermelho", f"{info['titulo']}: Condição crítica - atendimento imediato."

    if any(r["resposta"] == "sim" and r["id"] in urgentes for r in respostas):
        return "laranja", f"{info['titulo']}: Situação muito urgente - avaliação rápida necessária."

    if any(r["resposta"] == "sim" for r in respostas):
        return "amarelo", f"{info['titulo']}: Condição moderada - aguardar atendimento."

    return "verde", f"{info['titulo']}: Sem sinais de gravidade."


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/identificacao", methods=["GET", "POST"])
def identificacao():
    if request.method == "POST":
        nome = request.form.get("nome")
        data_nasc = request.form.get("data_nasc")
        sexo = request.form.get("sexo")

        if not nome:
            flash("Informe o nome do paciente.", "warning")
            return redirect(url_for("identificacao"))

        paciente_id = str(uuid.uuid4())
        pacientes[paciente_id] = {"nome": nome, "data_nasc": data_nasc, "sexo": sexo}
        return redirect(url_for("sintoma", paciente_id=paciente_id))

    return render_template("identificacao.html")

@app.route("/sintoma/<paciente_id>", methods=["GET", "POST"])
def sintoma(paciente_id):
    paciente = pacientes.get(paciente_id)
    if not paciente:
        flash("Paciente não encontrado. Comece novamente.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        sintomas_escolhidos = request.form.getlist("sintomas")
        outros_texto = request.form.get("outros_texto", "").strip()

        if not sintomas_escolhidos and not outros_texto:
            flash("Selecione pelo menos um sintoma ou descreva outro.", "warning")
            return redirect(url_for("sintoma", paciente_id=paciente_id))

        paciente["sintomas"] = sintomas_escolhidos
        paciente["outros_texto"] = outros_texto
        return redirect(url_for("perguntas", paciente_id=paciente_id, sintoma_key="_multi_"))

    return render_template("sintoma.html", paciente=paciente, sintomas_info=sintomas_info)

@app.route("/perguntas/<paciente_id>/<sintoma_key>", methods=["GET", "POST"])
def perguntas(paciente_id, sintoma_key):
    paciente = pacientes.get(paciente_id)
    if not paciente:
        flash("Paciente não encontrado. Comece novamente.", "danger")
        return redirect(url_for("index"))

    perguntas_list = []
    titulos_sintomas = []

    if sintoma_key == "_multi_":
        for s in paciente.get("sintomas", []):
            info_sintoma = sintomas_info.get(s)
            if info_sintoma:
                titulos_sintomas.append(info_sintoma["titulo"])
                for p in info_sintoma["perguntas"]:
                    perguntas_list.append({
                        "id": f"{s}_{p['id']}",
                        "texto": p["texto"],
                        "sintoma_key": s
                    })
        info = {
            "titulo": ", ".join(titulos_sintomas) or "Múltiplos sintomas",
            "perguntas": perguntas_list
        }
    else:
        info = sintomas_info.get(sintoma_key)
        if not info:
            flash("Sintoma inválido.", "danger")
            return redirect(url_for("sintoma", paciente_id=paciente_id))

        perguntas_list = [
            {"id": p["id"], "texto": p["texto"], "sintoma_key": sintoma_key}
            for p in info.get("perguntas", [])
        ]
        info = {"titulo": info["titulo"], "perguntas": perguntas_list}

    if request.method == "POST":
        respostas = []
        for p in info["perguntas"]:
            val = request.form.get(p["id"], "nao")
            id_parts = p["id"].split("_")
            original_id = id_parts[-1]
            respostas.append({
                "id": original_id,
                "pergunta": p["texto"],
                "resposta": "sim" if val == "sim" else "nao",
                "sintoma_key": p["sintoma_key"]
            })

        cor, texto = classificar_triagem(sintoma_key, respostas)

        sintomas_titulos_lista = [
            sintomas_info[s]["titulo"] for s in paciente.get("sintomas", [])
            if s in sintomas_info
        ]

        triagem = {
            "id": str(uuid.uuid4())[:8],
            "paciente_id": paciente_id,
            "paciente_nome": paciente["nome"],
            "idade": paciente.get("data_nasc", ""),
            "sexo": paciente.get("sexo", ""),
            "sintoma": sintoma_key,
            "sintomas_titulo": info.get("titulo"),
            "sintoma_titulo": info.get("titulo"),
            "respostas": respostas,
            "cor": cor,
            "texto": texto,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "paciente": {
                "sintomas": sintomas_titulos_lista
            }
        }
        triagens.append(triagem)
        return redirect(url_for("resultado", triagem_id=triagem["id"]))

    return render_template("perguntas.html", paciente=paciente, info=info)

@app.route("/resultado/<triagem_id>")
def resultado(triagem_id):
    triagem = next((t for t in triagens if t["id"] == triagem_id), None)
    if not triagem:
        flash("Triagem não encontrada.", "danger")
        return redirect(url_for("index"))
    return render_template("resultado.html", triagem=triagem)

@app.route("/relatorio")
def relatorio():
    return render_template("relatorio.html", triagens=triagens)

if __name__ == "__main__":
    app.run(debug=True)
