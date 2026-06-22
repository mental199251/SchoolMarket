from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app
from pymongo import ASCENDING, DESCENDING

from app.repositories.users import serialize_user, utc_now_iso


def _collection():
    return current_app.extensions["mongo"].db.operation_logs


def _users_collection():
    return current_app.extensions["mongo"].db.users


def ensure_operation_log_indexes():
    if current_app.extensions.get("operation_logs_indexes_ready"):
        return

    logs = _collection()
    logs.create_index([("operator_id", ASCENDING), ("created_at", DESCENDING)], name="idx_logs_operator_created")
    logs.create_index([("target_type", ASCENDING), ("target_id", ASCENDING)], name="idx_logs_target")
    logs.create_index([("action", ASCENDING), ("created_at", DESCENDING)], name="idx_logs_action_created")
    current_app.extensions["operation_logs_indexes_ready"] = True


def _operator_summary(operator_id):
    user = _users_collection().find_one({"_id": operator_id})
    public = serialize_user(user)
    if not public:
        return None
    return {
        "id": public["id"],
        "username": public["username"],
        "nickname": public["nickname"],
        "role": public["role"],
    }


def serialize_log(log):
    if not log:
        return None
    return {
        "id": str(log["_id"]),
        "operator_id": str(log["operator_id"]),
        "operator": _operator_summary(log["operator_id"]),
        "action": log["action"],
        "target_type": log["target_type"],
        "target_id": str(log["target_id"]) if log.get("target_id") else None,
        "details": log.get("details", {}),
        "created_at": log.get("created_at"),
    }


def create_log(operator_id, action, target_type, target_id=None, details=None):
    ensure_operation_log_indexes()
    target_object_id = None
    if target_id:
        try:
            target_object_id = ObjectId(target_id)
        except (InvalidId, TypeError):
            target_object_id = None

    document = {
        "operator_id": ObjectId(operator_id),
        "action": action,
        "target_type": target_type,
        "target_id": target_object_id,
        "details": details or {},
        "created_at": utc_now_iso(),
    }
    result = _collection().insert_one(document)
    document["_id"] = result.inserted_id
    return document


def list_logs(filters):
    ensure_operation_log_indexes()
    query = {}
    if filters.get("action"):
        query["action"] = filters["action"]
    if filters.get("target_type"):
        query["target_type"] = filters["target_type"]
    if filters.get("operator_id"):
        query["operator_id"] = ObjectId(filters["operator_id"])

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
        "items": [serialize_log(log) for log in cursor],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
