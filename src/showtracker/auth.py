from flask_login import UserMixin

from .sqliteapi import get_user_by_id, get_user_by_name
from .password_hash import verify_password
from .db import db


class User(UserMixin):
    def __init__(self, name, id):
        self.name = name
        self.id = id


def user_if_can_login(username, password):
    db_user = get_user_by_name(db.session, username)
    if db_user and verify_password(password, db_user['password']):
        return User(db_user['name'], db_user['member_id'])
    return None


def load_user(user_id: str):
    u = get_user_by_id(db.session, user_id)
    if u:
        return User(u['name'], u['member_id'])
    return None
