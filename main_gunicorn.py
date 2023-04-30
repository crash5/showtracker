# without install
# from pathlib import Path
# package_path = Path(__file__).resolve().parent / 'src'
# sys.path.append(package_path)

import gunicorn.app.base

from showtracker.flask_app import app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    options = {
        'bind': '%s:%s' % ('0.0.0.0', '32019'),
        'workers': 1,
        'daemon': True,
        'loglevel': 'debug',
    }
    StandaloneApplication(app, options).run()
