# ShowTracker _(showtracker)_

Basic install for use:
```
python -m venv .venv
source .venv/Scripts/activate
pip install .

cat <<- EOF > .env
export FLASK_SECRET="very-secret-code"
export DATABASE_URL="sqlite:///db.sqlite"
export FLASK_INSTANCE_PATH="$(pwd)"
export GUNICORN_HOST="0.0.0.0"
export GUNICORN_PORT="80"
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
