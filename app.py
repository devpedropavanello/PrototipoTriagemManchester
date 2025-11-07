from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "troque_esta_chave_em_producao"

pacientes = {}
triagens = []

sintomas_info = {
    "dor_no_peito": {
        "titulo": "Dor no Peito",
        "perguntas": [
            {"id": "p1", "texto": "A dor começou de repente?"},
            {"id": "p2", "texto": "Está com falta de ar?"},
            {"id": "p3", "texto": "A dor irradia para o braço, mandíbula ou costas?"}
        ],
        "criticos": ["p2", "p3"],
        "urgente": ["p1"]
    },
    "falta_de_ar": {
        "titulo": "Falta de Ar",
        "perguntas": [
            {"id": "p1", "texto": "A dificuldade é ao falar ou respirar mesmo em repouso?"},
            {"id": "p2", "texto": "Tem histórico de asma/DPOC e piora significativa?"},
            {"id": "p3", "texto": "A cor dos lábios ou pele está azulada?"}
        ],
        "criticos": ["p1","p3"],
        "urgente": ["p2"]
    },
    "febre": {
        "titulo": "Febre",
        "perguntas": [
            {"id": "p1", "texto": "A febre está muito alta (>39°C)?"},
            {"id": "p2", "texto": "Há manchas na pele ou rigidez de nuca?"},
            {"id": "p3", "texto": "Tem dificuldade para respirar ou confusão mental?"}
        ],
        "criticos": ["p2", "p3"],
        "urgente": ["p1"]
    },
    "queda_acidente": {
        "titulo": "Queda ou Acidente",
        "perguntas": [
            {"id": "p1", "texto": "Há sangramento intenso?"},
            {"id": "p2", "texto": "Perda de ocnsciência ou confusão mental?"},
            {"id": "p3", "texto": "Fratura aparente ou dor intensa?"}
        ],
        "criticos": ["p1", "p2"],
        "urgente": ["p3"]
    },
    "dor_abdominal": {
        "titulo": "Dor Abdominal",
        "perguntas": [
            {"id": "p1", "texto": "A dor está muito intensa ou súbita?"},
            {"id": "p2", "texto": "Tem vômito persistente ou sangramento?"},
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
    }
}

def classificar_triagem(sintomas_key, respostas):
    """
    respostas: dict { 'p1': 'sim'/'não', ... }
    Retorna (cor, nivel_texto)
    Cores: vermelho, laranja, amarelo, verde, azul (prototipo)
    Regras simplificadas:
        - se alguma pergunta crítica = sim -> vermelho
        - elif alguma urgente = sim -> laranja
        - elif >=1 respostas 'sim' -> amarelo
        - else -> verde
    """
    info = sintomas_info.get(sintomas_key, {})
    criticos = info.get("criticos", [])
    urgente = info.get("urgente", [])
    for q in criticos:
        if respostas.get(q) == "sim":
            return ("vermelho","Emergencia - atendimento imediato")
    for q in urgente:
        if respostas.get(q) == "sim":
            return ("laranja","Muito Urgente - atendimento em até 10 minutos")
    if any(v == "sim" for v in respostas.values()):
        return ("amarelo","Urgente - atendimento em até 60 minutos")
    return ("verde","Pouco Urgente - pode aguardar")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/identificacao", methods=["GET", "POST"])
def identificacao():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        data_nascimento = request.form.get("data_nascimento", "").strip()
        sexo = request.form.get("sexo", "").strip()
        acompanhante = request.form.get("acompanhante", "não") == "sim"

        if not nome:
            flash("Por favor, informe o nome do paciente.", "warning")
            return redirect(url_for("identificacao"))
        paciente_id = str(uuid.uuid4())
        paciente = {
            "id": paciente_id,
            "nome": nome,
            "data_nascimento": data_nascimento,
            "sexo": sexo,
            "acompanhante": acompanhante
        }
        pacientes[paciente_id] = paciente
        return redirect(url_for("sintomas", paciente_id=paciente_id))
    return render_template("identificacao.html")

@app.route("/sintomas/<paciente_id>", methods=["GET", "POST"])
def sintomas(paciente_id):
    paciente = pacientes.get(paciente_id)
    if not paciente:
        flash("Paciente não encontrado. Comece novamente.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        sintomas_escolhidos = request.form.getlist("sintomas")
        outros_textos = request.form.get("outros_textos", "").strip()
        paciente["sintomas"] = sintomas_escolhidos
        paciente["outros_textos"] = outros_textos
        return redirect(url_for("perguntas", paciente_id=paciente_id, sintoma_key=sintomas_escolhidos))
    return render_template("sintoma.html", paciente=paciente, sintomas_info=sintomas_info)

@app.route("/perguntas/<paciente_id>/<sintoma_key>", methods=["GET", "POST"])
def perguntas(paciente_id, sintoma_key):
    paciente = pacientes.get(paciente_id)
    if not paciente:
        flash("Paciente não encontrado. Comece novamente.", "danger")
        return redirect(url_for("index"))

    info = sintomas_info.get(sintoma_key)
    if not info:
        flash("Sintoma inválido.", 'danger')
        return redirect(url_for("sintomas", paciente_id=paciente_id))

    perguntas = info.get("perguntas", [])

    if request.method == "POST":
        respostas = {}
        for p in perguntas:
            val = request.form.get(p["id"], "não")
            respostas[p["id"]] = val
        cor, texto = classificar_triagem(sintoma_key, respostas)
        triagem = {
            "id": str(uuid.uuid4())[:8],
            "paciente_id": paciente_id,
            "paciente_nome": paciente["nome"],
            "idade": paciente.get("data_nascimento", ""),
            "sexo": paciente.get("sexo", ""),
            "sintoma": sintoma_key,
            "sintoma_titulo": info.get("titulo"),
            "respostas": respostas,
            "cor": cor,
            "texto": texto,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    ordenadas = list(reversed(triagens))
    return render_template("relatorio.html", triagens=ordenadas)

if __name__ == "__main__":
    app.run(debug=True)