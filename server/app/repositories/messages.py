from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from app.repositories.users import utc_now_iso


def _collection():
    return current_app.extensions["mongo"].db.messages


def ensure_message_indexes():
    if current_app.extensions.get("messages_indexes_ready"):
        return

    messages = _collection()
    messages.create_index(
        [("user_id", ASCENDING), ("is_read", ASCENDING), ("created_at", DESCENDING)],
        name="idx_messages_user_read_created",
    )
    messages.create_index([("related_type", ASCENDING), ("related_id", ASCENDING)], name="idx_messages_related")
    current_app.extensions["messages_indexes_ready"] = True


def serialize_message(message):
    if not message:
        return None
    return {
        "id": str(message["_id"]),
        "user_id": str(message["user_id"]),
        "type": message["type"],
        "title": message["title"],
        "content": message.get("content", ""),
        "related_type": message.get("related_type"),
        "related_id": str(message["related_id"]) if message.get("related_id") else None,
        "is_read": message.get("is_read", False),
        "created_at": message.get("created_at"),
        "read_at": message.get("read_at"),
    }


def create_message(user_id, message_type, title, content="", related_type=None, related_id=None):
    ensure_message_indexes()
    related_object_id = None
    if related_id:
        try:
            related_object_id = ObjectId(related_id)
        except (InvalidId, TypeError):
            related_object_id = None

    now = utc_now_iso()
    document = {
        "user_id": ObjectId(user_id),
        "type": message_type,
        "title": title,
        "content": content,
        "related_type": related_type,
        "related_id": related_object_id,
        "is_read": False,
        "created_at": now,
        "read_at": None,
    }
    result = _collection().insert_one(document)
    document["_id"] = result.inserted_id
    return document


def list_messages(user_id, filters):
    ensure_message_indexes()
    query = {"user_id": ObjectId(user_id)}
    if filters.get("is_read") is not None:
        query["is_read"] = filters["is_read"]
    if filters.get("type"):
        query["type"] = filters["type"]

    page = filters["page"]
    page_size = filters["page_size"]
    total = _collection().count_documents(query)
    unread_count = _collection().count_documents({"user_id": ObjectId(user_id), "is_read": False})
    cursor = (
        _collection()
        .find(query)
        .sort([("created_at", DESCENDING)])
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    return {
        "items": [serialize_message(message) for message in cursor],
        "total": total,
        "page": page,
        "page_size": page_size,
        "unread_count": unread_count,
    }


def mark_message_read(message_id, user_id):
    ensure_message_indexes()
    try:
        object_id = ObjectId(message_id)
    except (InvalidId, TypeError):
        return None
    return _collection().find_one_and_update(
        {"_id": object_id, "user_id": ObjectId(user_id)},
        {"$set": {"is_read": True, "read_at": utc_now_iso()}},
        return_document=ReturnDocument.AFTER,
    )


def mark_all_read(user_id):
    ensure_message_indexes()
    now = utc_now_iso()
    result = _collection().update_many(
        {"user_id": ObjectId(user_id), "is_read": False},
        {"$set": {"is_read": True, "read_at": now}},
    )
    return result.modified_count
