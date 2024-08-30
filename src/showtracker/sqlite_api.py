import datetime
from dataclasses import dataclass
from typing import Optional

from flask_sqlalchemy.session import Session
from sqlalchemy import text
from sqlalchemy.orm import scoped_session


@dataclass
class Episode:
    name: str
    season: int
    number: int
    airdate: Optional[datetime.datetime] = None


@dataclass
class Show:
    name: str
    episodes: Optional[list[Episode]] = None
    ids: Optional[dict[str, tuple]] = None
    premiered: Optional[datetime.date] = None
    ended: Optional[datetime.date] = None
    last_updated: Optional[int] = None


class SqliteApi:
    def __init__(self, session: scoped_session[Session]) -> None:
        self.session = session

    def _get_session(self):
        return self.session

    #

    def get_member_by_id(self, member_id: int):
        q1 = self._get_session().execute(
            text("SELECT * FROM Member WHERE member_id = :member_id"),
            {"member_id": member_id},
        )
        r = q1.fetchone()
        if r:
            return r._asdict()
        return None

    def get_member_by_name(self, name: str):
        q1 = self._get_session().execute(
            text("SELECT * FROM Member WHERE name = :name"),
            {"name": name},
        )
        r = q1.fetchone()
        if r:
            return r._asdict()
        return None

    #

    def get_series_details(self, series_id):
        session = self._get_session()

        q1 = session.execute(
            text(
                """
            SELECT
                S.series_id, S.name AS series_name, S.premiered, S.ended,
                (SELECT MAX(season) FROM Episode WHERE series_id = S.series_id) AS series_seasons,
                S_ES.externalsite_id AS external_site_name, S_ES.value as external_site_value
            FROM Series AS S
            LEFT JOIN Series_ExternalSite AS S_ES
                ON S.series_id = S_ES.series_id
            WHERE
                S.series_id = :sid
        """
            ),
            {"sid": series_id},
        )

        show = None
        for res in q1:
            res = res._asdict()
            if not show:
                show = {
                    "id": res["series_id"],
                    "name": res["series_name"],
                    "premiered": res["premiered"],
                    "ended": res["ended"],
                    "season_count": res["series_seasons"],
                    "external_sites": {},
                }
            show["external_sites"][res["external_site_name"]] = res[
                "external_site_value"
            ]

        return show

    def get_series_episodes(self, series_id):
        session = self._get_session()
        q1 = session.execute(
            text(
                "SELECT * FROM Episode AS E WHERE series_id = :sid ORDER BY E.season, E.number"
            ),
            {"sid": series_id},
        )

        seasons = dict()
        for res in q1:
            res = res._asdict()
            season = res["season"]
            if season not in seasons:
                seasons[season] = []
            seasons[season].append(
                {
                    "number": res["number"],
                    "name": res["name"],
                    "airstamp": res["airstamp"],
                }
            )

        return seasons

    def get_airdate(self, first_date, last_date):
        # +1 days because the date without time get 00:00 as hour, so only check before time 00:00 with <=
        session = self._get_session()
        q1 = session.execute(
            text(
                """
            SELECT *
            FROM v_Airdate
            WHERE
                airstamp BETWEEN date(:first_date) AND date(:last_date, "+1 days")
            ORDER BY series_name
        """
            ),
            {"first_date": first_date, "last_date": last_date},
        )

        shows = dict()
        for res in q1:
            res = res._asdict()
            show_id = res["series_id"]
            if show_id not in shows:
                shows[show_id] = {
                    "id": show_id,
                    "name": res["series_name"],
                    "episodes": [],
                }
            show = shows[show_id]

            ep = {
                "name": res["title"],
                "season": res["season"],
                "episode": res["number"],
                "airdate": datetime.datetime.fromisoformat(res["airstamp"]),
            }
            show["episodes"].append(ep)

        out = dict()
        out["start_date"] = first_date.isoformat()
        out["end_date"] = last_date.isoformat()
        out["series"] = list(shows.values())

        return out

    def get_member_airdate(self, first_date, last_date, member_id):
        # +1 days because the date without time get 00:00 as hour, so only check before time 00:00 with <=
        session = self._get_session()
        q1 = session.execute(
            text(
                """
            SELECT *
            FROM v_AirdateMember
            WHERE
                airstamp BETWEEN date(:first_date) AND date(:last_date, "+1 days")
                AND member_id = :member_id
            ORDER BY position
        """
            ),
            {"first_date": first_date, "last_date": last_date, "member_id": member_id},
        )

        shows = dict()
        for res in q1:
            res = res._asdict()
            show_id = res["series_id"]
            if show_id not in shows:
                shows[show_id] = {
                    "id": show_id,
                    "name": res["series_name"],
                    "episodes": [],
                }
            show = shows[show_id]

            ep = {
                "name": res["title"],
                "season": res["season"],
                "episode": res["number"],
                "airdate": datetime.datetime.fromisoformat(res["airstamp"]),
                "seen": res["status"] == 2,
            }
            show["episodes"].append(ep)

        out = dict()
        out["start_date"] = first_date.isoformat()
        out["end_date"] = last_date.isoformat()
        out["series"] = list(shows.values())
        out["member_id"] = member_id

        return out

    def get_following(self, member_id):
        session = self._get_session()
        q1 = session.execute(
            text(
                """
            SELECT *
            FROM v_Following
            WHERE
                member_id = :member_id
            ORDER BY position
        """
            ),
            {"member_id": member_id},
        )

        shows = dict()

        for res in q1:
            res = res._asdict()
            show_id = res["series_id"]
            if show_id not in shows:
                shows[show_id] = {
                    "name": res["series_name"],
                    "id": show_id,
                    "episodes": [],
                    "season_count": res["series_seasons"],
                    "season": res["season"],
                }
            show = shows[show_id]

            airstamp = res["airstamp"]
            ep_date = datetime.datetime.fromisoformat(airstamp) if airstamp else None
            ep = {
                "name": res["title"],
                "season": res["season"],
                "episode": res["number"],
                "airdate": ep_date,
                "seen": res["status"] == 2,
                "acquired": res["status"] == 1,
            }
            if ep["season"]:
                show["episodes"].append(ep)

        return {"data": list(shows.values()), "member_id": member_id}

    def set_season_status(self, member_id, series_id, season, status) -> bool:
        session = self._get_session()
        session.execute(
            text(
                """
            INSERT INTO Member_Episode(member_id, series_id, season, number, status)
            SELECT :member_id AS member_id, series_id, season, number, :status AS status FROM Episode AS E
                WHERE E.series_id = :series_id AND E.season = :season
            ON CONFLICT(member_id, series_id, season, number)
                DO UPDATE SET status=excluded.status
        """
            ),
            {
                "member_id": member_id,
                "status": status,
                "series_id": series_id,
                "season": season,
            },
        )
        session.commit()

        return True

    def set_episode_status(self, member_id, series_id, season, number, status) -> bool:
        session = self._get_session()
        session.execute(
            text(
                """
            INSERT INTO Member_Episode(member_id, series_id, season, number, status)
            VALUES(:member_id, :series_id, :season, :number, :status)
            ON CONFLICT(member_id, series_id, season, number)
                DO UPDATE SET status=excluded.status
        """
            ),
            {
                "member_id": member_id,
                "series_id": series_id,
                "season": season,
                "number": number,
                "status": status,
            },
        )
        session.commit()

        return True

    def select_season(self, member_id, show_id, selected_season) -> bool:
        session = self._get_session()
        session.execute(
            text(
                "UPDATE Member_Series SET selected_season = :selected_season WHERE member_id = :member_id AND series_id = :series_id"
            ),
            {
                "selected_season": selected_season,
                "member_id": member_id,
                "show_id": show_id,
            },
        )
        session.commit()
        return True

    def save_show_to_member(
        self, show_id, selected_season, position, member_id
    ) -> None:
        session = self._get_session()
        session.execute(
            text(
                "insert into Member_Series(member_id, series_id, selected_season, position) values(:member_id, :series_id, :selected_season, :position) on conflict(member_id, series_id) do update set selected_season=excluded.selected_season, position=excluded.position"
            ),
            {
                "member_id": member_id,
                "series_id": show_id,
                "selected_season": selected_season,
                "position": position,
            },
        )
        session.commit()

    #

    def get_external_site_infos(self, external_site: str):
        session = self._get_session()
        q1 = session.execute(
            text(
                "SELECT * FROM Series_ExternalSite WHERE externalsite_id = :external_site"
            ),
            {"external_site": external_site},
        )
        res = [res._asdict() for res in q1]
        return res

    def show_id_by_external_site_id(self, external_site_id: str, show_id: int):
        session = self._get_session()
        prev = session.execute(
            text(
                "select series_id from Series_ExternalSite where externalsite_id = :external_site_id and value = :show_id"
            ),
            {"show_id": show_id, "external_site_id": external_site_id},
        )
        stored_id = prev.fetchone()
        if stored_id:
            return stored_id[0]
        return None

    #

    def save_show_to_db_by_id(self, show_id: Optional[int], show: Show) -> int:
        session = self._get_session()
        prev_id = show_id
        res = session.execute(
            text(
                "insert into Series(series_id, name, premiered, ended) values(:series_id, :name, :premiered, :ended) on conflict(series_id) do update set name=excluded.name, premiered=excluded.premiered, ended=excluded.ended"
            ),
            {
                "series_id": prev_id,
                "name": show.name,
                "premiered": show.premiered,
                "ended": show.ended,
            },
        )
        session.commit()

        show_id = prev_id or res.lastrowid  # type: ignore
        if show.ids:
            session.execute(
                text(
                    "insert into Series_ExternalSite(series_id, externalsite_id, value, last_update) values(:series_id, :site_id, :value, :last_update) on conflict(series_id, externalsite_id) do update set value=excluded.value, last_update=excluded.last_update"
                ),
                [
                    {
                        "series_id": show_id,
                        "site_id": site_id,
                        "value": value[0],
                        "last_update": value[1],
                    }
                    for site_id, value in show.ids.items()
                    if value[0]
                ],
            )
            session.commit()

        return show_id

    def save_episodes_to_show(self, show_id: int, episodes: list[Episode]) -> None:
        session = self._get_session()
        session.execute(
            text(
                "insert into Episode(series_id, name, airstamp, season, number) values(:series_id, :name, :airdate, :season, :number) on conflict(series_id, season, number) do update set name=excluded.name, airstamp=excluded.airstamp"
            ),
            [
                {
                    "series_id": show_id,
                    "name": episode.name,
                    "airdate": episode.airdate,
                    "season": episode.season,
                    "number": episode.number,
                }
                for episode in episodes
            ],
        )
        session.commit()

    def save(self, show: Show) -> int:
        possible_id = None
        if show.ids:
            possible_id = self.show_id_by_external_site_id(
                "tvmaze", show.ids["tvmaze"][0]
            )
        show_id = self.save_show_to_db_by_id(possible_id, show)
        if show.episodes:
            self.save_episodes_to_show(show_id, show.episodes)

        return show_id
