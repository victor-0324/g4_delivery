import json, os, pytz
from sqlalchemy.orm.attributes import flag_modified
from src.database.db_connection import db_connector, db_connector_static
from ..delivery.tabelas import (
    G4DeliveryEmpresas,
    G4DeliveryMotoboy,
    G4DeliveryClientes,
    G4DeliveryContabilizar,
)
from src.database.models.user import UserDelivery
from ..enderecos.google_api import ConsultasGoogleAPI
from ..enderecos.tabelas import Bairros
from decimal import Decimal, InvalidOperation
from datetime import datetime


class ConsultasDelivery:
    """Faz as Consultas para g4 delivery"""

    _POLYGONS = None

    @staticmethod
    def _load_polygons():
        """Carrega o arquivo poligonos.json apenas na primeira chamada."""
        if ConsultasDelivery._POLYGONS is None:
            json_path = os.path.join(os.path.dirname(__file__), "poligonos.json")

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            ConsultasDelivery._POLYGONS = data["polygons"]

    @staticmethod
    def _point_in_poly(lat, lon, points):
        """Algoritmo ray-casting — verifica se o ponto está dentro do polígono."""
        inside = False
        n = len(points)
        j = n - 1

        for i in range(n):
            yi = float(points[i]["lat"])
            yj = float(points[j]["lat"])
            xi = float(points[i]["lng"])
            xj = float(points[j]["lng"])

            intersect = ((yi > lat) != (yj > lat)) and (
                lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi
            )

            if intersect:
                inside = not inside

            j = i

        return inside

    @staticmethod
    def verificar_poligono(lat, lon):
        """
        Retorna o nome do polígono (bairro) onde a coordenada está.
        Se não estiver em nenhum, retorna None.
        """
        ConsultasDelivery._load_polygons()

        for poly in ConsultasDelivery._POLYGONS:
            if ConsultasDelivery._point_in_poly(lat, lon, poly["points"]):
                return poly["name"]

        return None

    @classmethod
    @db_connector
    def verificar_bairro(cls, connection, poligono):
        """retorna bairro pelo nome do poligono"""
        consulta = (
            connection.session.query(Bairros).filter_by(poligono=poligono).first()
        )

        if not consulta:

            return "Desconhecido"

        return consulta.nome

    @classmethod
    @db_connector
    def verificar_valor(cls, connection, bairro):
        consulta = connection.session.query(Bairros).filter_by(poligono=bairro).first()

        if not consulta:
            return None

        tz = pytz.timezone("America/Sao_Paulo")
        agora = datetime.now(tz)
        hora = agora.hour

        if 6 <= hora <= 23:
            return consulta.valor_dia

        return consulta.valor_noite

    @classmethod
    @db_connector
    def user_por_cpf(cls, connection, cpf):
        """Busca usuário pelo CPF"""
        user = connection.session.query(UserDelivery).filter_by(cpf=cpf).first()
        return user.to_dict() if user else None

    @classmethod
    @db_connector
    def ativa_desativa_user(cls, connection, id):
        """Ativa ou desativa um motoboy e o usuário vinculado via CPF"""
        motoboy = connection.session.query(G4DeliveryMotoboy).filter_by(id=id).first()

        if not motoboy:
            return False

        user = connection.session.query(UserDelivery).filter_by(cpf=motoboy.cpf).first()

        if not user:
            return False

        if user.is_active:
            # DESATIVAR
            user.is_active = False
            if not motoboy.telefone.endswith("_"):
                motoboy.telefone = f"{motoboy.telefone}_"
        else:
            # ATIVAR
            user.is_active = True
            motoboy.telefone = motoboy.telefone.rstrip("_")

        connection.session.commit()
        return True

    @classmethod
    @db_connector
    def editar_motoboy(cls, connection, id, **dados):
        motoboy = connection.session.query(G4DeliveryMotoboy).filter_by(id=id).first()

        if not motoboy:
            return False

        for campo, valor in dados.items():
            setattr(motoboy, campo, valor)

        connection.session.commit()
        return True

    # @classmethod
    # @db_connector
    # def deletar_motoboy(cls, connection, id):
    #     """
    #     Deleta um motoboy e o usuário vinculado via CPF
    #     """

    #     motoboy = (
    #         connection.session
    #         .query(G4DeliveryMotoboy)
    #         .filter_by(id=id)
    #         .first()
    #     )

    #     if not motoboy:
    #         return False

    #     usuario = (
    #         connection.session
    #         .query(UserDelivery)
    #         .filter_by(cpf=motoboy.cpf)
    #         .first()
    #     )

    #     if usuario:
    #         connection.session.delete(usuario)

    #     connection.session.delete(motoboy)
    #     connection.session.commit()

    #     return True

    @classmethod
    @db_connector
    def busca_fretes_motoboy(cls, connection, motoboy_id):
        """Busca todos os fretes de um motoboy"""
        fretes = (
            connection.session.query(G4DeliveryContabilizar)
            .filter_by(motoboy_id=motoboy_id)
            .all()
        )
        return [frete.to_dict() for frete in fretes] if fretes else []

    @classmethod
    @db_connector
    def busca_motoboys(cls, connection):
        """Busca todos os motoboys cadastrados"""
        motoboys = connection.session.query(G4DeliveryMotoboy).all()
        return [motoboy.to_dict() for motoboy in motoboys] if motoboys else []

    @classmethod
    @db_connector
    def verifica_usuario(cls, connection, telefone):
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
        """Retira crédito da empresa, permitindo saldo negativo."""
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

        # Debita mesmo que o saldo fique negativo
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
    def cadastrar_motoboy(cls, connection, nome, telefone, cpf, placa, pix):
        """Cadastra um motoboy"""
        motoboy = G4DeliveryMotoboy(
            nome=nome, telefone=telefone, cpf=cpf, placa=placa, pix=pix
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
    def aceitar_frete(cls, connection, telefone, frete_id, id_mensagem):
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
        frete.id_mensagem = id_mensagem
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

    @classmethod
    @db_connector
    def adc_frete(cls, conection, telefone, valor, id_mensagem, via):
        """Contabiliza o valor da corrida para o motoboy"""
        motoboy = ConsultasDelivery.busca_motoboy_numero(telefone)
        motoboy_id = motoboy["id"]
        existente = (
            conection.session.query(G4DeliveryContabilizar)
            .filter_by(id_mensagem=id_mensagem)
            .first()
        )
        if existente:
            return False
        registro = G4DeliveryContabilizar(
            motoboy_id=motoboy_id,
            valor=valor,
            id_mensagem=id_mensagem,
            via=via,
            status="aceito",
        )
        conection.session.add(registro)
        conection.session.commit()
        return True

    @classmethod
    @db_connector
    def excluir_frete(cls, conection, id_mensagem):
        """Remove a corrida contabilizada pelo id_mensagem"""
        corrida = (
            conection.session.query(G4DeliveryContabilizar)
            .filter_by(id_mensagem=id_mensagem)
            .first()
        )

        if corrida:
            conection.session.delete(corrida)
            conection.session.commit()
            return True

        return False

    @classmethod
    @db_connector
    def verifica_motoboys_status(cls, connection):
        """Verifica status dos motoboys no banco de dados"""
        motoboys = connection.session.query(G4DeliveryMotoboy).all()
        return [motoboy.to_dict() for motoboy in motoboys] if motoboys else []

    @classmethod
    @db_connector
    def calcular_rota(
        cls, connection, retirada_lat, retirada_lon, entrega_lat, entrega_lon
    ):
        """Calcula a rota entre dois pontos usando a API do Google Maps"""
        resultado = ConsultasGoogleAPI.comparar_distancias(
            partida_lat=retirada_lat,
            partida_lon=retirada_lon,
            chegada_lat=entrega_lat,
            chegada_lon=entrega_lon,
        )
        return resultado
