from app import db
import datetime
import bcrypt
from config import PASSWORD_PEPPER


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rank = db.Column(db.String(20), default="User")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<User %>" % self.id

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rank": self.rank,
            "created_at": self.created_at.isoformat(),
        }

    @property
    def password(self):
        raise AttributeError("password not readable")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(
            str(password + PASSWORD_PEPPER).encode("utf8"), bcrypt.gensalt()
        )

    def check_password(self, password):
        return bcrypt.checkpw(
            str(password + PASSWORD_PEPPER).encode("utf8"), self.password_hash
        )
