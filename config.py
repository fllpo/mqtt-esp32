# Configurações MQTT
MQTT_BROKER = "45d119c6848248fea530845a5e22ec29.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
CLIENT_NAME = "client"
PASSWORD = "9IoV.TG6,x3l7*OybXc#"
MQTT_TOPICS = [
    "esp32/bme280/temperatura",
    "esp32/bme280/umidade",
    "esp32/bme280/pressao"
]

# Configurações MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '2018780075',
    'database': 'esp32teste'
}