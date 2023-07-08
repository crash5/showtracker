import sqlite3
import datetime

from .db import db, text


def get_connection(file='db.sqlite', mode='ro'):
    con = sqlite3.connect(f'file:{file}?mode={mode}', uri=True)
    con.execute('PRAGMA foreign_keys = true')
    con.row_factory = sqlite3.Row
    return con

def get_user_by_id(member_id):
    con = get_connection()
    q1 = con.execute('''
        SELECT * FROM Member WHERE member_id = ?
    ''', (member_id,))
    return q1.fetchone()

def get_user_by_name(name):
    con = get_connection()
    q1 = con.execute('''
        SELECT * FROM Member WHERE name = ?
    ''', (name,))
    return q1.fetchone()

def get_airdate(first_date, last_date, member_id):
    con = get_connection()

    # +1 days because the date without time get 00:00 as hour, so only check before time 00:00 with <=
    q1 = con.execute('''
        SELECT *
        FROM v_AirdateMember
        WHERE
            airstamp BETWEEN date(?) AND date(?, "+1 days")
            AND member_id = ?
        ORDER BY position
    ''', (first_date, last_date, member_id))

    shows = dict()
    for res in q1:
        show_id = res['series_id']
        if show_id not in shows:
            shows[show_id] = {
                'id': show_id,
                'name': res['series_name'],
                'episodes': [],
            }
        show = shows[show_id]

        ep ={
                "name": res['title'],
                "season": res['season'],
                "episode": res['number'],
                "airdate": datetime.datetime.fromisoformat(res['airstamp']),
                "seen": res['status'] == 2
        }
        show['episodes'].append(ep)

    out = dict()
    out['start_date'] = first_date.isoformat()
    out['end_date'] = last_date.isoformat()
    out['series'] = list(shows.values())

    con.close()
    return out


def get_following(member_id):
    con = get_connection()

    q1 = con.execute('''
        SELECT *
        FROM v_Following
        WHERE
        	member_id = ?
        ORDER BY position
    ''', (member_id,))

    shows = dict()

    for res in q1:
        show_id = res['series_id']
        if show_id not in shows:
            shows[show_id] = {
            "name": res['series_name'],
            "id": show_id,
            "episodes": [],
            "season_count": res['series_seasons'],
            "season": res['season']
            }
        show = shows[show_id]

        airstamp = res['airstamp']
        ep_date = datetime.datetime.fromisoformat(airstamp) if airstamp else None
        ep = {
            "name": res['title'],
            "season": res['season'],
            "episode": res['number'],
            "airdate": ep_date,
            "seen": res['status'] == 2,
            "acquired": res['status'] == 1
        }
        if ep['season']:
            show['episodes'].append(ep)

    con.close()
    return list(shows.values())

def get_series_details(series_id):
    con = get_connection()

    q1 = con.execute('''
        SELECT
        	S.series_id, S.name AS series_name, S.premiered, S.ended,
        	(SELECT MAX(season) FROM Episode WHERE series_id = S.series_id) AS series_seasons,
        	S_ES.externalsite_id AS external_site_name,	S_ES.value as external_site_value
        FROM Series AS S
        LEFT JOIN Series_ExternalSite AS S_ES
        	ON S.series_id = S_ES.series_id
        WHERE
            S.series_id = ?
    ''', (series_id,))

    show = None
    for res in q1:
        if not show:
            show = {
                'id': res['series_id'],
                "name": res['series_name'],
                'premiered': res['premiered'],
                'ended': res['ended'],
                'season_count': res['series_seasons'],
                'external_sites': {}
            }
        show['external_sites'][res['external_site_name']] = res['external_site_value']

    return show


def get_series_episodes(series_id):
    q1 = db.session.execute(
        text('SELECT * FROM Episode AS E WHERE series_id = :sid ORDER BY E.season, E.number'),
        {'sid': series_id}
    )

    seasons = dict()
    for res in q1:
        res = res._asdict()
        season = res['season']
        if season not in seasons:
            seasons[season] = []
        seasons[season].append({
            'number': res['number'],
            'name': res['name'],
            'airstamp': res['airstamp']
        })

    return seasons



def set_season_status(member_id, series_id, season, status):
    con = get_connection(mode='rw')
    con.execute('''
        INSERT INTO Member_Episode(member_id, series_id, season, number, status)
        SELECT ? AS member_id, series_id, season, number, ? AS status FROM Episode AS E
        	WHERE E.series_id = ? AND E.season = ?
        ON CONFLICT(member_id, series_id, season, number)
        	DO UPDATE SET status=excluded.status
    ''', (member_id, status, series_id, season))
    con.commit()

    return True

def set_episode_status(member_id, series_id, season, number, status):
    con = get_connection(mode='rw')
    con.execute('''
        INSERT INTO Member_Episode(member_id, series_id, season, number, status)
        VALUES(?, ?, ?, ?, ?)
        ON CONFLICT(member_id, series_id, season, number)
        	DO UPDATE SET status=excluded.status
    ''', (member_id, series_id, season, number, status))
    con.commit()

    return True




def get_external_site_infos(external_site):
    con = get_connection()
    q1 = con.execute(f'SELECT * FROM Series_ExternalSite WHERE externalsite_id = "{external_site}"')
    res = q1.fetchall()
    return list(res)

def show_id_by_external_site_id(external_site_id, show_id):
    con = get_connection()
    prev = con.execute(f'select series_id from Series_ExternalSite where externalsite_id = "{external_site_id}" and value = ?', (show_id,))
    stored_id = prev.fetchone()
    if stored_id:
        return stored_id[0]
    return None


def save_show_to_user(show_id, selected_season, position, member_id):
    con = get_connection(mode='rw')
    cursor = con.cursor()
    cursor.execute(
        'insert into Member_Series(member_id, series_id, selected_season, position) values(?, ?, ?, ?) on conflict(member_id, series_id) do update set selected_season=excluded.selected_season, position=excluded.position',
        (member_id, show_id, selected_season, position)
    )
    con.commit()
    cursor.close()

def select_season(member_id, show_id, selected_season):
    con = get_connection(mode='rw')
    con.execute(
        'UPDATE Member_Series SET selected_season = ? WHERE member_id = ? AND series_id = ?',
        (selected_season, member_id, show_id)
    )
    con.commit()
    return True
