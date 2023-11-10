from dataclasses import dataclass
import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text


@dataclass
class Episode:
    name: str
    season: int
    number: int
    airdate: Optional[datetime.datetime] = None


@dataclass
class Show:
    name: str
    episodes: Optional[List[Episode]] = None
    ids: Optional[Dict[str, Tuple]] = None
    premiered: Optional[datetime.date] = None
    ended: Optional[datetime.date] = None
    last_updated: Optional[int] = None


def get_user_by_id(session, member_id):
    q1 = session.execute(text('''
        SELECT * FROM Member WHERE member_id = :member_id
    '''), {'member_id': member_id})
    return q1.fetchone()._asdict()


def get_user_by_name(session, name):
    q1 = session.execute(text('''
        SELECT * FROM Member WHERE name = :name
    '''), {'name': name})
    return q1.fetchone()._asdict()


def get_airdate(session, first_date, last_date, member_id):
    # +1 days because the date without time get 00:00 as hour, so only check before time 00:00 with <=
    q1 = session.execute(text('''
        SELECT *
        FROM v_AirdateMember
        WHERE
            airstamp BETWEEN date(:first_date) AND date(:last_date, "+1 days")
            AND member_id = :member_id
        ORDER BY position
    '''), {'first_date': first_date, 'last_date': last_date, 'member_id': member_id})

    shows = dict()
    for res in q1:
        res = res._asdict()
        show_id = res['series_id']
        if show_id not in shows:
            shows[show_id] = {
                'id': show_id,
                'name': res['series_name'],
                'episodes': [],
            }
        show = shows[show_id]

        ep ={
                'name': res['title'],
                'season': res['season'],
                'episode': res['number'],
                'airdate': datetime.datetime.fromisoformat(res['airstamp']),
                'seen': res['status'] == 2
        }
        show['episodes'].append(ep)

    out = dict()
    out['start_date'] = first_date.isoformat()
    out['end_date'] = last_date.isoformat()
    out['series'] = list(shows.values())

    return out


def get_following(session, member_id):
    q1 = session.execute(text('''
        SELECT *
        FROM v_Following
        WHERE
            member_id = :member_id
        ORDER BY position
    '''), {'member_id': member_id})

    shows = dict()

    for res in q1:
        res = res._asdict()
        show_id = res['series_id']
        if show_id not in shows:
            shows[show_id] = {
                'name': res['series_name'],
                'id': show_id,
                'episodes': [],
                'season_count': res['series_seasons'],
                'season': res['season']
            }
        show = shows[show_id]

        airstamp = res['airstamp']
        ep_date = datetime.datetime.fromisoformat(airstamp) if airstamp else None
        ep = {
            'name': res['title'],
            'season': res['season'],
            'episode': res['number'],
            'airdate': ep_date,
            'seen': res['status'] == 2,
            'acquired': res['status'] == 1
        }
        if ep['season']:
            show['episodes'].append(ep)

    return list(shows.values())


def get_series_details(session, series_id):
    q1 = session.execute(text('''
        SELECT
            S.series_id, S.name AS series_name, S.premiered, S.ended,
            (SELECT MAX(season) FROM Episode WHERE series_id = S.series_id) AS series_seasons,
            S_ES.externalsite_id AS external_site_name, S_ES.value as external_site_value
        FROM Series AS S
        LEFT JOIN Series_ExternalSite AS S_ES
            ON S.series_id = S_ES.series_id
        WHERE
            S.series_id = :sid
    '''), {'sid': series_id})

    show = None
    for res in q1:
        res = res._asdict()
        if not show:
            show = {
                'id': res['series_id'],
                'name': res['series_name'],
                'premiered': res['premiered'],
                'ended': res['ended'],
                'season_count': res['series_seasons'],
                'external_sites': {}
            }
        show['external_sites'][res['external_site_name']] = res['external_site_value']

    return show


def get_series_episodes(session, series_id):
    q1 = session.execute(
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


def set_season_status(session, member_id, series_id, season, status):
    session.execute(text('''
        INSERT INTO Member_Episode(member_id, series_id, season, number, status)
        SELECT :member_id AS member_id, series_id, season, number, :status AS status FROM Episode AS E
            WHERE E.series_id = :series_id AND E.season = :season
        ON CONFLICT(member_id, series_id, season, number)
            DO UPDATE SET status=excluded.status
    '''), {
            'member_id': member_id,
            'status': status,
            'series_id': series_id,
            'season': season
        })
    session.commit()

    return True


def set_episode_status(session, member_id, series_id, season, number, status):
    session.execute(text('''
        INSERT INTO Member_Episode(member_id, series_id, season, number, status)
        VALUES(:member_id, :series_id, :season, :number, :status)
        ON CONFLICT(member_id, series_id, season, number)
            DO UPDATE SET status=excluded.status
    '''), {
        'member_id': member_id,
        'series_id': series_id,
        'season': season,
        'number': number,
        'status': status
        })
    session.commit()

    return True


def get_external_site_infos(session, external_site):
    q1 = session.execute(text('SELECT * FROM Series_ExternalSite WHERE externalsite_id = :external_site'), {'external_site': external_site})
    res = [res._asdict() for res in q1]
    return res


def show_id_by_external_site_id(session, external_site_id, show_id):
    prev = session.execute(text('select series_id from Series_ExternalSite where externalsite_id = :external_site_id and value = :show_id'), {'show_id': show_id, 'external_site_id': external_site_id})
    stored_id = prev.fetchone()
    if stored_id:
        return stored_id[0]
    return None


def save_show_to_user(session, show_id, selected_season, position, member_id):
    session.execute(
        text('insert into Member_Series(member_id, series_id, selected_season, position) values(:member_id, :series_id, :selected_season, :position) on conflict(member_id, series_id) do update set selected_season=excluded.selected_season, position=excluded.position'),
        {
            'member_id': member_id,
            'series_id': show_id,
            'selected_season': selected_season,
            'position': position
        }
    )
    session.commit()


def select_season(session, member_id, show_id, selected_season):
    session.execute(
        text('UPDATE Member_Series SET selected_season = :selected_season WHERE member_id = :member_id AND series_id = :series_id'),
    {'selected_season': selected_season, 'member_id': member_id, 'show_id': show_id}
    )
    session.commit()
    return True


def save_show_to_db_by_id(session, show_id: int, show: Show):
    prev_id = show_id
    res = session.execute(
        text('insert into Series(series_id, name, premiered, ended) values(:series_id, :name, :premiered, :ended) on conflict(series_id) do update set name=excluded.name, premiered=excluded.premiered, ended=excluded.ended'),
        {
            'series_id': prev_id,
            'name': show.name,
            'premiered': show.premiered,
            'ended': show.ended
        }
    )
    session.commit()

    show_id: int = prev_id or res.lastrowid
    session.execute(
        text('insert into Series_ExternalSite(series_id, externalsite_id, value, last_update) values(:series_id, :site_id, :value, :last_update) on conflict(series_id, externalsite_id) do update set value=excluded.value, last_update=excluded.last_update'),
        [
            {
                'series_id':show_id,
                'site_id':site_id,
                'value':value[0],
                'last_update':value[1]
            } for site_id, value in show.ids.items() if value[0]
        ]
    )
    session.commit()

    return show_id


def save_episodes_to_show(session, show_id: int, episodes: list[Episode]):
    session.execute(
        text('insert into Episode(series_id, name, airstamp, season, number) values(:series_id, :name, :airdate, :season, :number) on conflict(series_id, season, number) do update set name=excluded.name, airstamp=excluded.airstamp'),
        [
            {
                'series_id':show_id,
                'name':episode.name,
                'airdate':episode.airdate,
                'season':episode.season,
                'number':episode.number
            } for episode in episodes
        ]
    )
    session.commit()


def save(session, show: Show):
    possible_id = show_id_by_external_site_id(session, 'tvmaze', show.ids['tvmaze'][0])
    show_id = save_show_to_db_by_id(session, possible_id, show)
    save_episodes_to_show(session, show_id, show.episodes)

    return show_id
