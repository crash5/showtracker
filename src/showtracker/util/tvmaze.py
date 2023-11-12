import datetime
import json
import urllib.request

import showtracker.sqliteapi as db


def import_series_to_user(session, to_import, member_id):
    print(f'Import series: {to_import}')
    for maze_id in to_import:
        try:
            show = get_show_from_maze(maze_id)
            print(show)
            episodes = get_episodes_from_maze(maze_id)
            print(f'episode count: {len(episodes)}')
            show.episodes = episodes
        except Exception as e:
            print(f'Error during fetch {maze_id}: {e}')
            continue

        print(f'Save show with mazeid {maze_id} to DB')
        show_id = db.save(session, show)
        print(f'Save Show({show_id}) to User({member_id})')
        db.save_show_to_user(session, show_id, 1, 1, member_id)


def tvmaze_to_episode(episode):
    # cut off +00:00 with -6
    ep_date = datetime.datetime.fromisoformat(episode['airstamp'][:-6]) if episode['airstamp'] else None
    return db.Episode(
        episode['name'],
        episode['season'],
        episode['number'],
        ep_date
    )


def tvmaze_to_show(show):
    return db.Show(
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


def get_updated_series_id_from_tvmaze():
    request = urllib.request.urlopen('https://api.tvmaze.com/updates/shows?since=week').read()
    raw = json.loads(request)
    return raw


def series_to_update(updated, series):
    show_to_update = set()
    for show in series:
        if show['series_id'] in updated and (show['last_update'] is None or int(show['last_update']) < int(updated[show['series_id']])):
            show_to_update.add(show)
        elif show['last_update'] is None:
            show_to_update.add(show)
    return show_to_update


def import_shows(session, to_import):
    print(f'Update series: {to_import}')

    for maze_id in to_import:
        try:
            show = get_show_from_maze(maze_id)
            print(show)
            episodes = get_episodes_from_maze(maze_id)
            print(f'episode count: {len(episodes)}')
            show.episodes = episodes
        except Exception as e:
            print(f'Error during fetch {maze_id}: {e}')
            continue

        print(f'Save show with mazeid {maze_id} to db')
        db.save(session, show)


def update_shows(session):
    to_update = series_to_update(
        get_updated_series_id_from_tvmaze(),
        db.get_external_site_infos(session, 'tvmaze'))
    tvmaze_ids = {show['series_id'] for show in to_update}
    import_shows(session, tvmaze_ids)


def main():
    import os
    from pathlib import Path
    from sqlalchemy import create_engine

# TODO(crash): get it from config file
    db_path = Path(os.getcwd()).resolve() / 'db.sqlite'
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as conn:
        update_shows(conn)


if __name__ == '__main__':
    main()
