# ShowTracker _(showtracker)_

## Basic install for use:

```
python -m venv .venv
source .venv/Scripts/activate
pip install .

cat <<- EOF > .env
export FLASK_INSTANCE_PATH="$(pwd)"
export FLASK_SECRET="very-secure-secret"
export DATABASE_URL="sqlite:///db.sqlite"

export GUNICORN_BIND="0.0.0.0:80"
export GUNICORN_WORKERS=2

export GUNICORN_KEYFILE=\${FLASK_INSTANCE_PATH}/server.key
export GUNICORN_CERTFILE=\${FLASK_INSTANCE_PATH}/server.crt
export GUNICORN_ACCESSLOG=\${FLASK_INSTANCE_PATH}/gunicorn-access.log
export GUNICORN_ERRORLOG=\${FLASK_INSTANCE_PATH}/gunicorn.log
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
