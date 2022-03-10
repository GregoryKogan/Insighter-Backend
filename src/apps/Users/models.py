from app import db
from hmac import compare_digest
import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rank = db.Column(db.String(20), default="User")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<User %>" % self.id

    def check_password(self, password):
        return compare_digest(password, self.password)

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name, "rank": self.rank}
