from flask import current_app
from pymongo import ASCENDING, ReturnDocument


DEFAULT_CATEGORIES = [
    {"key": "books", "name": "教材资料", "sort_order": 10},
    {"key": "electronics", "name": "电子产品", "sort_order": 20},
    {"key": "daily", "name": "生活用品", "sort_order": 30},
    {"key": "sports", "name": "运动器材", "sort_order": 40},
]


def _collection():
    return current_app.extensions["mongo"].db.categories


def ensure_category_indexes():
    if current_app.extensions.get("categories_indexes_ready"):
        return

    categories = _collection()
    categories.create_index([("key", ASCENDING)], unique=True, name="uniq_categories_key")
    categories.create_index(
        [("is_active", ASCENDING), ("sort_order", ASCENDING)],
        name="idx_categories_active_sort",
    )
    current_app.extensions["categories_indexes_ready"] = True


def serialize_category(category):
    if not category:
        return None

    return {
        "id": str(category["_id"]),
        "key": category["key"],
        "name": category["name"],
        "sort_order": category.get("sort_order", 0),
        "is_active": category.get("is_active", True),
    }


def ensure_default_categories():
    ensure_category_indexes()
    if _collection().find_one({}) is None:
        return upsert_default_categories()
    return []


def list_categories(include_inactive=False):
    ensure_default_categories()
    query = {} if include_inactive else {"is_active": True}
    cursor = _collection().find(query).sort([("sort_order", ASCENDING), ("name", ASCENDING)])
    return [serialize_category(category) for category in cursor]


def find_category_by_key(key):
    ensure_default_categories()
    return _collection().find_one({"key": key, "is_active": True})


def upsert_default_categories():
    ensure_category_indexes()
    results = []
    for category in DEFAULT_CATEGORIES:
        document = _collection().find_one_and_update(
            {"key": category["key"]},
            {
                "$set": {
                    "name": category["name"],
                    "sort_order": category["sort_order"],
                    "is_active": True,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        results.append(document)
    return results
