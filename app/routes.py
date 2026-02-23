from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid

from .models import pacientes, triagens
from .services.triagem_service import sintomas_info, classificar_triagem

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/identificacao", methods=["GET", "POST"])
def identificacao():
    if request.method == "POST":
        nome = request.form.get("nome")
        data_nasc = request.form.get("data_nasc")
        sexo = request.form.get("sexo")

        if not nome:
            flash("Informe o nome do paciente.", "warning")
            return redirect(url_for("main.identificacao"))

        paciente_id = str(uuid.uuid4())
        pacientes[paciente_id] = {"nome": nome, "data_nasc": data_nasc, "sexo": sexo}
        return redirect(url_for("main.sintoma", paciente_id=paciente_id))

    return render_template("identificacao.html")

@main.route("/sintoma/<paciente_id>", methods=["GET", "POST"])
def sintoma(paciente_id):
    paciente = pacientes.get(paciente_id)
    if not paciente:
        flash("Pacientes não encontrado. Comece novamente.", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        sintomas_escolhidos = request.form.getlist("sintomas")
        outros_texto = request.form.get("outros_texto", "").strip()

        if not sintomas_escolhidos and not outros_texto:
            flash("Selecione pelo menos um sintoma ou descreva outro.", "warning")
            return redirect(url_for("main.sintoma", paciente_id=paciente_id))

        paciente["sintomas"] = sintomas_escolhidos
        paciente["outros_texto"] = outros_texto
        return redirect(url_for("main.perguntas", paciente_id=paciente_id, sintoma_key="_multi_"))

    return render_template("sintoma.html", paciente=paciente, sintomas_info=sintomas_info)

@main.route("/perguntas/<paciente_id>/<sintoma_key>", methods=["GET", "POST"])
def perguntas(paciente_id, sintoma_key):
    paciente = pacientes.get(paciente_id)
    if not paciente:
        flash("Pacientes não encontrado. Comece novamente.", "danger")
        return redirect(url_for("main.index"))

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
            return redirect(url_for("main.sintoma", paciente_id=paciente_id))

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

        triagem ={
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
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "paciente": {
                "sintomas": sintomas_titulos_lista,
            }
        }
        triagens.append(triagem)
        return redirect(url_for("main.resultado", triagem_id=triagem["id"]))

    return render_template("perguntas.html", paciente=paciente, info=info)

@main.route("/resultado/<triagem_id>")
def resultado(triagem_id):
    triagem = next((t for t in triagens if t["id"] == triagem_id), None)
    if not triagem:
        flash("Triagem não encontrada.", "danger")
        return redirect(url_for("main.index"))
    return render_template("resultado.html", triagem=triagem)

@main.route("/relatorio")
def relatorio():
    return render_template("relatorio.html", triagens=triagens)