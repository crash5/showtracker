from datetime import timedelta
import os

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user, login_required

from . import api_blueprint
from . import auth


app = Flask(__name__, static_url_path='')
app.config.update(
    SECRET_KEY=os.getenv('FLASK_SECRET'),
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
