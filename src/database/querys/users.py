"""User Querys"""

from typing import List

from src.database.db_connection import db_connector
from src.database.models import UserDelivery
# from src.blueprints.motoristas.tabelas import Motoristas
from datetime import datetime
# from werkzeug.security import check_password_hash, generate_password_hash


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

    # @classmethod
    # @db_connector
    # def update_password(cls, connection, cpf: int, new_password: str) -> bool:
    #     """Update password for a user."""
    #     user = connection.session.query(User).filter_by(cpf=cpf).first()
    #     if not user:
    #         raise ValueError("Usuário não encontrado.")

    #     # 2) Busca o Motorista pelo CPF do usuário
    #     mot = connection.session.query(Motoristas).filter_by(cpf=user.cpf).first()
    #     if not mot:
    #         raise ValueError("Motorista não encontrado.")

    #     # 3) Atualiza SENHA no User e no Motorista usando set_password
    #     user.password = generate_password_hash(new_password, method="pbkdf2:sha256")
    #     user.alterar_senha = True
    #     mot.password = generate_password_hash(new_password, method="pbkdf2:sha256")
    #     # 4) Persiste no banco
    #     connection.session.commit()
    #     print("Senha atualizada com sucesso.")
    #     return True

    # @classmethod
    # @db_connector
    # def atualiza_mot_flask(cls, connection) -> bool:
    #     session = connection.session
    #     motoristas = session.query(Motoristas).all()

    #     for mot in motoristas:
    #         usuario = session.query(User).filter_by(cpf=mot.cpf).first()

    #         # verifica se senha já está em hash
    #         senha = mot.password
    #         if not senha.startswith("pbkdf2:sha256:"):
    #             senha = generate_password_hash(senha, method="pbkdf2:sha256")

    #         if not usuario:
    #             # cria novo usuário
    #             novo_usuario = User(
    #                 name=mot.nome,  # campo da tabela Motoristas
    #                 cpf=mot.cpf,
    #                 password=senha,
    #                 created_on=datetime.utcnow(),
    #                 last_login=None,
    #                 is_active=True,
    #                 role="motorista",
    #                 alterar_senha=True,
    #             )
    #             session.add(novo_usuario)
    #         else:
    #             # se já existir, atualiza dados básicos
    #             usuario.name = mot.nome
    #             usuario.password = senha  # mantém atualizado
    #             usuario.is_active = True

    #     session.commit()
    #     return True

    @classmethod
    @db_connector
    def entrou_no_sistema(cls, connection, user) -> bool:
        session = connection.session
        db_user = session.get(User, user.id)  # recarrega o user dentro da sessão
        db_user.last_login = datetime.now()
        session.commit()
        return True

    @classmethod
    @db_connector
    def get_by_id(cls, connection, user_id):
        """Get a User by id."""
        return connection.session.query(User).filter_by(id=int(user_id))

    @classmethod
    @db_connector
    def get_by_cpf(cls, connection, cpf) -> List:
        """Select a user by CPF"""
        return connection.session.query(User).filter_by(cpf=cpf).first()

    @classmethod
    @db_connector
    def delivery_busca_cpf(cls, connection, cpf) -> List:
        """Select a user by CPF"""
        return connection.session.query(UserDelivery).filter_by(cpf=cpf).first()

    # @classmethod
    # @db_connector
    # def create(cls, connection, name, cpf, password, role) -> User:
    #     """Create_user"""
    #     user = User(name=name, cpf=cpf, created_on=datetime.now(), role=role)
    #     print(f"Criando usuário: {user}")
    #     user.set_password(password)
    #     connection.session.add(user)
    #     connection.session.commit()
    #     return user

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

    @classmethod
    @db_connector
    def altera_password(cls, connection, user_id, password) -> UserDelivery:
        """Set password for User e Motoristas associado."""
        # 1) Busca o usuário

        user_delivery = (
            connection.session.query(UserDelivery).filter_by(id=user_id).first()
        )

        if not user_delivery:
            raise ValueError("Usuário não encontrado.")
        if user_delivery:
            user_delivery.set_password(password)
            user_delivery.alterar_senha = False
        connection.session.commit()
        return user_delivery
