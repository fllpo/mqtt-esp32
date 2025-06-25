from database_handler import DatabaseHandler
import json
import os
from dotenv import load_dotenv

db_handler = DatabaseHandler()

leituras_atuais = {
    "temperatura_atual": None,
    "temperatura_max": None,
    "temperatura_min": None,
    
    "pressao_atual": None,
    "pressao_max": None,
    "pressao_min": None,
    
    "umidade_atual": None,
    "umidade_max": None,
    "umidade_min": None,
    
    "orvalho_atual": None,
    "orvalho_max": None,
    "orvalho_min": None,
}
    
def on_connect(client, userdata, flags, rc, properties=None):
    if rc != 0:
        print(f"CONNACK recebido com código {rc}.")
    else:
        print("Conectado com sucesso ao broker MQTT!")
        client.subscribe(os.getenv("TOPIC"), qos=1)

def on_disconnect(client, userdata, flags, rc, properties=None):
    print("Desconectado do broker MQTT com código:", rc)
    if rc != 0:
        print("Tentando reconectar...")
        try:
            client.reconnect()
        except Exception as e:
            print(f"Falha na reconexão: {e}")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print(f"Inscrito com sucesso! ID: {mid} {granted_qos[0]}")

def on_message(client, userdata, msg):
    try:
        topico = msg.topic
        payload = msg.payload.decode("utf-8")
        
        if 'temperatura' in topico:
            valor = float(payload)
            leituras_atuais['temperatura_atual'] = valor
            print(f"Temperatura: {valor} °C")
        elif 'umidade' in topico:
            valor = float(payload)
            leituras_atuais['umidade_atual'] = valor
            print(f"Umidade: {valor} %")
        elif 'pressao' in topico:
            valor = float(payload)
            leituras_atuais['pressao_atual'] = valor
            print(f"Pressão: {valor} hPa")
        elif 'ponto_orvalho' in topico:
            valor = float(payload)
            leituras_atuais['orvalho_atual'] = valor
            print(f"Ponto de orvalho: {valor} °C")
        elif 'extremos' in topico:
            extremos = json.loads(payload)
            leituras_atuais['temperatura_min'] = extremos['temperatura']['min']
            leituras_atuais['temperatura_max'] = extremos['temperatura']['max']
            leituras_atuais['pressao_min'] = extremos['pressao']['min']
            leituras_atuais['pressao_max'] = extremos['pressao']['max']
            leituras_atuais['umidade_min'] = extremos['umidade']['min']
            leituras_atuais['umidade_max'] = extremos['umidade']['max']
            leituras_atuais['orvalho_min'] = extremos['ponto_orvalho']['min']
            leituras_atuais['orvalho_max'] = extremos['ponto_orvalho']['max']

        if all(v is not None for v in leituras_atuais.values()):
            if db_handler.insert_reading(
                leituras_atuais['temperatura_atual'],
                leituras_atuais['temperatura_max'],
                leituras_atuais['temperatura_min'],
                leituras_atuais['umidade_atual'],
                leituras_atuais['umidade_max'],
                leituras_atuais['umidade_min'],
                leituras_atuais['pressao_atual'],
                leituras_atuais['pressao_max'],
                leituras_atuais['pressao_min'],
                leituras_atuais['orvalho_atual'],
                leituras_atuais['orvalho_max'],
                leituras_atuais['orvalho_min']
            ):
                for i in leituras_atuais:
                    leituras_atuais[i] = None


    except ValueError as e:
        print(f"Erro ao processar payload: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def cleanup():
    db_handler.close()
