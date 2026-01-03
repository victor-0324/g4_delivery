import json
from sqlalchemy.orm.attributes import flag_modified
from src.database.db_connection import db_connector, db_connector_static
from ..delivery.tabelas import (
    G4DeliveryEmpresas,
    G4DeliveryMotoboy,
    G4DeliveryClientes,
    G4DeliveryContabilizar,
)
from ..enderecos.google_api import ConsultasGoogleAPI
from decimal import Decimal, InvalidOperation
from datetime import datetime


class ConsultasDelivery:
    """Faz as Consultas para g4 delivery"""

    @classmethod
    @db_connector
    def busca_motoboys(cls, connection):
        """Busca todos os motoboys cadastrados"""
        motoboys = connection.session.query(G4DeliveryMotoboy).all()
        return [motoboy.to_dict() for motoboy in motoboys] if motoboys else []

    @classmethod
    @db_connector
    def verifica_usuario(cls, connection, telefone, tipo):
        """Verifica se o usuário existe no banco de dados"""

        usuario = (
            connection.session.query(G4DeliveryMotoboy)
            .filter_by(telefone=telefone)
            .first()
        )

        usuario = (
            connection.session.query(G4DeliveryEmpresas)
            .filter_by(telefone=telefone)
            .first()
        )

        usuario = (
            connection.session.query(G4DeliveryClientes)
            .filter_by(telefone=telefone)
            .first()
        )

        return usuario.to_dict() if usuario else None

    @classmethod
    @db_connector
    def busca_pedidos_empresa(cls, connection, empresa_id):
        """Busca todos os pedidos de uma empresa"""
        pedidos = (
            connection.session.query(G4DeliveryContabilizar)
            .filter_by(
                telefone=connection.session.query(G4DeliveryEmpresas.telefone)
                .filter_by(id=empresa_id)
                .scalar()
            )
            .all()
        )
        return [pedido.to_dict() for pedido in pedidos] if pedidos else []

    @classmethod
    @db_connector
    def atualizar_empresa(cls, connection, id, nome, telefone, endereco, credito):
        """Atualiza os dados de uma empresa parceira."""
        empresa = connection.session.query(G4DeliveryEmpresas).filter_by(id=id).first()
        if not empresa:
            return None

        empresa.nome = nome
        empresa.telefone = telefone
        empresa.endereco = endereco
        empresa.credito = credito

        connection.session.commit()
        return empresa.to_dict()

    @classmethod
    @db_connector
    def retirar_credito_empresa(cls, connection, telefone, valor):
        """Retira crédito da empresa, sem permitir saldo negativo."""
        empresa = (
            connection.session.query(G4DeliveryEmpresas)
            .filter_by(telefone=telefone)
            .first()
        )
        if not empresa:
            return None

        try:
            valor = Decimal(valor)
        except InvalidOperation:
            return {"erro": "Valor inválido"}

        if valor <= 0:
            return {"erro": "O valor deve ser maior que zero"}

        # Verificar saldo
        if empresa.credito < valor:
            return {"erro": "Saldo insuficiente"}

        empresa.credito -= valor
        connection.session.commit()

        return empresa.to_dict()

    @classmethod
    @db_connector
    def busca_todas_empras(cls, connection):
        """Busca todas as empresas cadastradas"""
        empresas = connection.session.query(G4DeliveryEmpresas).all()
        return [empresa.to_dict() for empresa in empresas] if empresas else []

    @classmethod
    @db_connector
    def busca_empresas(cls, connection, nome):
        """Busca empresas cadastradas"""
        empresas = (
            connection.session.query(G4DeliveryEmpresas).filter_by(nome=nome).first()
        )
        return empresas.to_dict() if empresas else None

    @classmethod
    @db_connector
    def buscar_por_cpf(cls, connection, cpf):
        """Busca motoboy pelo cpf"""
        motoboy = connection.session.query(G4DeliveryMotoboy).filter_by(cpf=cpf).first()

        return motoboy.to_dict() if motoboy else None

    @classmethod
    @db_connector
    def busca_motoboy_numero(cls, connection, telefone):
        """Busca motoboy pelo numero de telefone"""
        motoboy = (
            connection.session.query(G4DeliveryMotoboy)
            .filter_by(telefone=telefone)
            .first()
        )
        return motoboy.to_dict() if motoboy else None

    @classmethod
    @db_connector
    def busca_empresas_numero(cls, connection, telefone):
        """Busca empresa pelo numero de telefone"""
        empresa = (
            connection.session.query(G4DeliveryEmpresas)
            .filter_by(telefone=telefone)
            .first()
        )
        return empresa.to_dict() if empresa else None

    @classmethod
    @db_connector
    def busca_pessoa_numero(cls, connection, telefone):
        """Busca pessoa pelo numero de telefone"""
        cliente = (
            connection.session.query(G4DeliveryClientes)
            .filter_by(telefone=telefone)
            .first()
        )
        return cliente.to_dict() if cliente else None

    @classmethod
    @db_connector
    def cadastrar_empresa(cls, connection, nome, telefone, endereco, lat, lon):
        """Cadastra uma empresa parceira"""
        empresa = G4DeliveryEmpresas(
            nome=nome, telefone=telefone, endereco=endereco, lat=lat, lon=lon
        )

        connection.session.add(empresa)
        connection.session.commit()
        return empresa.to_dict() if empresa else None

    @classmethod
    @db_connector
    def cadastrar_motoboy(cls, connection, nome, telefone, cpf, placa):
        """Cadastra um motoboy"""
        motoboy = G4DeliveryMotoboy(
            nome=nome,
            telefone=telefone,
            cpf=cpf,
            placa=placa,
        )

        connection.session.add(motoboy)
        connection.session.commit()
        return motoboy.to_dict() if motoboy else None

    @classmethod
    @db_connector
    def cadastrar_cliente(cls, connection, nome, telefone, status):
        """Cadastra um cliente"""
        cliente = G4DeliveryClientes(nome=nome, telefone=telefone, status=status)

        connection.session.add(cliente)
        connection.session.commit()
        return cliente.to_dict() if cliente else None

    @classmethod
    @db_connector
    def verificar_livres(cls, connection):
        """Retorna todos os motoboys com status livre, ou None se não houver"""

        livres = (
            connection.session.query(G4DeliveryMotoboy)
            .filter(G4DeliveryMotoboy.status == "livre")
            .all()
        )

        return livres if livres else None

    @classmethod
    @db_connector
    def Contabilizar(
        cls,
        connection,
        telefone,
        valor,
        retirada_lat,
        retirada_lon,
        entrega_lat,
        entrega_lon,
        usuario,
        via,
        status="pendente",
    ):
        """Contabiliza o valor da entrega para o motoboy"""
        valor_decimal = Decimal(str(valor).replace(",", "."))
        if usuario == "pessoa":
            registro = G4DeliveryContabilizar(
                telefone=telefone,
                valor=float(valor_decimal),
                retirada_lat=str(retirada_lat),
                retirada_lon=str(retirada_lon),
                entrega_lat=str(entrega_lat),
                entrega_lon=str(entrega_lon),
                via=via,
                status=status,
                hora_pedido=datetime.now(),
            )

            connection.session.add(registro)
            connection.session.commit()
            return registro.id

        registro = G4DeliveryContabilizar(
            telefone=telefone,
            valor=float(valor_decimal),
            retirada_lat=str(retirada_lat),
            retirada_lon=str(retirada_lon),
            entrega_lat=str(entrega_lat),
            entrega_lon=str(entrega_lon),
            empresa_id=usuario,
            via=via,
            status=status,
            hora_pedido=datetime.now(),
        )

        connection.session.add(registro)
        connection.session.commit()
        return registro.id

    @classmethod
    @db_connector
    def buscar_motoboy_frete(cls, connection, frete_id):
        """Busca o motoboy livre mais próximo"""

        frete = (
            connection.session.query(G4DeliveryContabilizar)
            .filter_by(id=frete_id)
            .first()
        )

        livres = ConsultasDelivery.verificar_livres()
        if not livres:
            return None

        recusou = ConsultasDelivery.verificar_recusados(frete)

        motoboy_mais_proximo = None
        menor_distancia = float("inf")

        for m in livres:
            if m.telefone in recusou:
                continue

            resultado = ConsultasGoogleAPI.comparar_distancias(
                partida_lat=m.lat,
                partida_lon=m.lon,
                chegada_lat=frete.retirada_lat,
                chegada_lon=frete.retirada_lon,
            )

            if not resultado:
                continue

            distancia = resultado["distancia"]

            if distancia < menor_distancia:
                menor_distancia = distancia
                motoboy_mais_proximo = m

        return motoboy_mais_proximo.to_dict() if motoboy_mais_proximo else None

    @classmethod
    @db_connector
    def aceitar_frete(cls, connection, telefone, frete_id):
        """Motoboy aceita o frete"""

        motoboy = (
            connection.session.query(G4DeliveryMotoboy)
            .filter_by(telefone=telefone)
            .first()
        )

        if not motoboy:
            return None

        frete = (
            connection.session.query(G4DeliveryContabilizar)
            .filter_by(id=frete_id)
            .first()
        )

        if not frete:
            return None

        frete.motoboy_id = motoboy.id
        frete.status = "aceito"
        frete.hora_aceite = datetime.now()

        motoboy.status = "ocupado"
        motoboy.id_pedido = frete_id

        connection.session.commit()

        return frete.to_dict() if frete else None

    @classmethod
    @db_connector
    def recusar_frete(cls, connection, telefone, frete_id):
        """Motoboy recusa um frete"""

        frete = (
            connection.session.query(G4DeliveryContabilizar)
            .filter_by(id=frete_id)
            .first()
        )

        motoboy = (
            connection.session.query(G4DeliveryMotoboy)
            .filter_by(telefone=telefone)
            .first()
        )

        if not frete:
            return "Erro: Frete não encontrado", 404

        if not motoboy:
            return "Erro: Motoboy não encontrado", 404

        if frete.recusou is None:
            frete.recusou = []

        if telefone not in frete.recusou:
            frete.recusou.append(telefone)

            motoboy.status = "livre"
            motoboy.id_pedido = None

            frete.motoboy_id = None
            frete.status = "pendente"
            flag_modified(frete, "recusou")

            connection.session.commit()

        return frete

    @classmethod
    @db_connector
    def passar_frete(cls, connection, frete_id):
        """Procura outro motoboy para o frete"""

        frete = (
            connection.session.query(G4DeliveryContabilizar)
            .filter_by(id=frete_id)
            .first()
        )

        motoboy = ConsultasDelivery.buscar_motoboy_frete(frete_id)

        return motoboy

    @classmethod
    def verificar_recusados(cls, frete):
        """Retorna a lista de telefones que recusaram o frete."""
        r = frete.recusou

        if r is None:
            return []

        if isinstance(r, str):
            try:
                return json.loads(r)
            except json.JSONDecodeError:
                return []

        if isinstance(r, list):
            return r

        return []

    @classmethod
    @db_connector
    def coloca_livre(cls, connection, telefone, lat, lon):
        """Atualiza o status do motoboy para livre e salva a nova localização"""

        motoboy = (
            connection.session.query(G4DeliveryMotoboy)
            .filter_by(telefone=telefone)
            .first()
        )

        if not motoboy:
            print(f"Motoboy com telefone {telefone} não encontrado.")
            return False

        # Se ele estava off ou em entrega, marcar como livre
        if motoboy.status in ["off", "ocupado"]:
            motoboy.status = "livre"
            motoboy.hora_livre = datetime.now()
            motoboy.duracao_entrega = ""
            motoboy.inicio_entrega = None
            motoboy.destino = ""
            motoboy.lat = lat
            motoboy.lon = lon
            motoboy.id_pedido = None
            connection.session.commit()
        else:
            # Se já está livre, apenas atualiza a localização
            motoboy.status = "livre"
            motoboy.duracao_entrega = ""
            motoboy.inicio_entrega = None
            motoboy.destino = ""
            motoboy.lat = lat
            motoboy.lon = lon
            motoboy.id_pedido = None
            connection.session.commit()

        return True

    @classmethod
    @db_connector
    def atualizar_status(cls, connection, telefone, status):

        motorista = (
            connection.session.query(G4DeliveryMotoboy)
            .filter_by(telefone=telefone)
            .first()
        )
        motorista.status = status
        connection.session.commit()
