# pylint: disable=too-few-public-methods
"""Configurações para o projeto
Para passar determinadas variaveis e constantes para o sistemas
"""
import os
from dotenv import load_dotenv


class Config:

    LOCAL = os.environ.get("LOCAL")
    load_dotenv(LOCAL)
    DATABASE_CONNECTION = os.environ.get("DATABASE_CONNECTION")
    SECRET_KEY = os.environ.get("SECRET_KEY")


class TestingConfig(Config):
    """Ambiente de testes"""

    DEBUG = False
    TESTING = True


class ProductionConfig(Config):
    """Ambiente de produção"""

    DEBUG = False
