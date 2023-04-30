from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
from flask_login import UserMixin, login_user, logout_user, login_required

from .sqliteapi import get_user_by_id, get_user_by_name
from .password_hash import verify_password


bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, name, id):
        self.name = name
        self.id = id

def load_user(user_id: str):
    u = get_user_by_id(user_id)
    if u:
        return User(u['name'], u['member_id'])
    return None


@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('name')
    password = request.form.get('password')
    rememberme = request.form.get('rememberme')

    db_user = get_user_by_name(username)
    if db_user and verify_password(password, db_user['password']):
        user = User(db_user['name'], db_user['member_id'])
        login_user(user, remember=rememberme)
        return redirect(url_for('index'))

    flash('Error, bad credentials?')
    return redirect(url_for('auth.login'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
