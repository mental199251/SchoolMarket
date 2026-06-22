from flask import Blueprint, g, request

from app.middleware.auth import require_auth
from app.services.ai import AIError, generate_descriptions, generate_titles
from app.utils.response import error_response, success_response


ai_bp = Blueprint("ai", __name__)


def _json_payload():
    return request.get_json(silent=True) or {}


def _ai_error(error):
    return error_response(error.error_code, error.message, error.status_code)


@ai_bp.post("/title")
@require_auth
def generate_title():
    try:
        data = generate_titles(str(g.current_user["_id"]), _json_payload())
    except AIError as error:
        return _ai_error(error)
    return success_response(data=data, message="标题建议已生成")


@ai_bp.post("/description")
@require_auth
def generate_description():
    try:
        data = generate_descriptions(str(g.current_user["_id"]), _json_payload())
    except AIError as error:
        return _ai_error(error)
    return success_response(data=data, message="描述建议已生成")
