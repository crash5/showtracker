from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy.engine import Engine
from sqlalchemy import event


db = SQLAlchemy()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = true")
    cursor.close()
