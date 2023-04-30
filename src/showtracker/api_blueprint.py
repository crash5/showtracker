from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from .sqliteapi import get_airdate, get_following, set_season_status, set_episode_status, get_series_details, select_season


bp = Blueprint('api', __name__)


@bp.route('/series/<int:series_id>', methods=['GET'])
def series(series_id):
    series = get_series_details(series_id)
    if not series:
        return jsonify({'error': 'Series not found!'}), 404
    return jsonify(series)



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

    show_dict = get_airdate(first_date, last_date, member_id)
    show_dict['user_id'] = member_id
    return jsonify(show_dict)

@bp.route('/users/<int:member_id>/following')
def following(member_id):
    member_id = 1
    shows = dict()
    shows['data'] = get_following(member_id)
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
        set_season_status(member_id, series_id, season, 2)
        return jsonify(''), 200
    return jsonify(''), 404


@bp.route('/users/<int:member_id>/series/<int:series_id>/seasons/<int:season>/episodes/<int:episode>', methods=['PATCH'])
@login_required
def user_series_season_episode_patch(member_id, series_id, season, episode):
    if member_id != current_user.id:
        return jsonify('Wrong user'), 401

    body = request.get_json(force=True)
    if body.get('status') == 'seen':
        set_episode_status(member_id, series_id, season, episode, 2)
        return jsonify(''), 200

    if body.get('status') == 'unseen':
        # TODO: delete instead of change to 0
        set_episode_status(member_id, series_id, season, episode, 0)
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
        select_season(member_id, series_id, selected_season)
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
    # current_user.id
    ids_input = request.form.get('ids')
    ids = ids_input.split()
    ids_int = list(filter(lambda x: isinstance(x, int), map(to_int, ids)))
    if not ids_int:
        return jsonify(''), 400

    return jsonify(ids_int)
