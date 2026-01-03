import requests
from time import sleep
from src.settings import TestingConfig
import requests


class LocationIq:
    """Faz as requisiçoes no location iq"""

    @staticmethod
    def busca_endereco(latitude, longitude):
        """Busca o endereço do motorista usando LocationIQ Reverse Geocoding."""
        try:
            url = (
                f"https://us1.locationiq.com/v1/reverse"
                f"?key={TestingConfig.API_LOCATION_KEY}"
                f"&lat={latitude}&lon={longitude}&format=json"
            )

            response = requests.get(url, timeout=10)
            sleep(0.51)
            if response.status_code == 200:
                data = response.json()
                endereco = data.get("display_name")
                if endereco:
                    return endereco
                else:
                    return {"erro": "Endereço não encontrado no retorno da API."}

            else:
                return {
                    "erro": "Não foi possível obter os dados da API.",
                    "status_code": response.status_code,
                    "response": response.text,
                }

        except requests.Timeout:
            return {"erro": "A requisição expirou (timeout)."}

        except requests.RequestException as e:
            return {"erro": "Erro ao fazer requisição HTTP.", "detalhes": str(e)}

        except Exception as e:
            return {
                "erro": "Erro inesperado ao processar o endereço.",
                "detalhes": str(e),
            }

    @staticmethod
    def comparar_distancias(partida_lat, partida_lon, chegada_lat, chegada_lon):
        """Busca a distância entre dois pontos usando a API Directions do LocationIQ."""
        try:
            url = (
                f"https://us1.locationiq.com/v1/directions/driving/"
                f"{partida_lon},{partida_lat};{chegada_lon},{chegada_lat}"
                f"?key={TestingConfig.API_LOCATION_KEY}&steps=false&alternatives=false&geometries=polyline&overview=false"
            )

            response = requests.get(url)
            sleep(0.34)
            print(response)
            if response.status_code == 200:
                dados = response.json()

                if dados.get("code") == "Ok":
                    rota = dados["routes"][0]

                    distancia = rota["distance"]
                    duracao = rota["duration"]

                    return {"distancia": distancia, "tempo_para_embarque": duracao}
                else:
                    print("Erro na resposta:", dados.get("code"))
                    return None

            else:
                print(f"Erro ao acessar a API: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"Erro durante a execução: {e}")
            return None

    @staticmethod
    def buscar_lat_lon(endereco):
        """
        Busca latitude e longitude usando apenas AUTOCOMPLETE do LocationIQ.
        Retorna sempre o resultado mais relevante.
        """

        try:
            url_auto = (
                f"https://api.locationiq.com/v1/autocomplete"
                f"?key={TestingConfig.API_LOCATION_KEY}"
                f"&q={endereco}"
                f"&limit=5"
                f"&dedupe=1"
            )

            resposta = requests.get(url_auto)

            if resposta.status_code != 200:
                print(f"Autocomplete falhou: HTTP {resposta.status_code}")
                return None

            dados = resposta.json()

            if not isinstance(dados, list) or len(dados) == 0:
                print("Autocomplete retornou vazio")
                return None

            melhor = dados[0]  # mais relevante

            lat = melhor.get("lat")
            lon = melhor.get("lon")

            # Converter para float
            try:
                lat = float(lat)
                lon = float(lon)
            except:
                print("Erro convertendo lat/lon para float")
                return None

            return {"lat": lat, "lon": lon, "display_name": melhor.get("display_name")}

        except Exception as e:
            print(f"Erro na busca de lat/lon: {e}")
            return None
