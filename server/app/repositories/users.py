from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError


class DuplicateAccountError(Exception):
    pass


def utc_now_iso():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def _collection():
    return current_app.extensions["mongo"].db.users


def ensure_user_indexes():
    if current_app.extensions.get("users_indexes_ready"):
        return

    users = _collection()
    users.create_index(
        [("username_key", ASCENDING)],
        unique=True,
        name="uniq_users_username_key",
    )
    users.create_index([("status", ASCENDING)], name="idx_users_status")
    current_app.extensions["users_indexes_ready"] = True


def username_key(username):
    return username.strip().lower()


def serialize_user(user):
    if not user:
        return None

    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "user"),
        "status": user.get("status", "active"),
        "nickname": user.get("nickname", ""),
        "contact": user.get("contact", ""),
        "campus": user.get("campus", ""),
        "avatar_url": user.get("avatar_url", ""),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }


def create_user(username, password_hash, profile=None, role="user", status="active"):
    ensure_user_indexes()
    now = utc_now_iso()
    profile = profile or {}
    document = {
        "username": username.strip(),
        "username_key": username_key(username),
        "password_hash": password_hash,
        "role": role,
        "status": status,
        "nickname": profile.get("nickname", "").strip(),
        "contact": profile.get("contact", "").strip(),
        "campus": profile.get("campus", "").strip(),
        "avatar_url": profile.get("avatar_url", "").strip(),
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
    }

    try:
        result = _collection().insert_one(document)
    except DuplicateKeyError as exc:
        raise DuplicateAccountError from exc

    document["_id"] = result.inserted_id
    return document


def upsert_seed_user(username, password_hash, role="user", status="active", profile=None):
    ensure_user_indexes()
    now = utc_now_iso()
    profile = profile or {}
    update = {
        "$set": {
            "username": username.strip(),
            "username_key": username_key(username),
            "password_hash": password_hash,
            "role": role,
            "status": status,
            "nickname": profile.get("nickname", "").strip(),
            "contact": profile.get("contact", "").strip(),
            "campus": profile.get("campus", "").strip(),
            "avatar_url": profile.get("avatar_url", "").strip(),
            "updated_at": now,
        },
        "$setOnInsert": {
            "created_at": now,
            "last_login_at": None,
        },
    }
    return _collection().find_one_and_update(
        {"username_key": username_key(username)},
        update,
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )


def find_user_by_username(username):
    ensure_user_indexes()
    return _collection().find_one({"username_key": username_key(username)})


def find_user_by_id(user_id):
    ensure_user_indexes()
    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None

    return _collection().find_one({"_id": object_id})


def mark_login(user_id):
    ensure_user_indexes()
    now = utc_now_iso()
    _collection().update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"last_login_at": now, "updated_at": now}},
    )


def update_user_profile(user_id, profile):
    ensure_user_indexes()
    now = utc_now_iso()
    allowed_fields = {"nickname", "contact", "campus", "avatar_url"}
    update_fields = {
        field: str(profile.get(field, "")).strip()
        for field in allowed_fields
        if field in profile
    }
    update_fields["updated_at"] = now

    return _collection().find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_fields},
        return_document=ReturnDocument.AFTER,
    )


def update_password_hash(user_id, password_hash):
    ensure_user_indexes()
    now = utc_now_iso()
    return _collection().find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": password_hash, "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )


def set_user_status_for_tests(user_id, status):
    ensure_user_indexes()
    return _collection().find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": status, "updated_at": utc_now_iso()}},
        return_document=ReturnDocument.AFTER,
    )
