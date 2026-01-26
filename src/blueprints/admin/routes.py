from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
    flash,
    jsonify,
)
from datetime import datetime, time
from ..delivery.consultas import ConsultasDelivery
from .consultas import ConsultaDados
from flask_login import login_required
from ..delivery.src.functions import fila_motoristas

admin_app = Blueprint("admin_app", __name__, url_prefix="/admin/")


def public_endpoint(function):
    """Decorator for public routes"""
    function.is_public = True
    return function

@login_required
@admin_app.route("/desativar", methods=["POST"])
def desativar_user():
    """Desativa um motorista com base no ID fornecido."""
    user = session.get("user")
    if not user or user.get("role") != "admin_delivery":
        return jsonify({"error": "Acesso não autorizado."}), 403

    id = request.form.get("id")

    ConsultaDados.ativa_desativa_user(id)

    return redirect(url_for("admin_app.motoboys"))

@login_required
@admin_app.route("/desativar/empresa", methods=["POST"])
def desativar_empresa():
    """Desativa uma empresa com base no ID fornecido."""
    user = session.get("user")
    if not user or user.get("role") != "admin_delivery":
        return jsonify({"error": "Acesso não autorizado."}), 403

    id = request.form.get("id")

    ConsultaDados.ativa_desativa_empresa(id)

    return redirect(url_for("admin_app.delivery"))

@admin_app.route("/consulta/status")
def consulta_is_active():
    cpf = request.args.get("cpf")
    empresa = request.args.get("nome")

    if cpf:
        user = ConsultasDelivery.user_por_cpf(cpf)
        print(f"Usuário encontrado: {user}")
        if not user:
            return jsonify({"exists": False})

        return jsonify({
            "exists": True,
            "is_active": user['is_active']
        })

    elif empresa:
        user = ConsultaDados.empresa_por_nome(empresa)

        if not user:
            return jsonify({"exists": False})

        return jsonify({
            "exists": True,
            "is_active": user['is_active']
        })

    return jsonify({"error": "Parâmetros insuficientes."}), 400

@login_required
@admin_app.route("/motoboys", methods=["GET"])
def motoboys():
    """Render the delivery admin page for the web application."""

    user = session.get("user")
    if not user or user.get("role") != "admin_delivery":
        return redirect(url_for("auth.login"))

    moto_boy = ConsultasDelivery.busca_motoboys()

    return render_template("deshboards/motoboy.html", user=user, moto_boy=moto_boy)

@login_required
@admin_app.route("/editar_motoboy", methods=["POST"])
def editar_motoboy():
    user = session.get("user")
    print(f"Usuário na sessão: {user}")

    if not user or user.get("role") != "admin_delivery":
        return redirect(url_for("auth.login"))

    id = request.form.get("id")
    print(f"Editando motoboy com id: {id}")
    if not id:
        return redirect(url_for("admin_app.motoboys"))

    dados = {
        "nome": request.form.get("nome"),
        "telefone": request.form.get("telefone"),
        "cpf": request.form.get("cpf"),
        "placa": request.form.get("placa"),
        "status": request.form.get("status"),
    }

    # remove campos vazios
    dados = {k: v for k, v in dados.items() if v}

    ConsultasDelivery.editar_motoboy(id=id, **dados)

    return redirect(url_for("admin_app.motoboys"))


@login_required
@admin_app.route("/delivery", methods=["GET", "POST"])
def delivery():
    """Render the delivery admin page for the web application."""
    user = session.get("user")
    if not user or user.get("role") != "admin_delivery":
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        empresa_id = request.form.get("empresa_id")
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        endereco = request.form.get("endereco")
        credito = request.form.get("credito")

        if not all([empresa_id, nome, telefone, endereco, credito]):
            flash("Dados incompletos para atualizar a empresa.", "danger")
            return redirect(url_for("admin_app.delivery"))

        try:
            credito = float(credito)
            sucesso = ConsultasDelivery.atualizar_empresa(
                empresa_id, nome, telefone, endereco, credito
            )
            if sucesso:
                flash("Empresa atualizada com sucesso!", "success")
            else:
                flash(
                    "Erro ao atualizar a empresa. Verifique os dados e tente novamente.",
                    "danger",
                )
        except ValueError:
            flash("Valor de crédito inválido.", "danger")

        return redirect(url_for("admin_app.delivery"))

    empresas = ConsultasDelivery.busca_todas_empras()
    fila = fila_motoristas()

    return render_template("pages/delivery/admin.html", user=user, empresas=empresas, fila=fila)

@login_required
@admin_app.route("/pagamento/<int:empresa_id>", methods=["GET"])
def pagamento(empresa_id):
    """Render the payment page for a specific company."""
    user = session.get("user")
    if not user or user.get("role") != "admin_delivery":
        return redirect(url_for("auth.login"))

    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    if data_inicio:
        data_inicio = datetime.combine(
            datetime.strptime(data_inicio, "%Y-%m-%d").date(),
            time.min  # 00:00:00
        )

    if data_fim:
        data_fim = datetime.combine(
            datetime.strptime(data_fim, "%Y-%m-%d").date(),
            time.max  # 23:59:59.999999
        )

    empresa = ConsultaDados.empresa_por_id(empresa_id)
    pagamentos_raw = ConsultasDelivery.busca_pedidos_empresa(
        empresa_id=empresa_id,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    pagamentos = []
    for p in pagamentos_raw:
        pagamentos.append({
            "data": p["hora_pedido"].strftime("%d/%m/%Y"),
            "endereco": p["endereco_entrega"],
            "status": p["status"],
            "valor": f"R$ {float(p['valor']):.2f}".replace(".", ","),
            "motoboy": p.get("motoboy_nome", "—")
        })

    if not empresa:
        flash("Empresa não encontrada.", "danger")
        return redirect(url_for("admin_app.delivery"))

    return render_template("pages/delivery/pagamento.html", user=user, empresa=empresa, pagamentos=pagamentos)
