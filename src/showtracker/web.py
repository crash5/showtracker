from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import auth

bp = Blueprint("web", __name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("web.airdate"))
    else:
        return redirect(url_for("web.login"))


@bp.route("/airdate")
def airdate():
    return render_template("airdate.html")


@bp.route("/airdate2")
def airdate2():
    return render_template("airdate2.html")


@bp.route("/following")
def following():
    return render_template("following.html")


@bp.route("/import")
@login_required
def import_series():
    return render_template("import.html")


@bp.route("/series/<int:id>")
def series(id):
    return render_template("series_detail.html", id=id)


@bp.route("/login")
def login():
    return render_template("login.html")


@bp.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("name")
    password = request.form.get("password")
    rememberme = bool(request.form.get("rememberme", False))

    if username and password:
        user = auth.user_if_can_login(username, password)
        if user:
            login_user(user, remember=rememberme)
            return redirect(url_for("web.index"))

    flash("Error, bad credentials?")
    return redirect(url_for("web.login"))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.index"))
