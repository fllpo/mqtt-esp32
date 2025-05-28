from database_handler import DatabaseHandler

db_handler = DatabaseHandler()

leituras_atuais = {
    'temperatura': None,
    'umidade': None,
    'pressao': None
}

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"CONNACK recebido com código {rc}.")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print(f"Inscrito com sucesso! ID: {mid} {granted_qos[0]}")

def on_message(client, userdata, msg):
    try:
        topico = msg.topic
        payload = msg.payload.decode("utf-8")
        valor = float(payload)
                
        if 'temperatura' in topico:
            leituras_atuais['temperatura'] = valor
            print(f"Temperatura: {valor} °C")
        elif 'umidade' in topico:
            leituras_atuais['umidade'] = valor
            print(f"Umidade: {valor} %")
        elif 'pressao' in topico:
            leituras_atuais['pressao'] = valor
            print(f"Pressão: {valor} hPa")
            
        if all(v is not None for v in leituras_atuais.values()):
            if db_handler.insert_reading(
                leituras_atuais['temperatura'],
                leituras_atuais['umidade'],
                leituras_atuais['pressao']
            ):
                for i in leituras_atuais:
                    leituras_atuais[i] = None
                    
    except ValueError as e:
        print(f"Erro ao processar payload: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def cleanup():
    db_handler.close()