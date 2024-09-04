import calendar
import datetime
from typing import Optional

from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required

from . import tvmaze
from .service import get_service

bp = Blueprint("api", __name__)


def generate_date_range(
    today: Optional[datetime.date] = None, style: str = "half"
) -> tuple[datetime.date, datetime.date]:
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    if style == "half":
        first_date = today - datetime.timedelta(days=15)
        last_date = today + datetime.timedelta(days=15)
    else:
        first_date = today.replace(day=1)
        last_day_of_month = calendar.monthrange(first_date.year, first_date.month)[1]
        last_date = first_date.replace(day=last_day_of_month)
    return first_date, last_date


def to_int(maybe_int) -> Optional[int]:
    try:
        return int(maybe_int)
    except:
        return None


@bp.route("/series/<int:series_id>", methods=["GET"])
def get_series_info(series_id: int):
    series = get_service().get_series_details(series_id)
    if not series:
        return jsonify({"error": "Series not found!"}), 404

    episodes = get_service().get_series_episodes(series_id)
    series.episodes = episodes
    return jsonify(series)


@bp.route("/airdate", defaults={"style": "half"}, methods=["GET"])
@bp.route("/airdate/<string:style>", methods=["GET"])
def get_airdate(style: str):
    first_date, last_date = generate_date_range(style=style)
    r = get_service().get_airdate(first_date, last_date)
    return jsonify(r)


#


@bp.route("/users/<int:member_id>/airdate", defaults={"style": "half"}, methods=["GET"])
@bp.route("/users/<int:member_id>/airdate/<string:style>", methods=["GET"])
def get_member_airdate(member_id: int, style: str):
    first_date, last_date = generate_date_range(style=style)
    r = get_service().get_member_airdate(first_date, last_date, member_id)
    return jsonify(r)


@bp.route("/users/<int:member_id>/following", methods=["GET"])
def get_member_following(member_id):
    member_id = 1
    r = get_service().get_following(member_id)
    return jsonify(r)


@bp.route(
    "/users/<int:member_id>/series/<int:series_id>/seasons/<int:season>",
    methods=["PATCH"],
)
@login_required
def set_member_season_status(member_id, series_id, season):
    if member_id != current_user.id:
        return jsonify("Wrong user"), 401

    body = request.get_json(force=True)
    if body.get("status") == "seen":
        get_service().set_season_status(member_id, series_id, season, 2)
        return jsonify(""), 200
    elif body.get("status") == "unseen":
        get_service().set_season_status(member_id, series_id, season, 0)
        return jsonify(""), 200
    return jsonify(""), 404


@bp.route(
    "/users/<int:member_id>/series/<int:series_id>/seasons/<int:season>/episodes/<int:episode>",
    methods=["PATCH"],
)
@login_required
def set_member_episode_status(member_id, series_id, season, episode):
    if member_id != current_user.id:
        return jsonify("Wrong user"), 401

    body = request.get_json(force=True)
    if body.get("status") == "seen":
        get_service().set_episode_status(member_id, series_id, season, episode, 2)
        return jsonify(""), 200
    elif body.get("status") == "unseen":
        # TODO: delete instead of change to 0
        get_service().set_episode_status(member_id, series_id, season, episode, 0)
        return jsonify(""), 200

    return jsonify(""), 404


@bp.route("/users/<int:member_id>/series/<int:series_id>", methods=["PATCH"])
@login_required
def set_member_series_current_season(member_id, series_id):
    if member_id != current_user.id:
        return jsonify("Wrong user"), 401

    body = request.get_json(force=True)
    selected_season = to_int(body.get("selected_season"))
    if selected_season:
        get_service().select_season(member_id, series_id, selected_season)
        return jsonify(""), 200

    return jsonify(""), 404


@bp.route("/import", methods=["POST"])
@login_required
def import_series_post():
    ids_input = request.form.get("ids")
    if not ids_input:
        return jsonify(""), 404

    ids = ids_input.split()
    ids_int: list[int] = list(set(filter(lambda x: isinstance(x, int), map(to_int, ids))))  # type: ignore
    if not ids_int:
        return jsonify(""), 400

    service = get_service()
    for id in ids_int:
        # FIXME(crash): check if show already available
        current_app.logger.info(f"Import show from TVmaze: {id}")
        local_show_id = tvmaze.import_show(id, service)
        service.save_show_to_member(local_show_id, 1, 1, current_user.id)

    return jsonify(ids_int)


@bp.route("/update", methods=["GET"])
@login_required
def update_series():
    # FIXME(crash@veluna): allow only for admins
    service = get_service()
    show_ids = tvmaze.update_shows(service)
    return jsonify({"ids": list(show_ids)})
