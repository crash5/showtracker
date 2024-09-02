import os

import dotenv
from flask import Flask

from . import api, auth, db, log, scheduler, web


def create_app(config="prod", instance_path=None, config_file=None):
    dotenv.load_dotenv(override=False)

    env_instance_path = os.environ.get("FLASK_INSTANCE_PATH")
    inst_path = env_instance_path or instance_path
    app = Flask(
        __name__,
        static_url_path="",
        instance_relative_config=True,
        instance_path=inst_path,
    )
    app.config.from_object(f"showtracker.config.{config.capitalize()}")
    if config_file:
        app.config.from_pyfile(config_file)
    app.config.from_envvar("FLASK_CONFIG_FILE", silent=True)

    log.init_app(app)
    db.init_app(app)
    auth.init_app(app)
    scheduler.init_app(app)

    app.register_blueprint(api.bp, url_prefix="/api")
    app.register_blueprint(web.bp)

    return app
