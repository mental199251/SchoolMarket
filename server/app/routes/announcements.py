from flask import Blueprint, request

from app.repositories import announcements as announcement_repository
from app.services.admin import AdminError, parse_announcement_filters
from app.utils.response import error_response, success_response


announcements_bp = Blueprint("announcements", __name__)


@announcements_bp.get("")
def list_public_announcements():
    try:
        filters = parse_announcement_filters(request.args, include_hidden=False)
    except AdminError as error:
        return error_response(error.error_code, error.message, error.status_code)
    return success_response(data=announcement_repository.list_announcements(filters))
