import logging
from datetime import timedelta
import os

from flask import Flask
from flask_login import LoginManager
from flask_apscheduler import APScheduler

from . import api
from . import web
from . import auth
from .util import tvmaze_update

logger = logging.getLogger()


##########
# App
##########
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET')
if not FLASK_SECRET_KEY:
    logger.warning('No secret key from "FLASK_SECRET" environment variable, using an automatically generated secret key.')
    FLASK_SECRET_KEY = os.urandom(12)


app = Flask(__name__, static_url_path='')
app.config.update(
    SECRET_KEY=FLASK_SECRET_KEY,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_SECURE=True,
    REMEMBER_COOKIE_DURATION=timedelta(days=30),
    REMEMBER_COOKIE_SAMESITE='Strict'
)


##########
# Auth
##########
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'web.login'
# login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id: str):
    return auth.load_user(user_id)


##########
# Scheduler
##########
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
scheduler.add_job(
    func=tvmaze_update.main,
    trigger='interval',
    hours=8,
    id='update_from_tvmaze',
    replace_existing=True,
    coalesce=True,
    max_instances=1,
)


##########
# Blueprint
##########
app.register_blueprint(api.bp, url_prefix='/api')
app.register_blueprint(web.bp)
