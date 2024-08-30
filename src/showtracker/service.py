from . import db, sqlite_api


def get_service() -> sqlite_api.SqliteApi:
    return sqlite_api.SqliteApi(db.get_db())
