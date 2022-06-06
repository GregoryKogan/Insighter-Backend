from app import app
from flask import request, jsonify
from apps.Authorization.auth_utils import *
from flask_jwt_extended import (
    current_user,
    jwt_required,
    create_access_token,
    create_refresh_token,
)


@app.route("/auth/login", methods=["POST"])
def login():
    user_credentials = get_user_credentials(request)
    if "err" in user_credentials:
        return jsonify({"msg": user_credentials["err"]}), 400

    name, password = user_credentials["name"], user_credentials["password"]

    user = User.query.filter_by(name=name).first()
    if user is None:
        return jsonify({"msg": "This user does not exist"}), 400

    if not user.check_password(password):
        return jsonify({"msg": "Wrong password"}), 400

    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@app.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token)
