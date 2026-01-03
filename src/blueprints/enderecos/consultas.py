from src.database.db_connection import db_connector
from .tabelas import Bairros
import os
import json


class ConsultasEnderecos:
    """Faz as Consultas em Endereços"""

    @staticmethod
    def _load_polygons():
        """Carrega o arquivo poligonos.json apenas na primeira chamada."""
        if ConsultasEnderecos._POLYGONS is None:
            json_path = os.path.join(os.path.dirname(__file__), "poligonos.json")

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            ConsultasEnderecos._POLYGONS = data["polygons"]

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

    @classmethod
    @db_connector
    def registrar_endereco(cls, connection, nome, bairro, lat, lon):
        novo = Enderecos(nome=nome, bairro=bairro, lat=lat, lon=lon)
        """Adiciona um endereço novo ao banco de dados."""
        connection.session.add(novo)
        connection.session.commit()
        connection.session.refresh(novo)

        return novo.to_dict()

    @staticmethod
    def verificar_poligono(lat, lon):
        """
        Retorna o nome do polígono (bairro) onde a coordenada está.
        Se não estiver em nenhum, retorna None.
        """
        ConsultasEnderecos._load_polygons()

        for poly in ConsultasEnderecos._POLYGONS:
            if ConsultasEnderecos._point_in_poly(lat, lon, poly["points"]):
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
