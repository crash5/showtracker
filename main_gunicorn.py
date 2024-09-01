# without install
# from pathlib import Path
# package_path = Path(__file__).resolve().parent / 'src'
# sys.path.append(package_path)
import multiprocessing
import os
from pathlib import Path
import dotenv
import gunicorn.app.base

import showtracker.flask_app as st_app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app):
        self.application = app

        instance_path = Path(os.environ.get("FLASK_INSTANCE_PATH")) or sys.exit(
            'Set "FLASK_INSTANCE_PATH" env. variable!'
        )
        listen_host = os.environ.get("GUNICORN_HOST") or sys.exit(
            'Set "GUNICORN_HOST" env. variable!'
        )
        listen_port = os.environ.get("GUNICORN_PORT") or sys.exit(
            'Set "GUNICORN_PORT" env. variable!'
        )

        self.options = {
            "bind": f"{listen_host}:{listen_port}",
            "workers": (multiprocessing.cpu_count() * 2) + 1,
            "daemon": True,
            "loglevel": "debug",
            "accesslog": (instance_path / "access.log").absolute().as_posix(),
            "errorlog": (instance_path / "error.log").absolute().as_posix(),
        }

        keyfile = instance_path / "server.key"
        certfile = instance_path / "server.crt"
        if keyfile.is_file() and certfile.is_file():
            self.options.update({
                "keyfile": keyfile.absolute().as_posix(),
                "certfile": certfile.absolute().as_posix(),
            })
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":
    dotenv.load_dotenv(override=False)
    StandaloneApplication(st_app.create_app("prod")).run()
