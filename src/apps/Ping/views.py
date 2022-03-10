from app import app
from flask import jsonify


@app.route("/ping", methods=["GET"])
def ping_view():
    return jsonify({"message": "pong"}), 200
