import urllib
import json

import showtracker.sqliteapi as db

from . import tvmaze as tvm


def get_updated_series_id_from_tvmaze():
    request = urllib.request.urlopen('https://api.tvmaze.com/updates/shows?since=week').read()
    raw = json.loads(request)
    return raw


def series_to_update(updated, series):
    show_to_update = set()
    for show in series:
        if show[2] in updated and (show[3] is None or int(show[3]) < int(updated[show[2]])):
            show_to_update.add(show)
        elif show[3] is None:
            show_to_update.add(show)
    return show_to_update


def update_series(to_import):
    print(f'Update series: {to_import}')

    for maze_id in to_import:
        try:
            show = tvm.get_show_from_maze(maze_id)
            print(show)
            episodes = tvm.get_episodes_from_maze(maze_id)
            print(f'episode count: {len(episodes)}')
            show.episodes = episodes
        except Exception as e:
            print(f'Error during fetch {maze_id}: {e}')
            continue

        print(f'Save show with mazeid {maze_id} to db')
        tvm.save(show)


def main():
    to_update = series_to_update(
        get_updated_series_id_from_tvmaze(),
        db.get_external_site_infos('tvmaze'))
    tvmaze_ids = {show[2] for show in to_update}
    update_series(tvmaze_ids)


if __name__ == '__main__':
    main()
