from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from app.repositories.products import serialize_product
from app.repositories.users import serialize_user, utc_now_iso


ACTIVE_TRADE_STATUSES = {"pending", "confirmed"}


def _collection():
    return current_app.extensions["mongo"].db.trade_requests


def _products_collection():
    return current_app.extensions["mongo"].db.products


def _users_collection():
    return current_app.extensions["mongo"].db.users


def ensure_trade_indexes():
    if current_app.extensions.get("trades_indexes_ready"):
        return

    trades = _collection()
    trades.create_index(
        [("buyer_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
        name="idx_trades_buyer_status_created",
    )
    trades.create_index(
        [("seller_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
        name="idx_trades_seller_status_created",
    )
    trades.create_index(
        [("product_id", ASCENDING), ("status", ASCENDING)],
        name="idx_trades_product_status",
    )
    trades.create_index(
        [("buyer_id", ASCENDING), ("product_id", ASCENDING), ("status", ASCENDING)],
        name="idx_trades_buyer_product_status",
    )
    current_app.extensions["trades_indexes_ready"] = True


def _to_object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def _user_summary(user_id):
    public = serialize_user(_users_collection().find_one({"_id": user_id}))
    if not public:
        return None
    return {
        "id": public["id"],
        "username": public["username"],
        "nickname": public["nickname"],
        "campus": public["campus"],
        "contact": public["contact"],
    }


def _product_summary(product_id):
    product = _products_collection().find_one({"_id": product_id})
    public = serialize_product(product)
    if not public:
        return None
    return {
        "id": public["id"],
        "title": public["title"],
        "price_cents": public["price_cents"],
        "category_name": public["category_name"],
        "condition": public["condition"],
        "images": public["images"],
        "status": public["status"],
    }


def serialize_trade(trade):
    if not trade:
        return None

    return {
        "id": str(trade["_id"]),
        "product_id": str(trade["product_id"]),
        "buyer_id": str(trade["buyer_id"]),
        "seller_id": str(trade["seller_id"]),
        "product": _product_summary(trade["product_id"]),
        "buyer": _user_summary(trade["buyer_id"]),
        "seller": _user_summary(trade["seller_id"]),
        "status": trade["status"],
        "message": trade.get("message", ""),
        "created_at": trade.get("created_at"),
        "updated_at": trade.get("updated_at"),
        "confirmed_at": trade.get("confirmed_at"),
        "cancelled_at": trade.get("cancelled_at"),
        "completed_at": trade.get("completed_at"),
        "completed_by": str(trade["completed_by"]) if trade.get("completed_by") else None,
    }


def has_active_trade(buyer_id, product_id):
    ensure_trade_indexes()
    return (
        _collection().count_documents(
            {
                "buyer_id": ObjectId(buyer_id),
                "product_id": ObjectId(product_id),
                "status": {"$in": sorted(ACTIVE_TRADE_STATUSES)},
            }
        )
        > 0
    )


def create_trade(buyer_id, product, message=""):
    ensure_trade_indexes()
    now = utc_now_iso()
    document = {
        "product_id": product["_id"],
        "buyer_id": ObjectId(buyer_id),
        "seller_id": product["owner_id"],
        "status": "pending",
        "message": message,
        "created_at": now,
        "updated_at": now,
        "confirmed_at": None,
        "cancelled_at": None,
        "completed_at": None,
        "completed_by": None,
    }
    result = _collection().insert_one(document)
    document["_id"] = result.inserted_id
    return document


def find_trade_by_id(trade_id):
    ensure_trade_indexes()
    object_id = _to_object_id(trade_id)
    if not object_id:
        return None
    return _collection().find_one({"_id": object_id})


def list_trades(filters):
    ensure_trade_indexes()
    query = {}
    if filters.get("buyer_id"):
        query["buyer_id"] = ObjectId(filters["buyer_id"])
    if filters.get("seller_id"):
        query["seller_id"] = ObjectId(filters["seller_id"])
    if filters.get("status"):
        query["status"] = filters["status"]

    page = filters["page"]
    page_size = filters["page_size"]
    total = _collection().count_documents(query)
    cursor = (
        _collection()
        .find(query)
        .sort([("created_at", DESCENDING)])
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    return {
        "items": [serialize_trade(trade) for trade in cursor],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def confirm_trade(trade_id):
    ensure_trade_indexes()
    now = utc_now_iso()
    return _collection().find_one_and_update(
        {"_id": ObjectId(trade_id), "status": "pending"},
        {"$set": {"status": "confirmed", "confirmed_at": now, "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )


def cancel_trade(trade_id):
    ensure_trade_indexes()
    now = utc_now_iso()
    return _collection().find_one_and_update(
        {"_id": ObjectId(trade_id), "status": "pending"},
        {"$set": {"status": "cancelled", "cancelled_at": now, "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )


def complete_trade(trade_id, completed_by):
    ensure_trade_indexes()
    now = utc_now_iso()
    return _collection().find_one_and_update(
        {"_id": ObjectId(trade_id), "status": "confirmed"},
        {
            "$set": {
                "status": "completed",
                "completed_at": now,
                "completed_by": ObjectId(completed_by),
                "updated_at": now,
            }
        },
        return_document=ReturnDocument.AFTER,
    )
