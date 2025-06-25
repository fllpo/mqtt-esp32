import os
import signal
import sys
from dotenv import load_dotenv
import paho.mqtt.client as paho
from paho import mqtt
from callbacks import *
import time

load_dotenv()

def signal_handler(sig, frame):
    print("\nEncerrando aplicação...")
    cleanup()
    client.disconnect()
    sys.exit(0)

client = paho.Client(paho.CallbackAPIVersion.VERSION2,
                     protocol=paho.MQTTv5,
                     reconnect_on_failure=True
)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(os.getenv("CLIENT_NAME"), os.getenv("PASSWORD"))
client.reconnect_delay_set(min_delay=1, max_delay=120)
client.connect_timeout = 10

max_tentativas = 3
tentativas = 0

while tentativas < max_tentativas:
    try:
        client.connect(os.getenv("HOST"), 8883, keepalive=60)
        break
    except Exception as e:
        print(f"Erro na conexão: {e}")
        tentativas += 1
        if tentativas == max_tentativas:
            print("Número máximo de tentativas de conexão atingido. Encerrando.")
            sys.exit(1)
        time.sleep(5)

signal.signal(signal.SIGINT, signal_handler)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
except Exception as e:
    print(f"Erro inesperado: {e}")
    client.disconnect()
finally:
    cleanup()
