from typing import Optional

from flask_login import LoginManager, UserMixin

from . import password_hash, service


def init_app(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "web.login"  # type: ignore

    @login_manager.user_loader
    def user_loader(user_id: int) -> Optional[User]:
        u = service.get_service().get_member_by_id(user_id)
        if u:
            return User(u["name"], u["member_id"])
        return None


class User(UserMixin):
    def __init__(self, name, id):
        self.name = name
        self.id = id


def user_if_can_login(username: str, password: str) -> Optional[User]:
    db_user = service.get_service().get_member_by_name(username)
    if db_user and password_hash.verify_password(password, db_user["password"]):
        return User(db_user["name"], db_user["member_id"])
    return None
