from flask import Flask, render_template, jsonify, request
from callbacks import db_handler
from rag import get_resposta_rag

app = Flask(__name__)

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


app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
