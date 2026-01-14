from src.database.db_connection import db_connector
from ..delivery.tabelas import (
    G4DeliveryEmpresas,
    G4DeliveryMotoboy,
)
from src.database.models.user import UserDelivery


class ConsultaDados:


    @classmethod
    @db_connector
    def empresa_por_nome(cls, connection, nome):
        """Retorna os dados de uma empresa pelo nome."""
        empresa = connection.session.query(UserDelivery).filter_by(name=nome).first()
        return empresa.to_dict() if empresa else None

    @classmethod
    @db_connector
    def ativa_desativa_empresa(cls, connection, id):
        """Ativa ou desativa um empresa e o usuário vinculado via CPF"""
        empresa = connection.session.query(G4DeliveryEmpresas).filter_by(id=id).first()

        if not empresa:
            return False

        user = connection.session.query(UserDelivery).filter_by(name=empresa.nome).first()

        if not user:
            return False

        if user.is_active:
            # DESATIVAR
            user.is_active = False
            if not empresa.telefone.endswith("_"):
                empresa.telefone = f"{empresa.telefone}_"
                empresa.status = "desativado"
        else:
            # ATIVAR
            user.is_active = True
            empresa.telefone = empresa.telefone.rstrip("_")
            empresa.status = "ativo"

        connection.session.commit()
        return True

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
                motoboy.status = "off"
        else:
            # ATIVAR
            user.is_active = True
            motoboy.telefone = motoboy.telefone.rstrip("_")

        connection.session.commit()
        return True
