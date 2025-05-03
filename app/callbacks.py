def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


# def on_publish(client, userdata, mid, properties=None):
#    print("mid: " + str(mid))


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Inscrito em: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    
    if msg.topic == "esp32/bme280/temperatura":
        print("Temperatura: " + str(msg.payload.decode("utf-8")) + " °C")
    elif msg.topic == "esp32/bme280/umidade":
        print("Umidade: " + str(msg.payload.decode("utf-8")) + " %")
    elif msg.topic == "esp32/bme280/pressao":
        print("Pressao: " + str(msg.payload.decode("utf-8")) + " hPa")
