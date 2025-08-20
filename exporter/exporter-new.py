import requests
import json
import time
from prometheus_client import start_http_server, Gauge

url_numero_pessoas = "http://api.open-notify.org/astros.json"
url_local_iss = "http://api.open-notify.org/iss-now.json"

def pega_local_iss():
    try:
        """
        Faz uma requisição HTTP para obter a localização atual da ISS.
        """
        response = requests.get(url_local_iss)
        data = response.json()
        return data['iss_position']
    except Exception as e:
        print(f"Erro ao obter dados da api externa para capturar a localização da ISS: {e}")

def pega_numero_astronautas():
    try:
        """
        Faz uma requisição HTTP para obter o número de astronautas atualmente no espaço.
        """
        response = requests.get(url_numero_pessoas)
        data = response.json()
        return data['number']
    except Exception as e:
        print(f"Erro ao obter dados da api externa: {e}")
        return 0
    
def atualiza_metricas():
    try:
        """
        Atualiza as métricas do Prometheus com o número de astronautas no espaço e localização atual da ISS.
        """
        numero_pessoas = Gauge('numero_de_astronautas', 'Número de astronautas atualmente no espaço')
        longitude = Gauge('longitude_iss', 'Longitude atual da ISS')
        latitude = Gauge('latitude_iss', 'Latitude atual da ISS')

        while True:
            numero_pessoas.set(pega_numero_astronautas())
            longitude.set(pega_local_iss()['longitude'])
            latitude.set(pega_local_iss()['latitude'])
            time.sleep(10)
            print("O número de astronautas no espaço nesse momento é: %s" % pega_numero_astronautas())
            print("A longitude atual da ISS é: %s" % pega_local_iss()['longitude'])
            print("A latitude atual da ISS é: %s" % pega_local_iss()['latitude'])
    except Exception as e:
        print(f"Erro ao atualizar métricas: {e}")

def inicia_exporter():
    try:
        """
        Inicia o servidor HTTP do Prometheus e começa a atualizar as métricas.
        """
        start_http_server(8899)
        return True
    except Exception as e:
        print(f"Erro ao iniciar o servidor HTTP do Prometheus: {e}")

def main():
    try:
        """
        Função principal que inicia o exporter.
        """
        inicia_exporter()
        print("HTTP server do Prometheus iniciado na porta 8899")
        atualiza_metricas()
    except Exception as e:
        print(f"Erro na inicialização do exporter: {e}")
        exit(1)

if __name__ == "__main__":
    main()
    exit(0)