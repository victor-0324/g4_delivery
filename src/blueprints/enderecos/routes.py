from flask import Blueprint, request, jsonify
from geopy.distance import geodesic
import requests
# from .consultas import ConsultasEnderecos

endereco_app = Blueprint("endereco_app", __name__, url_prefix="/endereco/")


def public_endpoint(function):
    """Decorator for public routes"""
    function.is_public = True
    return function


@public_endpoint
@endereco_app.route("/", methods=["POST"])
def gerere():
    """Endpoint para testar o funcionamento do blueprint de endereços"""
    return jsonify({"message": "Blueprint de endereços funcionando!"}), 200


SAO_LOURENCO_COORDS = (-22.1164, -45.0559)
LOCATIONIQ_API_KEY = "pk.7ef02a32917f0cc4ea887c2d6190cf29"


def calcular_prioridade(distancia_km):
    if distancia_km <= 0.5:
        return 1.0
    elif distancia_km < 100:
        return round(1 - (distancia_km / 100), 2)
    else:
        return 0.0


@public_endpoint
@endereco_app.route("/locationiq", methods=["POST"])
def locationiq():
    data = request.json
    endereco = data.get("endereco")

    if not endereco:
        return jsonify({"erro": "Endereço não fornecido"}), 400

    # Chamada à API LocationIQ, restringindo ao Brasil
    url = "https://api.locationiq.com/v1/autocomplete"
    params = {
        "key": LOCATIONIQ_API_KEY,
        "q": endereco,
        "limit": 5,
        "dedupe": 1,
        "countrycodes": "br",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        resultados = response.json()

        ranked_results = []
        for r in resultados:
            lat = float(r.get("lat", 0))
            lon = float(r.get("lon", 0))
            distancia_km = geodesic(SAO_LOURENCO_COORDS, (lat, lon)).km

            prioridade = calcular_prioridade(distancia_km)

            r["distancia_km"] = round(distancia_km, 2)
            r["prioridade"] = prioridade
            ranked_results.append(r)

        # Ordena: prioridade desc, distância asc
        resultados_ordenados = sorted(
            ranked_results, key=lambda x: (-x["prioridade"], x["distancia_km"])
        )

        return jsonify(resultados_ordenados)

    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500


@public_endpoint
@endereco_app.route("/googlemaps", methods=["POST"])
def googlemaps():
    from .google_api import ConsultasGoogleAPI

    data = request.get_json()
    endereco = data.get("endereco")
    result = ConsultasGoogleAPI.busca_lat_lon(endereco=endereco)
    return jsonify(result)


@public_endpoint
@endereco_app.route("/registrar_endereco", methods=["POST"])
def registrar_endereco():
    """Adiciona um endereço novo ao banco de dados."""
    from ..corridas.consultas import ConsultasCorridas

    data = request.get_json()
    nome = data.get("nome")
    lat = data.get("lat")
    lon = data.get("lon")
    poligono = ConsultasCorridas.verificar_poligono(lat, lon)
    bairro = ConsultasCorridas.verificar_bairro(poligono)
    endereco = ConsultasEnderecos.registrar_endereco(nome, bairro, lat, lon)

    return jsonify(endereco)


@public_endpoint
@endereco_app.route("/extrair_cidades", methods=["POST"])
def busca_endereo():
    """Extrai as cidades de embarque e destino de um endereço completo."""
