from flask import Flask, render_template, jsonify
from callbacks import db_handler
app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/dados')
def api_dados():
    return jsonify(db_handler.get_latest_data())

app.run(host="localhost", port=5000, debug=True, use_reloader=False)
