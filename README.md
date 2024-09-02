# ShowTracker _(showtracker)_

## Basic install for use:

```
python -m venv .venv
source .venv/Scripts/activate
pip install .

cat <<- EOF > config.prod.py
SECRET_KEY = "very-secure-secret"
SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"
EOF

cat <<- EOF > .env
FLASK_INSTANCE_PATH="$(pwd)"
FLASK_CONFIG_FILE=\${FLASK_INSTANCE_PATH}/config.prod.py

GUNICORN_BIND="127.0.0.1:80"
GUNICORN_WORKERS=2

GUNICORN_ACCESSLOG=\${FLASK_INSTANCE_PATH}/gunicorn-access.log
GUNICORN_ERRORLOG=\${FLASK_INSTANCE_PATH}/gunicorn.log
#GUNICORN_KEYFILE=\${FLASK_INSTANCE_PATH}/server.key
#GUNICORN_CERTFILE=\${FLASK_INSTANCE_PATH}/server.crt
EOF

flask init-db
flask run --debug
```


## Contributing

General Commands:
- Install as editable package: `pip install -e .[dev]`
- Run for development: `flask run --debug`
- Initialize database: `flask init-db`
- Run test: `python -m pytest`
- Run mypy typecheck: `python -m mypy`
- Run flake8 style check: `python -m flake8 ./src`
- Run black code formatter: `black ./src`
