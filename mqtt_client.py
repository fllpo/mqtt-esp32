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
    cleanup()
    client.disconnect()
    sys.exit(0)

client = paho.Client(paho.CallbackAPIVersion.VERSION2, protocol=paho.MQTTv5)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(os.getenv("CLIENT_NAME"), os.getenv("PASSWORD"))
client.connect(os.getenv("HOST"), 8883, keepalive=60)

signal.signal(signal.SIGINT, signal_handler)
client.loop_forever()
