from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from . import sqliteapi
from .util import tvmaze
from .db import db


bp = Blueprint('api', __name__)


@bp.route('/series/<int:series_id>', methods=['GET'])
def series(series_id):
    series = sqliteapi.get_series_details(db.session, series_id)
    if not series:
        return jsonify({'error': 'Series not found!'}), 404
    episodes = sqliteapi.get_series_episodes(db.session, series_id)
    series['episodes'] = episodes
    return jsonify(series)


@bp.route('/series/<int:series_id>/episodes', methods=['GET'])
def series_episodes(series_id):
    episodes = sqliteapi.get_series_episodes(db.session, series_id)
    if not episodes:
        return jsonify({'error': 'Series not found!'}), 404
    return jsonify(episodes)


@bp.route('/users/<int:member_id>/airdate')
def airdate(member_id):
    member_id = 1
    style = 'half'

    import datetime
    today = datetime.datetime.now(datetime.timezone.utc).date()
    if style == 'half':
        first_date = today - datetime.timedelta(days=15)
        last_date = today + datetime.timedelta(days=15)
    else:
        import calendar
        first_date = today.replace(day = 1)
        last_day_of_month = calendar.monthrange(first_date.year, first_date.month)[1]
        last_date = first_date.replace(day = last_day_of_month)

    show_dict = sqliteapi.get_airdate(db.session, first_date, last_date, member_id)
    show_dict['user_id'] = member_id
    return jsonify(show_dict)

@bp.route('/users/<int:member_id>/following')
def following(member_id):
    member_id = 1
    shows = dict()
    shows['data'] = sqliteapi.get_following(db.session, member_id)
    shows['user_id'] = member_id
    return jsonify(shows)

###############
# Authorization required
###############

@bp.route('/users/<int:member_id>/series/<int:series_id>/seasons/<int:season>', methods=['PATCH'])
@login_required
def user_series_season_patch(member_id, series_id, season):
    if member_id != current_user.id:
        return jsonify('Wrong user'), 401

    body = request.get_json(force=True)
    if body.get('status') == 'seen':
        sqliteapi.set_season_status(db.session, member_id, series_id, season, 2)
        return jsonify(''), 200
    return jsonify(''), 404


@bp.route('/users/<int:member_id>/series/<int:series_id>/seasons/<int:season>/episodes/<int:episode>', methods=['PATCH'])
@login_required
def user_series_season_episode_patch(member_id, series_id, season, episode):
    if member_id != current_user.id:
        return jsonify('Wrong user'), 401

    body = request.get_json(force=True)
    if body.get('status') == 'seen':
        sqliteapi.set_episode_status(db.session, member_id, series_id, season, episode, 2)
        return jsonify(''), 200

    if body.get('status') == 'unseen':
        # TODO: delete instead of change to 0
        sqliteapi.set_episode_status(db.session, member_id, series_id, season, episode, 0)
        return jsonify(''), 200

    return jsonify(''), 404


@bp.route('/users/<int:member_id>/series/<int:series_id>', methods=['PATCH'])
@login_required
def user_series_patch(member_id, series_id):
    if member_id != current_user.id:
        return jsonify('Wrong user'), 401

    body = request.get_json(force=True)
    selected_season = to_int(body.get('selected_season'))
    if selected_season:
        sqliteapi.select_season(db.session, member_id, series_id, selected_season)
        return jsonify(''), 200

    return jsonify(''), 404


def to_int(x):
    try:
        return int(x)
    except:
        return None

@bp.route('/import', methods=['POST'])
@login_required
def import_series_post():
    ids_input = request.form.get('ids')
    ids = ids_input.split()
    ids_int = list(set(filter(lambda x: isinstance(x, int), map(to_int, ids))))
    if not ids_int:
        return jsonify(''), 400

    tvmaze.import_series_to_user(db.session, ids_int, current_user.id)

    return jsonify(ids_int)
