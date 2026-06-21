import pytest

from app import create_app


@pytest.fixture()
def app():
    return create_app(
        "testing",
        {
            "MONGO_URI": "mongodb://127.0.0.1:27017/?directConnection=true",
            "MONGO_DB_NAME": "school_market_test",
            "MONGO_TIMEOUT_MS": 10,
            "PROPAGATE_EXCEPTIONS": False,
        },
    )


@pytest.fixture()
def client(app):
    return app.test_client()
