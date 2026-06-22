from flask import Blueprint, g, request

from app.middleware.auth import require_auth
from app.repositories.users import serialize_user, update_user_profile
from app.services.auth import (
    AuthError,
    extract_profile,
    validate_no_forbidden_fields,
)
from app.utils.response import error_response, success_response


users_bp = Blueprint("users", __name__)


def _json_payload():
    return request.get_json(silent=True) or {}


@users_bp.get("/me")
@require_auth
def get_me():
    return success_response(data=serialize_user(g.current_user))


@users_bp.put("/me")
@require_auth
def update_me():
    payload = _json_payload()
    try:
        validate_no_forbidden_fields(payload)
        profile = extract_profile(payload)
    except AuthError as error:
        return error_response(error.error_code, error.message, error.status_code)

    user = update_user_profile(str(g.current_user["_id"]), profile)
    return success_response(data=serialize_user(user), message="资料已更新")
