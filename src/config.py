from datetime import timedelta


SQLALCHEMY_DATABASE_URI = "sqlite:///mw.db"
ADMIN_PASSWORD = "ADMIN"
PASSWORD_PEPPER = "PEPPER"
JWT_SECRET_KEY = "TESTING"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
