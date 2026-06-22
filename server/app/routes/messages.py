from flask import Blueprint, g, request

from app.middleware.auth import require_auth
from app.repositories import messages as message_repository
from app.services.admin import AdminError, parse_pagination
from app.utils.response import error_response, success_response


messages_bp = Blueprint("messages", __name__)


def _parse_message_filters(args):
    page, page_size = parse_pagination(args)
    read = (args.get("read") or "").strip().lower()
    is_read = None
    if read in {"true", "1", "yes"}:
        is_read = True
    elif read in {"false", "0", "no"}:
        is_read = False
    elif read:
        raise AdminError("VALIDATION_ERROR", "消息已读筛选无效", 400)
    return {
        "page": page,
        "page_size": page_size,
        "is_read": is_read,
        "type": (args.get("type") or "").strip(),
    }


@messages_bp.get("")
@require_auth
def list_messages():
    try:
        filters = _parse_message_filters(request.args)
    except AdminError as error:
        return error_response(error.error_code, error.message, error.status_code)
    return success_response(
        data=message_repository.list_messages(str(g.current_user["_id"]), filters)
    )


@messages_bp.put("/<message_id>/read")
@require_auth
def read_message(message_id):
    message = message_repository.mark_message_read(message_id, str(g.current_user["_id"]))
    if not message:
        return error_response("NOT_FOUND", "消息不存在", 404)
    return success_response(data=message_repository.serialize_message(message), message="消息已读")


@messages_bp.put("/read-all")
@require_auth
def read_all_messages():
    count = message_repository.mark_all_read(str(g.current_user["_id"]))
    return success_response(data={"updated": count}, message="消息已全部标记为已读")
