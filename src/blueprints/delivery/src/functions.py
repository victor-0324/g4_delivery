from ..consultas import ConsultasDelivery
from datetime import datetime

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


def fila_motoristas():
    """
    Função que retorna a lista dos 10 motoristas livres mais antigos,
    já com endereço e hora formatados.
    """
    livres = ConsultasDelivery().verificar_livres() or []  # Garante que seja uma lista
    fila_ = [
        [
            driver.id,
            driver.nome,
            driver.hora_livre,
        ]
        for driver in livres
    ]

    fila_ = sorted(fila_, key=lambda x: x[2] or datetime.min)  # Ordena pela hora_livre
    fila_ = fila_

    motoristas_info = []
    for motorista in fila_:
        # endereco = LocationIq.busca_endereco(motorista[3], motorista[4])
        motoristas_info.append(
            {
                "nome": motorista[1],
                # "endereco": endereco,
                "hora_livre": motorista[2] if motorista[2] else datetime.now(),
            }
        )

    return motoristas_info
