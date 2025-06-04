from flask import Flask, render_template, jsonify
from callbacks import db_handler
#from previsao import get_forecast

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route("/api/dados_sensor")
def api_dados():
    return jsonify(db_handler.get_latest_data())


#@app.route("/api/previsao")
# def api_previsao():
#    return jsonify(get_forecast())


app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
