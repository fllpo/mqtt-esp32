from database_handler import DatabaseHandler

# Cria instância do banco de dados
db_handler = DatabaseHandler()

# Variáveis para acumular as leituras
current_readings = {
    'temperatura': None,
    'umidade': None,
    'pressao': None
}

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"CONNACK recebido com código {rc}.")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print(f"Inscrito com mid {mid} e QoS {granted_qos}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        value = float(payload)
        
        print(f"Mensagem recebida - Tópico: {topic}, Valor: {value}")
        
        # Identifica o tipo de leitura pelo tópico
        if 'temperatura' in topic:
            current_readings['temperatura'] = value
        elif 'umidade' in topic:
            current_readings['umidade'] = value
        elif 'pressao' in topic:
            current_readings['pressao'] = value
            
        # Verifica se temos todas as leituras
        if all(v is not None for v in current_readings.values()):
            if db_handler.insert_reading(
                current_readings['temperatura'],
                current_readings['umidade'],
                current_readings['pressao']
            ):
                # Reseta as leituras após inserção bem-sucedida
                for key in current_readings:
                    current_readings[key] = None
                    
    except ValueError as e:
        print(f"Erro ao processar payload: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def cleanup():
    db_handler.close()