import time
import os
import signal
import sys
from dotenv import load_dotenv
import paho.mqtt.client as paho
from paho import mqtt
from callbacks import *

load_dotenv()

def signal_handler(sig, frame):
    print("\nEncerrando aplicação...")
    cleanup()  # Função de limpeza dos callbacks
    client.disconnect()
    sys.exit(0)

# Configura cliente MQTT
client = paho.Client(protocol=paho.MQTTv5)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message

# Configura TLS e credenciais
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(os.getenv("CLIENT_NAME"), os.getenv("PASSWORD"))
client.connect(os.getenv("HOST"), 8883)

# Inscreve nos tópicos
client.subscribe(os.getenv("TOPIC"), qos=1)

# Configura handler para Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

print("Aplicação iniciada. Pressione Ctrl+C para sair.")
client.loop_forever()