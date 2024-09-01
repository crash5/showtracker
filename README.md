# showtracker _(showtracker)_

Basic install:
```
python -m venv .venv
source .venv/Scripts/activate

echo 'export FLASK_SECRET="very-secret-code"' >> .env
echo 'export DATABASE_URL="sqlite:///db.sqlite"' >> .env
echo 'export FLASK_INSTANCE_PATH="$(pwd)"' >> .env

# Gunicorn
echo 'export GUNICORN_HOST="0.0.0.0"' >> .env
echo 'export GUNICORN_PORT="80"' >> .env

flask init-db
flask run --debug
```

- Run for development: `flask run --debug`
- Initialize database: `flask init-db`

## Contributing

General Commands:
- Run test: `python -m pytest`
- Run mypy typecheck: `python -m mypy`
- Run flake8 style check: `python -m flake8 ./src`
- Run black code formatter: `black ./src`
