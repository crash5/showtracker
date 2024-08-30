import datetime
import json
import urllib.request
from typing import Any

from . import sqlite_api


def to_show(show: dict[str, Any]) -> sqlite_api.Show:
    return sqlite_api.Show(
        show["name"],
        [],
        {
            "tvmaze": (show["id"], show["updated"]),
            "imdb": (show["externals"]["imdb"], None),
            "thetvdb": (show["externals"]["thetvdb"], None),
            "tvrage": (show["externals"]["tvrage"], None),
        },
        show["premiered"],
        show["ended"],
        show["updated"],
    )


def to_episode(episode: dict[str, Any]) -> sqlite_api.Episode:
    # cut off +00:00 with -6
    ep_date = (
        datetime.datetime.fromisoformat(episode["airstamp"][:-6])
        if episode["airstamp"]
        else None
    )
    return sqlite_api.Episode(
        episode["name"], episode["season"], episode["number"], ep_date
    )


def series_to_update(
    updated_tvmaze_ids: dict[str, int], available_series_infos: list[dict[str, str]]
) -> set[int]:
    show_to_update = set()
    for show in available_series_infos:
        if show["series_id"] in updated_tvmaze_ids and (
            show["last_update"] is None
            or int(show["last_update"]) < int(updated_tvmaze_ids[show["series_id"]])
        ):
            show_to_update.add(show)
        elif show["last_update"] is None:
            show_to_update.add(show["value"])
    return show_to_update


#


def get_show(show_id):
    request = urllib.request.urlopen(f"https://api.tvmaze.com/shows/{show_id}").read()
    return to_show(json.loads(request))


def get_episodes(show_id):
    request = urllib.request.urlopen(
        f"https://api.tvmaze.com/shows/{show_id}/episodes"
    ).read()
    # TODO: handle special episodes, without episode number
    # request = urllib.request.urlopen(f'https://api.tvmaze.com/shows/{show_id}/episodes/?specials=1').read()
    raw = json.loads(request)
    return [to_episode(episode) for episode in raw]


def get_updated_series_ids():
    request = urllib.request.urlopen(
        "https://api.tvmaze.com/updates/shows?since=week"
    ).read()
    raw = json.loads(request)
    return raw


#


def update_shows(api: sqlite_api.SqliteApi) -> set[int]:
    updated_on_maze: dict[str, int] = get_updated_series_ids()
    our_shows = api.get_external_site_infos("tvmaze")
    tvmaze_ids = series_to_update(updated_on_maze, our_shows)
    print(f"TVmaze shows to update: {tvmaze_ids}")
    for id in tvmaze_ids:
        print(f"Update tvmaze show: {id}")
        import_show(id, api)
    return tvmaze_ids


def import_show(show_id: int, api: sqlite_api.SqliteApi) -> int:
    show = get_show(show_id)
    show.episodes = get_episodes(show_id)
    return api.save(show)


def main():
    from . import flask_app, service

    app = flask_app.create_app()
    with app.app_context():
        api = service.get_service()
        # import_show(60153, api)
        # update_shows(api)


if __name__ == "__main__":
    main()
