from flask import Blueprint, request

from app.middleware.auth import require_admin
from app.repositories import stats as stats_repository
from app.services.stats import StatsError, parse_stats_filters, parse_stats_limit
from app.utils.response import error_response, success_response


stats_bp = Blueprint("stats", __name__)


def _stats_error(error):
    return error_response(error.error_code, error.message, error.status_code)


@stats_bp.get("/overview")
@require_admin
def overview():
    try:
        filters = parse_stats_filters(request.args)
    except StatsError as error:
        return _stats_error(error)
    return success_response(data=stats_repository.get_overview(filters))


@stats_bp.get("/categories")
@require_admin
def categories():
    try:
        filters = parse_stats_filters(request.args)
        limit = parse_stats_limit(request.args)
    except StatsError as error:
        return _stats_error(error)
    return success_response(data=stats_repository.get_category_stats(filters, limit))


@stats_bp.get("/users")
@require_admin
def users():
    try:
        filters = parse_stats_filters(request.args)
        limit = parse_stats_limit(request.args)
    except StatsError as error:
        return _stats_error(error)
    return success_response(data=stats_repository.get_user_stats(filters, limit))
