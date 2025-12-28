"""Configs from database conncetions"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import TestingConfig


class DBConnectionHendler:
    """Sqlalchemy database connection"""

    def __init__(self) -> None:
        self.__connection_string = TestingConfig.DATABASE_CONNECTION
        self.session = None

    def get_engine(self):
        """Return connection engine
        :param - None
        :return - engine_connection
        """
        engine = create_engine(self.__connection_string)
        return engine

    def get_session(self):
        """Return a new session
        :param - None
        :return - database session
        """
        engine = self.get_engine()
        session_maker = sessionmaker(bind=engine)
        return session_maker()


    def __enter__(self):
        engine = create_engine(self.__connection_string)
        session_maker = sessionmaker()
        self.session = session_maker(bind=engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()  # pylint: disable=no-member

def db_connector(func):
    """Fornece uma conexão com o banco de dados usando DBConnectionHendler."""

    def with_connection_(cls, *args, **kwargs):
        with DBConnectionHendler() as connection:
            try:
                return func(cls, connection, *args, **kwargs)
            except:
                connection.session.rollback()
                raise
            finally:
                connection.session.close()

    return with_connection_

def db_connector_static(func):
    def wrapper(*args, **kwargs):
        with DBConnectionHendler() as connection:
            try:
                return func(connection, *args, **kwargs)
            except:
                connection.session.rollback()
                raise
            finally:
                connection.session.close()
    return wrapper
