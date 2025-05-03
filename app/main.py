import time
import os
from dotenv import load_dotenv
import paho.mqtt.client as paho
from callbacks import *
from paho import mqtt


load_dotenv()

client = paho.Client(protocol=paho.MQTTv5)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(os.getenv("CLIENT_NAME"),os.getenv("PASSWORD"))
client.connect(os.getenv("HOST"), 8883)

client.subscribe(os.getenv("TOPIC"), qos=1)

client.loop_forever()
