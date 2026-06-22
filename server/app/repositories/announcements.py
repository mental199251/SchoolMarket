from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from app.repositories.users import utc_now_iso


def _collection():
    return current_app.extensions["mongo"].db.announcements


def ensure_announcement_indexes():
    if current_app.extensions.get("announcements_indexes_ready"):
        return

    announcements = _collection()
    announcements.create_index([("status", ASCENDING), ("created_at", DESCENDING)], name="idx_announcements_status_created")
    current_app.extensions["announcements_indexes_ready"] = True


def serialize_announcement(announcement):
    if not announcement:
        return None
    return {
        "id": str(announcement["_id"]),
        "title": announcement["title"],
        "content": announcement.get("content", ""),
        "status": announcement.get("status", "published"),
        "created_by": str(announcement["created_by"]) if announcement.get("created_by") else None,
        "created_at": announcement.get("created_at"),
        "updated_at": announcement.get("updated_at"),
    }


def create_announcement(data, created_by):
    ensure_announcement_indexes()
    now = utc_now_iso()
    document = {
        "title": data["title"],
        "content": data.get("content", ""),
        "status": data.get("status", "published"),
        "created_by": ObjectId(created_by),
        "created_at": now,
        "updated_at": now,
    }
    result = _collection().insert_one(document)
    document["_id"] = result.inserted_id
    return document


def list_announcements(filters):
    ensure_announcement_indexes()
    query = {}
    if not filters.get("include_hidden"):
        query["status"] = "published"
    elif filters.get("status"):
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
        "items": [serialize_announcement(item) for item in cursor],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def find_announcement_by_id(announcement_id):
    ensure_announcement_indexes()
    try:
        object_id = ObjectId(announcement_id)
    except (InvalidId, TypeError):
        return None
    return _collection().find_one({"_id": object_id})


def update_announcement(announcement_id, data):
    ensure_announcement_indexes()
    try:
        object_id = ObjectId(announcement_id)
    except (InvalidId, TypeError):
        return None
    update_fields = {
        "title": data["title"],
        "content": data.get("content", ""),
        "status": data.get("status", "published"),
        "updated_at": utc_now_iso(),
    }
    return _collection().find_one_and_update(
        {"_id": object_id},
        {"$set": update_fields},
        return_document=ReturnDocument.AFTER,
    )


def delete_announcement(announcement_id):
    ensure_announcement_indexes()
    try:
        object_id = ObjectId(announcement_id)
    except (InvalidId, TypeError):
        return None
    return _collection().find_one_and_update(
        {"_id": object_id},
        {"$set": {"status": "hidden", "updated_at": utc_now_iso()}},
        return_document=ReturnDocument.AFTER,
    )
