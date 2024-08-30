# showtracker _(showtracker)_

Basic install:
```
python -m venv .venv
source .venv/Scripts/activate

echo 'export FLASK_SECRET="very-secret-code"' >> .env
echo 'export DATABASE_URL="sqlite:///db.sqlite"' >> .env

flask init-db
flask run --debug
```

- Run for development: `flask run --debug`
- Initialize database: `flask init-db`

Set env. variables in `.env` file, like:
- export FLASK_SECRET="very-secret-thing"
- export DATABASE_URL="sqlite:///st-db.sqlite"


## Contributing

General Commands:
- Run test: `python -m pytest`
- Run mypy typecheck: `python -m mypy`
- Run flake8 style check: `python -m flake8 ./src`
- Run black code formatter: `black ./src`
