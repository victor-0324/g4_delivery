# pylint: disable=no-value-for-parameter
"""Routes for user authentication."""
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
    flash,
)

from flask_login import login_user, logout_user, current_user, login_required
from src.database.querys import UserQuerys

auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static",
)


def public_endpoint(function):
    """Decoretor for public routes"""
    function.is_public = True
    return function


@current_app.before_request
def check_valid_login():
    """Check if user have a valid login."""
    login_valid = "_user_id" in session  # or whatever you use to check valid login
    rules = (
        request.endpoint
        and "static" not in request.endpoint
        and not login_valid
        and not getattr(
            current_app.view_functions[request.endpoint], "is_public", False
        )
    )

    match rules:
        case True:
            return redirect(url_for("auth.login"))


@public_endpoint
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form.get("login")
        password = request.form.get("password")

        print(f"Login informado: {login_input}")

        user = UserQuerys.delivery_busca_email_ou_cpf(login_input)

        print(f"Usuário encontrado: {user.name if user else 'Nenhum'}")

        if not user or not user.check_password(password):
            flash("Credenciais inválidas.", "danger")
            return redirect(url_for("auth.login"))

        # Autentica
        login_user(user)
        session["user"] = user.to_dict()

        # Redireciona conforme role
        if user.alterar_senha:
            return redirect(url_for("auth.altera_password"))

        # Fluxos bem definidos
        if user.role == "admin_delivery":
            return redirect(url_for("admin_app.delivery"))
        elif user.role == "motoboy":
            return redirect(url_for("delivery_app.entregadores"))
        elif user.role == "empresa_delivery":
            return redirect(url_for("delivery_app.painel_empresa"))
        else:
            flash("Tipo de usuário desconhecido.", "danger")
            return redirect(url_for("auth.login"))

    return render_template("pages/delivery/login_delivery.html")


@login_required
@auth.route("/create_user", methods=["POST"])
def create_user():
    """Register new user."""

    name = request.form.get("name")
    cpf = request.form.get("cpf")
    password = request.form.get("password")
    role = request.form.get("role")
    if not UserQuerys.get_by_cpf(cpf):
        UserQuerys.create(name, cpf, password, role)

    return jsonify({"response": name}), 200


@login_required
@auth.route("/logout", methods=["GET", "POST"])
def logout():
    """Logout user."""
    logout_user()
    session.pop("user", None)
    return redirect(url_for("auth.login"))


@auth.route("/", methods=["GET", "POST"])
def inicio():
    """ """
    print("Início")
    return redirect(url_for("auth.login"))


@login_required
@auth.route("/altera_password", methods=["GET", "POST"])
def altera_password():
    """Altera a senha do usuário."""
    session_user = session.get("user")
    print(f"Usuário na sessão: {session_user}")
    user = UserQuerys.delivery_busca_cpf(session_user["cpf"])
    if not user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nova_senha = request.form["new_password"]
        confirma_senha = request.form["confirm_password"]

        if nova_senha != confirma_senha:
            flash("Senhas não coincidem.", "danger")
            return redirect(url_for("auth.altera_password"))

        try:
            UserQuerys.altera_password(user.id, nova_senha)
            flash("Senha atualizada com sucesso.", "success")
            return redirect(url_for("auth.login"))
        except ValueError as e:
            flash(str(e))
        return redirect(url_for("auth.altera_password"))

    return render_template("pages/delivery/altera_password.html", user=user)
