import logging
from datetime import timedelta
import os

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user, login_required

from flask_apscheduler import APScheduler

from . import api_blueprint
from . import auth
from .util import tvmaze_update


logger = logging.getLogger()


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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
# login_manager.session_protection = "strong"


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


@login_manager.user_loader
def load_user(user_id: str):
    return auth.load_user(user_id)


app.register_blueprint(api_blueprint.bp, url_prefix='/api')
app.register_blueprint(auth.bp)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('airdate'))
    else:
        return redirect(url_for('auth.login'))

@app.route('/airdate')
def airdate():
    return render_template('airdate.html')

@app.route('/following')
def following():
    return render_template('following.html')

@app.route('/series/<int:id>')
def series(id):
    return 'Under construction'

@app.route('/import')
@login_required
def import_series():
    return render_template('import.html')
