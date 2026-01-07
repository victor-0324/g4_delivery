from flask import (
    Blueprint,
    render_template,
    session,
    jsonify,
    request,
    redirect,
    url_for,
    flash,
)
import requests
from flask_login import login_required, login_user
from ..delivery.consultas import ConsultasDelivery
from .src.functions import fila_motoristas
# from ..enderecos.google_api import ConsultasGoogleAPI
from src.database.querys import UserQuerys
from .src.functions import verificar_usuarios

delivery_app = Blueprint(
    "delivery_app",
    __name__,
    url_prefix="/g4delivery/",
    template_folder="templates",
    static_folder="static",
)


def public_endpoint(function):
    """Decorator for public routes"""
    function.is_public = True
    return function

@login_required
@delivery_app.route("/", methods=["GET"])
def painel_empresa():
    """panel das empresas"""
    user = session.get("user")
    if user["role"] != "empresa_delivery":
        return redirect(url_for("auth.login"))

    empresa = ConsultasDelivery.busca_empresas(user["nome"])

    todos_pedidos = ConsultasDelivery.busca_pedidos_empresa(empresa["id"])

    return render_template(
        "pages/delivery/painel_empresa.html",
        user=user,
        pedidos=todos_pedidos,
        empresa=empresa,
    )


@delivery_app.route("/gerar_pix")
def gerar_pix():
    """Gera um pix para o pedido."""
    url = "https://api-sandbox.asaas.com/v3/pix/addressKeys"

    payload = {"type": "EVP"}
    headers = {"accept": "application/json", "content-type": "application/json"}

    response = request.post(url, json=payload, headers=headers)

    print(response.text)

    return render_template("pages/delivery/gerar_pix.html")


@login_required
@delivery_app.route("/entregadores", methods=["GET"])
def entregadores():
    user = session.get("user")

    if not user or user.get("role") != "motoboy":
        return redirect(url_for("auth.login"))

    motoboy = ConsultasDelivery.buscar_por_cpf(user["cpf"])
    fretes = ConsultasDelivery.busca_fretes_motoboy(motoboy["id"])
    fila = fila_motoristas()
    print("fila:", fila)
    corridas = []
    receita_bruta = 0.0

    for f in fretes:
        valor = float(f.get("valor", 0))
        receita_bruta += valor

        corridas.append({
            "id": f.get("id"),
            "valor": valor,
            "data_hora": f.get("hora_aceite") or f.get("hora_pedido"),
            "via": f.get("via"),
            "status": f.get("status"),
        })

    total_corridas = len(corridas)

    percentual_comissao = 0.10  # 10%
    comissao = receita_bruta * percentual_comissao
    receita_liquida = receita_bruta - comissao

    return render_template(
        "pages/delivery/entregadores.html",
        user=user,
        corridas=corridas,
        total_corridas=total_corridas,
        receita_bruta=receita_bruta,
        comissao=comissao,
        receita_liquida=receita_liquida,
        fila=fila,
    )


@public_endpoint
@delivery_app.route("/verificar_numero", methods=["POST"])
def verificar_usuario():
    """verifica o tipo de usuario que está mandando mensagem."""
    data = request.get_json()
    telefone = data.get("telefone")
    usuario = verificar_usuarios(telefone)
    return jsonify(usuario)


@login_required
@delivery_app.route("/cadastrar_empresa", methods=["GET", "POST"])
def cadastrar_empresa():
    """cadastra empresa no banco de dados."""
    user = session.get("user")

    if request.method == "POST":
        data = request.form
        print(data)
        nome = data.get("nome")
        email = data.get("email")
        telefone = data.get("telefone")
        endereco = data.get("endereco")
        password = "Empres@-senhag4"
        cpf = None
        role = "empresa_delivery"

        # Validação básica
        if not nome or not telefone or not endereco:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return redirect(request.url)

        try:
            # lat, lon = ConsultasGoogleAPI.lat_lon(endereco)
            # Cria o usuário
            UserQuerys.create_user_delivery(nome, email, cpf, password, role)
            # Registra na tabela própria
            # ConsultasDelivery.cadastrar_empresa(nome, telefone, endereco, lat, lon)
            flash("Empresa cadastrada com sucesso!", "success")
            return redirect(url_for("delivery_app.painel_empresa"))

        except Exception as e:
            print("🔥 ERRO AO CADASTRAR:", e)
            flash("Erro ao cadastrar. Verifique os dados.", "danger")
            return redirect(request.url)

    return render_template("pages/delivery/cadastrar_empresa.html", user=user)


@login_required
@delivery_app.route("/cadastrar_motoboy", methods=["GET", "POST"])
def cadastrar_motoboy():
    """cadastra motoboy no banco de dados."""
    user = session.get("user")

    if request.method == "POST":
        data = request.form
        print(data)
        nome = data.get("nome")
        telefone = data.get("telefone")
        cpf = data.get("CPF")
        placa = data.get("placa")
        password = "Mot0r!stA-senha"
        role = data.get("role")
        email = None

        # Validação básica
        if not nome or not cpf or not telefone:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return redirect(request.url)

        # Valida CPF tamanho (exemplo)
        if len(cpf.replace(".", "").replace("-", "")) != 11:
            flash("CPF inválido.", "danger")
            return redirect(request.url)

        try:
            # Cria o usuário
            UserQuerys.create_user_delivery(nome, email, cpf, password, role)

            # Se for motoboy, registra na tabela própria
            if role == "motoboy":
                ConsultasDelivery.cadastrar_motoboy(nome, telefone, cpf, placa)
                flash("Motoboy cadastrado com sucesso!", "success")
                return redirect(url_for("delivery_app.cadastrar_motoboy"))

            elif role == "admin_delivery":
                flash("Administrador criado com sucesso!", "success")
                return redirect(url_for("delivery_app.cadastrar_empresa"))

            else:
                flash("Tipo de usuário inválido.", "warning")
                return redirect(request.url)

        except Exception as e:
            print("🔥 ERRO AO CADASTRAR:", e)
            flash("Erro ao cadastrar. Verifique os dados.", "danger")
            return redirect(request.url)

    return render_template("pages/delivery/cadastrar_motoboy.html", user=user)


@public_endpoint
@delivery_app.route("/cadastrar_cliente", methods=["POST"])
def cadastrar_cliente():
    """Cadastra um cliente no banco de dados"""
    data = request.get_json()
    telefone = data.get("telefone")
    nome = data.get("nome")
    status = "pedindo"
    cliente = ConsultasDelivery.cadastrar_cliente(nome, telefone, status)
    return jsonify(cliente)


@public_endpoint
@delivery_app.route("/pedir_frete", methods=["POST"])
def pedir_frete():
    """Pedir um frete."""

    data = request.get_json()
    telefone = data.get("telefone")
    valor = data.get("valor")
    retirada_lat = data.get("retirada_lat")
    retirada_lon = data.get("retirada_lon")
    entrega_lat = data.get("entrega_lat")
    entrega_lon = data.get("entrega_lon")
    usuario = data.get("usuario")
    via = "WhatsApp"

    frete_id = ConsultasDelivery.Contabilizar(telefone, valor, retirada_lat, retirada_lon, entrega_lat, entrega_lon, usuario, via)

    motoboy = ConsultasDelivery.buscar_motoboy_frete(frete_id)

    if motoboy is None:
        return jsonify({"mensagem": "Nenhum motoboy livre no momento."}), 200

    return jsonify({"motoboy": motoboy, "frete_id": frete_id})


@public_endpoint
@delivery_app.route("/aceitar_frete", methods=["POST"])
def aceitar_frete():
    """Aceitar um frete."""

    data = request.get_json()
    telefone = data.get("telefone")
    frete_id = data.get("frete_id")
    print(data)
    frete = ConsultasDelivery.aceitar_frete(telefone, frete_id)
    if not frete:
        return jsonify({"erro": "Frete não encontrado"}), 400

    frete_telefone = frete["telefone"]
    usuario = verificar_usuarios(frete_telefone)
    print(f"Usuário associado ao frete: {usuario}")
    if usuario["tipo_usuario"] == "empresa":
        empresa = ConsultasDelivery.retirar_credito_empresa(
            telefone=frete["telefone"], valor=frete["valor"]
        )
        if isinstance(empresa, dict) and empresa.get("erro"):
            return jsonify({"erro": empresa["erro"]}), 400

        return jsonify({"sucesso": True, "usuario": empresa})
    return jsonify({"sucesso": True, "usuario": usuario})


@public_endpoint
@delivery_app.route("/recusar_frete", methods=["POST"])
def recusar_frete():
    data = request.get_json()
    telefone = data.get("telefone")
    frete_id = data.get("frete_id")
    ConsultasDelivery.recusar_frete(telefone, frete_id)
    motoboy = ConsultasDelivery.passar_frete(frete_id)

    if motoboy is None:
        return jsonify({"mensagem": "Nenhum motoboy livre no momento."}), 200

    return jsonify({"motoboy": motoboy, "frete_id": frete_id})


@public_endpoint
@delivery_app.route("/colocar_livre", methods=["POST"])
def colocar_livre():
    data = request.get_json()
    telefone = data.get("telefone")
    lat = data.get("lat")
    lon = data.get("lon")
    ConsultasDelivery.coloca_livre(telefone, lat, lon)

    return jsonify({"sucesso": "sucesso"})


@public_endpoint
@delivery_app.route("/atualizar_status", methods=["POST"])
def atualizar_status():
    data_json = request.get_json()
    telefone = data_json.get("telefone")
    status = data_json.get("status")
    ConsultasDelivery.atualizar_status(telefone, status)
    return jsonify({"response": "Status atualizado com sucesso"}), 200


@public_endpoint
@delivery_app.route("/contabilizar", methods=["POST"])
def contabilizar():
    data_json = request.get_json()
    motorista = data_json.get("telefone")
    valor = data_json.get("valor")
    id_mensagem = data_json.get("id_mensagem")
    via = "WhatsApp"
    ConsultasDelivery.adc_frete(motorista, valor, id_mensagem, via)

    return jsonify({"response": "Contabilizado com sucesso"}), 200


@public_endpoint
@delivery_app.route("/descontabilizar", methods=["POST"])
def descontabilizar():
    data_json = request.get_json()
    id_mensagem = data_json.get("id_mensagem")
    ConsultasDelivery.excluir_frete(id_mensagem)
    return jsonify({"response": "descontabilizado com sucesso"}), 200


@public_endpoint
@delivery_app.route("/verificar_livre", methods=["GET"])
def verificar_livre():
    """Verifica se há motoboys livres, ocupados ou todos off."""
    motoboys = ConsultasDelivery.verifica_motoboys_status()

    if not motoboys:
        return jsonify({"status": "Off"})

    total = len(motoboys)
    off = sum(1 for m in motoboys if m["status"] == "off")
    livres = sum(1 for m in motoboys if m["status"] == "livre")

    if off == total:
        return jsonify({"status": "Off"})

    if livres > 0:
        return jsonify({"status": "Livre"})

    return jsonify({"status": "Ocupado"})
