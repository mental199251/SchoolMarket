import re

from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from app.repositories.users import serialize_user, utc_now_iso


def _collection():
    return current_app.extensions["mongo"].db.products


def _users_collection():
    return current_app.extensions["mongo"].db.users


def ensure_product_indexes():
    if current_app.extensions.get("products_indexes_ready"):
        return

    products = _collection()
    products.create_index(
        [("status", ASCENDING), ("created_at", DESCENDING)],
        name="idx_products_status_created",
    )
    products.create_index([("owner_id", ASCENDING)], name="idx_products_owner")
    products.create_index([("category_key", ASCENDING)], name="idx_products_category")
    products.create_index([("condition", ASCENDING)], name="idx_products_condition")
    products.create_index([("price_cents", ASCENDING)], name="idx_products_price")
    current_app.extensions["products_indexes_ready"] = True


def _to_object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def _owner_summary(owner_id):
    owner = _users_collection().find_one({"_id": owner_id})
    public = serialize_user(owner)
    if not public:
        return None
    return {
        "id": public["id"],
        "username": public["username"],
        "nickname": public["nickname"],
        "campus": public["campus"],
    }


def serialize_product(product):
    if not product:
        return None

    return {
        "id": str(product["_id"]),
        "owner_id": str(product["owner_id"]),
        "owner": _owner_summary(product["owner_id"]),
        "title": product["title"],
        "description": product.get("description", ""),
        "price_cents": product["price_cents"],
        "category_key": product["category_key"],
        "category_name": product.get("category_name", ""),
        "condition": product["condition"],
        "images": product.get("images", []),
        "status": product.get("status", "available"),
        "created_at": product.get("created_at"),
        "updated_at": product.get("updated_at"),
    }


def create_product(owner_id, data):
    ensure_product_indexes()
    now = utc_now_iso()
    document = {
        "owner_id": ObjectId(owner_id),
        "title": data["title"],
        "description": data.get("description", ""),
        "price_cents": data["price_cents"],
        "category_key": data["category_key"],
        "category_name": data["category_name"],
        "condition": data["condition"],
        "images": data.get("images", []),
        "status": "available",
        "created_at": now,
        "updated_at": now,
        "deleted_at": None,
    }
    result = _collection().insert_one(document)
    document["_id"] = result.inserted_id
    return document


def list_products(filters):
    ensure_product_indexes()
    query = {"deleted_at": None}

    if filters.get("owner_id"):
        query["owner_id"] = ObjectId(filters["owner_id"])
        if filters.get("status"):
            query["status"] = filters["status"]
    else:
        query["status"] = "available"

    if filters.get("keyword"):
        keyword = re.escape(filters["keyword"])
        query["$or"] = [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"description": {"$regex": keyword, "$options": "i"}},
        ]
    if filters.get("category_key"):
        query["category_key"] = filters["category_key"]
    if filters.get("condition"):
        query["condition"] = filters["condition"]

    price_query = {}
    if filters.get("min_price_cents") is not None:
        price_query["$gte"] = filters["min_price_cents"]
    if filters.get("max_price_cents") is not None:
        price_query["$lte"] = filters["max_price_cents"]
    if price_query:
        query["price_cents"] = price_query

    sort = filters.get("sort") or "newest"
    sort_spec = {
        "price_asc": [("price_cents", ASCENDING), ("created_at", DESCENDING)],
        "price_desc": [("price_cents", DESCENDING), ("created_at", DESCENDING)],
        "newest": [("created_at", DESCENDING)],
    }.get(sort, [("created_at", DESCENDING)])

    page = filters["page"]
    page_size = filters["page_size"]
    total = _collection().count_documents(query)
    cursor = (
        _collection()
        .find(query)
        .sort(sort_spec)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    return {
        "items": [serialize_product(product) for product in cursor],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def find_product_by_id(product_id):
    ensure_product_indexes()
    object_id = _to_object_id(product_id)
    if not object_id:
        return None
    return _collection().find_one({"_id": object_id, "deleted_at": None})


def update_product(product_id, data):
    ensure_product_indexes()
    now = utc_now_iso()
    update_fields = {
        "title": data["title"],
        "description": data.get("description", ""),
        "price_cents": data["price_cents"],
        "category_key": data["category_key"],
        "category_name": data["category_name"],
        "condition": data["condition"],
        "images": data.get("images", []),
        "updated_at": now,
    }
    return _collection().find_one_and_update(
        {"_id": ObjectId(product_id), "deleted_at": None},
        {"$set": update_fields},
        return_document=ReturnDocument.AFTER,
    )


def update_product_status(product_id, status):
    ensure_product_indexes()
    now = utc_now_iso()
    return _collection().find_one_and_update(
        {"_id": ObjectId(product_id), "deleted_at": None},
        {"$set": {"status": status, "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )


def mark_product_sold(product_id):
    ensure_product_indexes()
    now = utc_now_iso()
    return _collection().find_one_and_update(
        {
            "_id": ObjectId(product_id),
            "deleted_at": None,
            "status": {"$ne": "sold"},
        },
        {"$set": {"status": "sold", "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )


def delete_product(product_id):
    ensure_product_indexes()
    now = utc_now_iso()
    return _collection().find_one_and_update(
        {"_id": ObjectId(product_id), "deleted_at": None},
        {"$set": {"deleted_at": now, "status": "off_shelf", "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )


def upsert_sample_product(owner_id, data):
    ensure_product_indexes()
    now = utc_now_iso()
    return _collection().find_one_and_update(
        {
            "owner_id": ObjectId(owner_id),
            "title": data["title"],
            "deleted_at": None,
        },
        {
            "$set": {
                "description": data.get("description", ""),
                "price_cents": data["price_cents"],
                "category_key": data["category_key"],
                "category_name": data["category_name"],
                "condition": data["condition"],
                "images": data.get("images", []),
                "status": data.get("status", "available"),
                "updated_at": now,
            },
            "$setOnInsert": {
                "owner_id": ObjectId(owner_id),
                "title": data["title"],
                "created_at": now,
                "deleted_at": None,
            },
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
