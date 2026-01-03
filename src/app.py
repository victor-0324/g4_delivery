from flask_login import LoginManager
from flask import Flask

from src.database.models import UserDelivery


def init_app() -> Flask:
    app = Flask(__name__)

    # Configurando o LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        session = db_connection.get_session()  # Obtenha uma sessão de banco de dados
        user = session.query(UserDelivery).get(int(user_id))  # Busque o usuário pela ID
        session.close()  # Feche a sessão
        return user

    # Setando configurações da aplicação
    from .settings import ProductionConfig

    app.config.from_object(ProductionConfig)

    # Configuração do banco de dados
    from .database import Base, DBConnectionHendler

    db_connection = DBConnectionHendler()
    engine = db_connection.get_engine()
    # Criando o contexto da aplicação
    with app.app_context():
        from .blueprints import (
            admin_app,
            auth,
            delivery_app,
            endereco_app,
        )

        app.register_blueprint(delivery_app)
        app.register_blueprint(admin_app)
        app.register_blueprint(auth)
        app.register_blueprint(endereco_app)

        # Criando tabelas no banco de dados
        Base.metadata.create_all(engine)

    return app
