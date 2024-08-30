import os
import sys
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET") or sys.exit(
        'Set "FLASK_SECRET" env. variable!'
    )

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # Flask-Login
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = timedelta(days=30 * 6)
    REMEMBER_COOKIE_SAMESITE = "Strict"

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or sys.exit(
        'Set "DATABASE_URL" env. variable!'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Dev(Config):
    DEBUG = True


class Test(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///:memory:"


class Prod(Config):
    DEBUG = False
    TESTING = False
