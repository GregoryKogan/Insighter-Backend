from app import jwt
from apps.Users.models import User


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)


def get_user_credentials(request) -> dict:
    data = None
    try:
        data = request.json
    except Exception as e:
        return {"err": str(e)}

    if data is None:
        return {"err": "No data provided"}

    name = data.get("username", None)
    password = data.get("password", None)
    if name is None or password is None:
        return {"err": "Invalid user data"}

    return {"name": name, "password": password}


def validate_username(username: str) -> (bool, str):
    if len(username) < 5:
        return False, "username is too short"

    if len(username) > 40:
        return False, "username is too long"

    exists = User.query.filter_by(name=username).one_or_none()
    if exists:
        return False, "username already taken"

    return True, None
