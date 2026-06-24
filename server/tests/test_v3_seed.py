from pathlib import Path
import json

from app.repositories.users import find_user_by_username
from scripts.seed_v3_demo import FIXTURE_PATH, SEED_TAG, seed_v3_demo


def _db(app):
    return app.extensions["mongo"].db


def test_v3_fixture_is_versioned_demo_data():
    assert FIXTURE_PATH.exists()

    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert len(data["users"]) == 10
    assert len(data["products"]) == 12
    assert len(data["trades"]) == 4
    assert len(data["announcements"]) == 3
    assert len(data["ai_logs"]) == 3


def test_v3_seed_writes_realistic_demo_data(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        summary = seed_v3_demo()
        db = _db(app)

        assert summary["users"] == 10
        assert summary["products"] == 12
        assert summary["trades"] == 4
        assert summary["announcements"] == 3

        admin = find_user_by_username("admin")
        blocked = find_user_by_username("blocked_user")
        assert admin["role"] == "admin"
        assert blocked["status"] == "disabled"

        products = list(db.products.find({"seed_tag": SEED_TAG}))
        assert len(products) == 12
        assert {product["category_key"] for product in products} == {
            "books",
            "electronics",
            "daily",
            "sports",
        }

        category_counts = {}
        image_urls = set()
        for product in products:
            category_counts[product["category_key"]] = category_counts.get(product["category_key"], 0) + 1
            assert product["images"]
            for url in product["images"]:
                image_urls.add(url)
                assert url.startswith("/uploads/images/v3-")
                image_path = Path(tmp_path) / url.replace("/uploads/", "")
                assert image_path.exists()
                assert image_path.stat().st_size > 0

        assert category_counts == {
            "books": 3,
            "electronics": 3,
            "daily": 3,
            "sports": 3,
        }
        assert len(image_urls) == 12
        assert db.products.count_documents({"seed_tag": SEED_TAG, "status": "sold"}) == 1
        assert db.products.count_documents({"seed_tag": SEED_TAG, "status": "off_shelf"}) == 1

        assert {
            item["status"]
            for item in db.trade_requests.find({"seed_tag": SEED_TAG}, {"status": 1})
        } == {"pending", "confirmed", "completed", "cancelled"}
        assert db.messages.count_documents({"seed_tag": SEED_TAG}) == 8
        assert db.announcements.count_documents({"seed_tag": SEED_TAG}) == 3
        assert db.operation_logs.count_documents({"seed_tag": SEED_TAG}) == 2
        assert db.ai_generation_logs.count_documents({"seed_tag": SEED_TAG}) == 3


def test_v3_seed_is_repeatable(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        seed_v3_demo()
        seed_v3_demo()
        db = _db(app)

        assert db.products.count_documents({"seed_tag": SEED_TAG}) == 12
        assert db.trade_requests.count_documents({"seed_tag": SEED_TAG}) == 4
        assert db.messages.count_documents({"seed_tag": SEED_TAG}) == 8
        assert db.announcements.count_documents({"seed_tag": SEED_TAG}) == 3
        assert db.ai_generation_logs.count_documents({"seed_tag": SEED_TAG}) == 3
