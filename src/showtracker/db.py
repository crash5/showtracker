import click
from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
from sqlalchemy import Engine, event
from sqlalchemy.orm.scoping import scoped_session

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = true")
    cursor.close()


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.teardown_appcontext(close_db)


def get_db() -> scoped_session[Session]:
    if "db" not in g:
        g.db = db.session
    return g.db


def close_db(e=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("db/schema.sql") as f:
        db.connection().connection.dbapi_connection.executescript(  # type: ignore
            f.read().decode("utf8")
        )


@click.command("init-db")
def init_db_command():
    """Create the showtracker database."""
    init_db()
    click.echo("Database initialized.")
