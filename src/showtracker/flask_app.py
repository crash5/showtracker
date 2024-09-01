import os
import sys
from pathlib import Path

import dotenv
from flask import Flask

from . import api, auth, db, log, scheduler, web


def create_app(config="dev"):
    # load .env content as environment variable, do not overwrite variables which already exists from env.
    dotenv.load_dotenv(override=False)

    # can't set it from config
    instance_path = Path(os.environ.get("FLASK_INSTANCE_PATH")) or sys.exit(  # type: ignore
        'Set "FLASK_INSTANCE_PATH" env. variable!'
    )

    app = Flask(
        __name__,
        static_url_path="",
        instance_relative_config=True,
        instance_path=instance_path,  # type: ignore
    )
    app.config.from_object(f"showtracker.config.{config.capitalize()}")

    log.init_app(app)
    db.init_app(app)
    auth.init_app(app)
    scheduler.init_app(app)

    app.register_blueprint(api.bp, url_prefix="/api")
    app.register_blueprint(web.bp)

    return app
