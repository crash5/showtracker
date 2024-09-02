# To use without package install:
# from pathlib import Path
# package_path = Path(__file__).resolve().parent / 'src'
# sys.path.append(package_path)

import os
from typing import Any

import dotenv
import gunicorn.app.base

import showtracker.flask_app as st_app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app):
        self.application = app
        self.options = {
            "bind": "127.0.0.1:80",
            "workers": 1,
            "daemon": True,
            "loglevel": "debug",
            "preload_app": True,
        }
        env_options = self._collect_gunicorn_options(os.environ)
        self.options.update(env_options)
        super().__init__()

    def load_config(self):
        if not self.cfg:
            return
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    def _collect_gunicorn_options(self, inp) -> dict[str, Any]:
        GUNICORN_PREFIX: str = "GUNICORN_"
        options: dict[str, Any] = {}
        key: str
        value: Any
        for key, value in dict(inp).items():
            if not key.startswith(GUNICORN_PREFIX):
                continue
            name = key[len(GUNICORN_PREFIX) :].lower()
            options[name] = value

        return options


if __name__ == "__main__":
    dotenv.load_dotenv(override=False)
    StandaloneApplication(st_app.create_app()).run()
