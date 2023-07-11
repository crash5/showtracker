import datetime
import sqlite3
import json
import urllib.request
import typing
from dataclasses import dataclass
from typing import Optional, Tuple

import showtracker.sqliteapi as db


@dataclass
class Episode:
    name: str
    season: int
    number: int
    airdate: Optional[datetime.datetime] = None


@dataclass
class Show:
    name: str
    episodes: Optional[typing.List[Episode]] = None
    ids: Optional[typing.Dict[str, Tuple]] = None
    premiered: Optional[datetime.date] = None
    ended: Optional[datetime.date] = None
    last_updated: Optional[int] = None



con = sqlite3.connect('db.sqlite', check_same_thread=False)


def save_show_to_db_by_id(show_id, show):
    cursor = con.cursor()

    prev_id = show_id
    cursor.execute(
        'insert into Series(series_id, name, premiered, ended) values(?, ?, ?, ?) on conflict(series_id) do update set name=excluded.name, premiered=excluded.premiered, ended=excluded.ended',
        (prev_id, show.name, show.premiered, show.ended)
    )

    show_id = prev_id or cursor.lastrowid
    cursor.executemany(
        'insert into Series_ExternalSite(series_id, externalsite_id, value, last_update) values(?, ?, ?, ?) on conflict(series_id, externalsite_id) do update set value=excluded.value, last_update=excluded.last_update',
        [(show_id, site_id, value[0], value[1]) for site_id, value in show.ids.items() if value[0]]
    )

    con.commit()
    cursor.close()
    return show_id

def save_show_to_db(show):
    prev_id = db.show_id_by_external_site_id('tvmaze', show.ids['tvmaze'][0])
    return save_show_to_db_by_id(prev_id, show)

def save_multiple_episode_to_db(show_id, episodes):
    cursor = con.cursor()

    cursor.executemany(
        'insert into Episode(series_id, name, airstamp, season, number) values(?, ?, ?, ?, ?) on conflict(series_id, season, number) do update set name=excluded.name, airstamp=excluded.airstamp',
        [(show_id, episode.name, episode.airdate, episode.season, episode.number) for episode in episodes]
    )

    con.commit()
    cursor.close()

def save(show):
    show_id = save_show_to_db(show)
    save_multiple_episode_to_db(show_id, show.episodes)
    return show_id



def tvmaze_to_episode(episode):
    # cut off +00:00 with -6
    ep_date = datetime.datetime.fromisoformat(episode['airstamp'][:-6]) if episode['airstamp'] else None
    return Episode(
        episode['name'],
        episode['season'],
        episode['number'],
        ep_date
    )


def tvmaze_to_show(show):
    return Show(
        show['name'],
        [],
        {
            'tvmaze': (show['id'], show['updated']),
            'imdb': (show['externals']['imdb'], None),
            'thetvdb': (show['externals']['thetvdb'], None),
            'tvrage': (show['externals']['tvrage'], None)
        },
        show['premiered'],
        show['ended'],
        show['updated']
    )


def get_show_from_maze(show_id):
    request = urllib.request.urlopen(f'https://api.tvmaze.com/shows/{show_id}').read()
    return tvmaze_to_show(json.loads(request))


def get_episodes_from_maze(show_id):
    request = urllib.request.urlopen(f'https://api.tvmaze.com/shows/{show_id}/episodes').read()
    # TODO: handle special episodes, without episode number
    # request = urllib.request.urlopen(f'https://api.tvmaze.com/shows/{show_id}/episodes/?specials=1').read()
    raw = json.loads(request)
    return [tvmaze_to_episode(episode) for episode in raw]
