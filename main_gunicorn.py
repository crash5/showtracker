# without install
# from pathlib import Path
# package_path = Path(__file__).resolve().parent / 'src'
# sys.path.append(package_path)

from pathlib import Path
import dotenv
import gunicorn.app.base

import showtracker.flask_app as st_app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
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

    instance_path = Path(os.environ.get("FLASK_INSTANCE_PATH")) or sys.exit(
        'Set "FLASK_INSTANCE_PATH" env. variable!'
    )
    listen_host = os.environ.get("GUNICORN_HOST") or sys.exit(
        'Set "GUNICORN_HOST" env. variable!'
    )
    listen_port = os.environ.get("GUNICORN_PORT") or sys.exit(
        'Set "GUNICORN_PORT" env. variable!'
    )


    options = {
        "bind": f"{listen_host}:{listen_port}",
        "workers": 1,
        "daemon": True,
        "loglevel": "debug"
    }

    keyfile = instance_path / "server.key",
    certfile = instance_path / "server.pem",
    if keyfile.isfile() and certfile.isfile():
        options.update({
            "keyfile": keyfile,
            "certfile": certfile
        })

    StandaloneApplication(st_app.create_app("prod"), options).run()
