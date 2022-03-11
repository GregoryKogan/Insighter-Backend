from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from config import *


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = JWT_REFRESH_TOKEN_EXPIRES
jwt = JWTManager(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


from apps.Users.models import *


db.create_all()
if User.query.filter_by(rank="Admin").one_or_none() is None:
    admin = User(name="Admin", password=ADMIN_PASSWORD, rank="Admin")
    db.session.add(admin)
db.session.commit()


from apps.Ping.views import *  # noqa
from apps.Authorization.views import *  # noqa
from apps.Users.views import *  # noqa


if __name__ == "__main__":
    app.run(debug=True)
