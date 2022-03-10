from flask import jsonify, request
from flask_jwt_extended import (
    current_user,
    jwt_required,
)
from app import app, db
from apps.Users.models import User
from apps.Authorization.auth_utils import *


# TODO: Only admin can get list of users


@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize for user in users]), 200


@app.route("/users", methods=["POST"])
def create_user():
    user_credentials = get_user_credentials(request)
    if "err" in user_credentials:
        return jsonify({"msg": user_credentials["err"]}), 400

    name, password = user_credentials["name"], user_credentials["password"]

    is_name_valid, err = validate_username(name)
    if not is_name_valid:
        return jsonify({"msg": err}), 400

    new_user = User(name=name, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize), 200


@app.route("/users/me", methods=["GET"])
@jwt_required()
def get_self():
    return jsonify(current_user.serialize), 200
