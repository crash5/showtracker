import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.urandom(12)

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # Flask-Login
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = timedelta(days=30 * 6)
    REMEMBER_COOKIE_SAMESITE = "Strict"

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Dev(Config):
    DEBUG = True
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev-db.sqlite"


class Test(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///:memory:"


class Prod(Config):
    DEBUG = False
    TESTING = False
