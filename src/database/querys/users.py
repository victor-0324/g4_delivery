"""User Querys"""

from typing import List

from src.database.db_connection import db_connector
from src.database.models import UserDelivery
from datetime import datetime
from werkzeug.security import  generate_password_hash


class UserQuerys:
    """querys from users"""

    @classmethod
    @db_connector
    def delivery_busca_email_ou_cpf(cls, connection, login_input) -> List:
        """Seleciona o usuario com  email or CPF"""
        return (
            connection.session.query(UserDelivery)
            .filter(
                (UserDelivery.email == login_input) | (UserDelivery.cpf == login_input)
            )
            .first()
        )


    @classmethod
    @db_connector
    def entrou_no_sistema(cls, connection, user) -> bool:
        session = connection.session
        db_user = session.get(UserDelivery, user.id)  # recarrega o user dentro da sessão
        db_user.last_login = datetime.now()
        session.commit()
        return True


    @classmethod
    @db_connector
    def delivery_busca_cpf(cls, connection, cpf) -> List:
        """Select a user by CPF"""
        return connection.session.query(UserDelivery).filter_by(cpf=cpf).first()


    @classmethod
    @db_connector
    def create_user_delivery(cls, connection, name, email, cpf, password, role) -> UserDelivery:
        """Create_user"""
        user = UserDelivery(name=name, email=email, cpf=cpf, created_on=datetime.now(), role=role)
        print(f"Criando usuário: {user}")
        user.set_password(password)
        connection.session.add(user)
        connection.session.commit()
        return user


