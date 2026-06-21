from flask_cors import CORS
from pymongo import MongoClient


class MongoConnection:
    def __init__(self, uri, database_name, timeout_ms):
        self.client = MongoClient(
            uri,
            connect=False,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
        )
        self.db = self.client[database_name]

    def ping(self):
        return self.client.admin.command("ping")


def init_extensions(app):
    CORS(
        app,
        resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}},
    )
    app.extensions["mongo"] = MongoConnection(
        uri=app.config["MONGO_URI"],
        database_name=app.config["MONGO_DB_NAME"],
        timeout_ms=app.config["MONGO_TIMEOUT_MS"],
    )

