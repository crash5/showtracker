import pytest
from flask import current_app, g, request

from showtracker.flask_app import create_app


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app("test")
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


def test_one(test_client):
    response = test_client.get("/api/series/1")
    assert response.status_code == 200
    assert response.json == {"a": 5}
