import os
import ssl
import json
from flask import Flask, render_template, jsonify, request
from flask_bootstrap import Bootstrap
from flask_mqtt import Mqtt
from dotenv import load_dotenv
from database_handler import DatabaseHandler, Clima
from rag import get_resposta_rag

load_dotenv()

app = Flask(
    import_name=__name__,
    template_folder="../../frontend/templates",
    static_folder="../../frontend/static",
)
bootstrap = Bootstrap(app)

app.config['MQTT_BROKER_URL'] = os.getenv("HOST")
app.config['MQTT_BROKER_PORT'] = 8883
app.config['MQTT_USERNAME'] = os.getenv("CLIENT_NAME")
app.config['MQTT_PASSWORD'] = os.getenv("PASSWORD")
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = True
app.config['MQTT_TLS_VERSION'] = ssl.PROTOCOL_TLS
app.config['MQTT_CLIENT_ID'] = 'flask_server'

mqtt = Mqtt(app)
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

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route("/api/dados_sensor")
def api_dados():
    return jsonify(db_handler.get_latest_data())


@app.route("/api/rag", methods=["POST"])
def api_rag():
    data = request.get_json()
    pergunta = data.get("pergunta", "")
    resposta = get_resposta_rag(pergunta)
    return jsonify({"resposta": resposta})


@app.route("/api/historico/<tipo>")
def historico(tipo):
    campos = {
        "temperatura": "temperatura_atual",
        "umidade": "umidade_atual",
        "pressao": "pressao_atual",
    }
    campo = campos.get(tipo)
    if not campo:
        return jsonify([])

    session = db_handler.Session()
    try:
        resultados = (
            session.query(Clima.timestamp, getattr(Clima, campo))
            .order_by(Clima.timestamp.desc())
            .limit(13)
            .all()
        )

        resultados = resultados[::-1]
        dados = [
            {"hora": str(int(r.timestamp.strftime("%H"))) + "h", "valor": r[1]}
            for r in resultados
        ]
        return jsonify(dados)
    finally:
        session.close()


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"[MQTT] Conexão falhou com código {rc}.")
    else:
        print("[MQTT] Conectado ao broker HiveMQ com sucesso!")
        topic = os.getenv("TOPIC")
        if topic:
            mqtt.subscribe(topic)
            print(f"[MQTT] Inscrito no tópico: {topic}")
        else:
            print("[MQTT] Erro: Tópico não definido no .env")


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    try:
        topico = message.topic
        payload = message.payload.decode("utf-8")       

        if 'temperatura' in topico:
            valor = float(payload)
            leituras_atuais['temperatura_atual'] = valor
            print(f"[MQTT] Temperatura: {valor} °C")
        elif 'umidade' in topico:
            valor = float(payload)
            leituras_atuais['umidade_atual'] = valor
            print(f"[MQTT] Umidade: {valor} %")
        elif 'pressao' in topico:
            valor = float(payload)
            leituras_atuais['pressao_atual'] = valor
            print(f"[MQTT] Pressão: {valor} hPa")
        elif 'ponto_orvalho' in topico:
            valor = float(payload)
            leituras_atuais['orvalho_atual'] = valor
            print(f"[MQTT] Ponto de orvalho: {valor} °C")
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
            if db_handler.insert_reading(**leituras_atuais):
                for key in leituras_atuais:
                    leituras_atuais[key] = None

    except Exception as e:
        print(f"[MQTT] Erro ao processar mensagem: {e}")

@mqtt.on_disconnect()
def handle_disconnect(client, userdata, rc):
    print(f"[MQTT] Desconectado do broker MQTT. Código: {rc}" )


@mqtt.on_log()
def handle_log(client, userdata, level, buf):
    print(f"[MQTT] {buf}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
