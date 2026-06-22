import pytest
import mongomock

from app import create_app


@pytest.fixture()
def app():
    app = create_app(
        "testing",
        {
            "MONGO_URI": "mongodb://127.0.0.1:27017/?directConnection=true",
            "MONGO_DB_NAME": "school_market_test",
            "MONGO_TIMEOUT_MS": 10,
            "JWT_SECRET_KEY": "test-secret",
            "JWT_EXPIRES_SECONDS": 3600,
            "PROPAGATE_EXCEPTIONS": False,
        },
    )
    app.extensions["mongo"].db = mongomock.MongoClient()["school_market_test"]
    app.extensions.pop("users_indexes_ready", None)
    app.extensions.pop("categories_indexes_ready", None)
    app.extensions.pop("products_indexes_ready", None)
    app.extensions.pop("trades_indexes_ready", None)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
