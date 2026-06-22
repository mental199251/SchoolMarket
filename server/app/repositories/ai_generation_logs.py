from bson import ObjectId
from flask import current_app
from pymongo import ASCENDING, DESCENDING

from app.repositories.users import utc_now_iso


def _collection():
    return current_app.extensions["mongo"].db.ai_generation_logs


def ensure_ai_generation_log_indexes():
    if current_app.extensions.get("ai_generation_logs_indexes_ready"):
        return

    logs = _collection()
    logs.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_ai_logs_user_created",
    )
    logs.create_index(
        [("generation_type", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
        name="idx_ai_logs_type_status_created",
    )
    current_app.extensions["ai_generation_logs_indexes_ready"] = True


def serialize_log(log):
    if not log:
        return None
    return {
        "id": str(log["_id"]),
        "user_id": str(log["user_id"]),
        "generation_type": log["generation_type"],
        "model": log["model"],
        "status": log["status"],
        "prompt_summary": log.get("prompt_summary", ""),
        "response_summary": log.get("response_summary", ""),
        "duration_ms": log.get("duration_ms", 0),
        "error_code": log.get("error_code"),
        "error_message": log.get("error_message", ""),
        "created_at": log.get("created_at"),
    }


def create_log(
    user_id,
    generation_type,
    model,
    status,
    prompt_summary="",
    response_summary="",
    duration_ms=0,
    error_code=None,
    error_message="",
):
    ensure_ai_generation_log_indexes()
    document = {
        "user_id": ObjectId(user_id),
        "generation_type": generation_type,
        "model": model,
        "status": status,
        "prompt_summary": prompt_summary,
        "response_summary": response_summary,
        "duration_ms": int(duration_ms or 0),
        "error_code": error_code,
        "error_message": (error_message or "")[:300],
        "created_at": utc_now_iso(),
    }
    result = _collection().insert_one(document)
    document["_id"] = result.inserted_id
    return document
