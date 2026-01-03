import requests
import re
from src.settings import TestingConfig
import urllib.parse
from .consultas import ConsultasEnderecos

# from ..corridas.consultas import ConsultasEnderecos
# from ..enderecos.tabelas import Enderecos
from src.database.db_connection import db_connector, db_connector_static


class ConsultasGoogleAPI:
    """Classe para consultas relacionadas à API do Google Maps."""

    # @db_connector
    # @classmethod
    # def busca_endereco(cls, connection, latitude, longitude):
    #     """Busca o endereço por latitude e longitude"""

    #     existence = (
    #         connection.session.query(Enderecos)
    #         .filter(Enderecos.lat == str(latitude), Enderecos.lon == str(longitude))
    #         .first()
    #     )

    #     if existence:
    #         return existence.nome

    #     response = requests.get(
    #         f"https://maps.googleapis.com/maps/api/geocode/json"
    #         f"?latlng={latitude},{longitude}&key={TestingConfig.GOOGLE_API}"
    #     )

    #     if response.status_code != 200:
    #         return {
    #             "erro": "Não foi possível obter os dados da API.",
    #             "status_code": response.status_code,
    #         }

    #     data = response.json()
    #     endereco = data["results"][0]["formatted_address"]

    #     poligono = ConsultasEnderecos.verificar_poligono(latitude, longitude)
    #     bairro = ConsultasEnderecos.verificar_bairro(poligono)

    #     ConsultasEnderecos.registrar_endereco(
    #         nome=endereco, bairro=bairro, lat=str(latitude), lon=str(longitude)
    #     )

    #     return endereco

    # @classmethod
    # @db_connector
    # def busca_lat_lon(cls, connection, endereco):
    #     """Função para buscar a latitude e longitude do cliente"""
    #     existence = (
    #         connection.session.query(Enderecos)
    #         .filter(Enderecos.nome == endereco)
    #         .first()
    #     )

    #     if existence:
    #         return existence.to_dict()

    #     url = (
    #         f"https://maps.googleapis.com/maps/api/geocode/json?"
    #         f"address={endereco}&key={TestingConfig.GOOGLE_API}"
    #     )

    #     try:
    #         response = requests.get(url)

    #         if response.status_code == 200:
    #             data = response.json()

    #             if data["status"] == "OK" and len(data["results"]) > 0:
    #                 result = data["results"][0]
    #                 location = result["geometry"]["location"]

    #                 lat = location["lat"]
    #                 lon = location["lng"]
    #                 poligono = ConsultasEnderecos.verificar_poligono(lat, lon)
    #                 bairro = ConsultasEnderecos.verificar_bairro(poligono)

    #                 ConsultasEnderecos.registrar_endereco(
    #                     nome=endereco, bairro=bairro, lat=str(lat), lon=str(lon)
    #                 )

    #                 return {
    #                     "nome": endereco,
    #                     "bairro": bairro,
    #                     "lat": lat,
    #                     "lon": lon,
    #                 }

    #             else:
    #                 return {"error": "Nenhuma coordenada encontrada."}

    #         else:
    #             return {
    #                 "error": f"Erro na requisição: {response.status_code}",
    #                 "detalhes": response.text,
    #             }

    #     except Exception as e:
    #         return {"error": f"Erro inesperado: {e}"}

    @staticmethod
    def consultar_distancia_tempo_da_corrida(partida, chegada):

        response = requests.get(
            f"https://maps.googleapis.com/maps/api/directions/json?origin={partida}&destination={chegada}&key={TestingConfig.GOOGLE_API}"
        )
        if response.status_code == 200:

            data = response.json()
            embarque_corrigido = data["routes"][0]["legs"][0]["start_address"]
            destino_corrigido = data["routes"][0]["legs"][0]["end_address"]
            duracao = data["routes"][0]["legs"][0]["duration"]["value"]  # Em segundos
            distancia = data["routes"][0]["legs"][0]["distance"]["value"]  # Em metros

            dados = {
                "duracao": duracao,
                "distancia": distancia,
                "destino_corrigido": destino_corrigido,
                "embarque_corrigido": embarque_corrigido,
            }

            # Retorne como JSON
            return dados

        else:
            return {
                "erro": "Não foi possível obter os dados da API.",
                "status_code": response.status_code,
            }

    @staticmethod
    def gerar_link_local(latitude, longitude):
        """Gera um link para o Google Maps baseado em coordenadas geográficas."""

        # Validar os parâmetros
        if not (
            isinstance(latitude, (int, float)) and isinstance(longitude, (int, float))
        ):
            raise ValueError("Latitude e longitude devem ser números.")

        # Base URL do Google Maps para coordenadas
        base_url = "https://www.google.com/maps/search/?api=1&query="

        # Construir o link final
        mensagem = f"{base_url}{latitude},{longitude}"
        return mensagem

    @staticmethod
    def extrair_cidades(endereco):
        """
        Extrai o nome das cidades diretamente de um dicionário contendo os endereços de embarque e destino.
        """
        cidades = {}

        def obter_cidade(endereco_str):
            """
            Extrai o nome da cidade de um endereço em string, ignorando Plus Codes.
            """
            # Remover possíveis Plus Codes (padrão: 4 caracteres + "+" + 2 a 4 caracteres)
            endereco_str = re.sub(r"\b\w{4}\+\w{2,4}\b", "", endereco_str)

            # Procurar padrão "Cidade - UF", "Cidade, UF" ou "- Cidade, UF"
            match = re.search(
                r"([\w\s]+) - [A-Z]{2}|([\w\s]+), [A-Z]{2}|- ([\w\s]+), [A-Z]{2}",
                endereco_str,
            )
            if match:
                return match.group(1) or match.group(2) or match.group(3)
            else:
                return "Cidade não identificada"

        # Processar embarque
        cidades["embarque"] = obter_cidade(endereco["embarque"])

        # Processar destino
        cidades["destino"] = obter_cidade(endereco["destino"])

        return cidades

    @staticmethod
    def lat_lon(endereco):
        """Função para buscar a latitude e longitude do cliente"""

        # Construir a URL da API para buscar a latitude e longitude
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco}&key={TestingConfig.GOOGLE_API}"

        try:
            # Fazer a requisição GET para a API
            response = requests.get(url)

            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 200:
                data = response.json()

                # Extrair lat e lon da primeira resposta
                # Verificar se a resposta contém resultados
                if data["status"] == "OK" and len(data["results"]) > 0:
                    # Extrair a latitude e a longitude do primeiro resultado
                    location = data["results"][0]["geometry"]["location"]
                    lat = location["lat"]
                    lon = location["lng"]

                    return lat, lon
                else:
                    print("Nenhuma coordenada encontrada na resposta.")
                    return None

            else:
                print(f"Erro na requisição: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            return None

    @staticmethod
    def gerar_link_google_maps(embarque, destino):
        """Gera um link para o Google Maps com os pontos de embarque e destino."""

        # Preparar os parâmetros para o URL do Google Maps
        base_url = "https://www.google.com/maps/dir/"
        embarque_encoded = urllib.parse.quote(embarque)
        destino_encoded = urllib.parse.quote(destino)

        # Construir o link final
        link_rota = f"{base_url}{embarque_encoded}/{destino_encoded}"
        # print(link_rota)
        return link_rota

    @staticmethod
    def comparar_distancias(partida_lat, partida_lon, chegada_lat, chegada_lon):
        """Busca a distância entre dois pontos usando a API Distance Matrix."""
        try:

            # URL da API com parâmetros adequados
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={partida_lat},{partida_lon}&destinations={chegada_lat},{chegada_lon}&units=metric&key={TestingConfig.GOOGLE_API}"
            response = requests.get(url)

            if response.status_code == 200:
                dados = response.json()
                # print(f"Resposta da API: {dados}")
                # Verifica se a API retornou resultados válidos
                status_element = dados["rows"][0]["elements"][0]["status"]
                if status_element == "OK":
                    distancia = dados["rows"][0]["elements"][0]["distance"]["value"]
                    tempo_para_embarque = dados["rows"][0]["elements"][0]["duration"][
                        "value"
                    ]
                    # print(f"Distância calculada: {tempo_para_embarque} metros")
                    return {
                        "distancia": distancia,
                        "tempo_para_embarque": tempo_para_embarque,
                    }

                else:
                    print(f"Erro na resposta da API: {status_element}")
                    return None
            else:
                print(f"Erro ao acessar a API: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro durante a execução: {e}")
            return None
