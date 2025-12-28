from ..consultas import ConsultasDelivery


def verificar_usuarios(telefone):
    """Verifica se o usuário existe em empresas, motoboys ou pessoas"""

    fontes = [
        ("empresa", ConsultasDelivery.busca_empresas_numero),
        ("motoboy", ConsultasDelivery.busca_motoboy_numero),
        ("pessoa", ConsultasDelivery.busca_pessoa_numero),
    ]

    for tipo, consulta in fontes:
        usuario = consulta(telefone)
        if usuario:
            return {
                "tipo_usuario": tipo,
                "dados": usuario.to_dict() if hasattr(usuario, "to_dict") else usuario,
            }

    return {"tipo_usuario": "novo"}
