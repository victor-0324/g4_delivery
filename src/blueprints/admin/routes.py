from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
    flash,
)

from ..delivery.consultas import ConsultasDelivery
from flask_login import login_required


admin_app = Blueprint("admin_app", __name__, url_prefix="/admin/")


def public_endpoint(function):
    """Decorator for public routes"""
    function.is_public = True
    return function


@login_required
@admin_app.route("/motoboys", methods=["GET", "POST"])
def motoboys():
    """Render the delivery admin page for the web application."""

    user = session.get("user")
    if not user or user.get("role") != "admin":
        return redirect(url_for("auth.login"))

    moto_boy = ConsultasDelivery.busca_motoboys()
    # print(f"Empresas encontradas: {empresas}")
    return render_template("deshboards/motoboy.html", user=user, moto_boy=moto_boy)


@login_required
@admin_app.route("/delivery", methods=["GET", "POST"])
def delivery():
    """Render the delivery admin page for the web application."""
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        empresa_id = request.form.get("empresa_id")
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        endereco = request.form.get("endereco")
        credito = request.form.get("credito")

        print(
            f"Atualizando empresa: id={empresa_id}, nome={nome}, telefone={telefone}, endereco={endereco}, credito={credito}"
        )

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
    # print(f"Empresas encontradas: {empresas}")
    return render_template("pages/delivery/admin.html", user=user, empresas=empresas)


