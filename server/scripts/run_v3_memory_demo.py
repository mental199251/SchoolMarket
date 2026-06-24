from pathlib import Path
import sys

import mongomock


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from scripts.seed_v3_demo import seed_v3_demo


LOCAL_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]


def create_memory_demo_app():
    app = create_app(
        "development",
        {
            "MONGO_URI": "mongodb://127.0.0.1:27017/?directConnection=true",
            "MONGO_DB_NAME": "school_market_v3_memory",
            "MONGO_TIMEOUT_MS": 10,
            "CORS_ORIGINS": LOCAL_CORS_ORIGINS,
        },
    )

    mongo_client = mongomock.MongoClient()
    app.extensions["mongo"].client = mongo_client
    app.extensions["mongo"].db = mongo_client["school_market_v3_memory"]
    for key in list(app.extensions.keys()):
        if key.endswith("_indexes_ready"):
            app.extensions.pop(key, None)

    with app.app_context():
        seed_v3_demo()

    return app


def main():
    app = create_memory_demo_app()
    print("V3 memory demo backend ready: http://127.0.0.1:5001", flush=True)
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
