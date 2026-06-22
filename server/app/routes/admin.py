from flask import Blueprint, g, request

from app.middleware.auth import require_admin
from app.repositories import announcements as announcement_repository
from app.repositories import operation_logs as log_repository
from app.repositories import products as product_repository
from app.repositories import users as user_repository
from app.services.admin import (
    AdminError,
    parse_admin_product_filters,
    parse_announcement_filters,
    parse_log_filters,
    parse_user_filters,
    validate_announcement_payload,
    validate_product_status,
    validate_user_status,
)
from app.utils.response import error_response, success_response


admin_bp = Blueprint("admin", __name__)


def _json_payload():
    return request.get_json(silent=True) or {}


def _admin_error(error):
    return error_response(error.error_code, error.message, error.status_code)


def _log(action, target_type, target_id=None, details=None):
    return log_repository.create_log(
        str(g.current_user["_id"]),
        action,
        target_type,
        target_id=target_id,
        details=details,
    )


@admin_bp.get("/users")
@require_admin
def list_users():
    try:
        filters = parse_user_filters(request.args)
    except AdminError as error:
        return _admin_error(error)
    return success_response(data=user_repository.list_users(filters))


@admin_bp.put("/users/<user_id>/status")
@require_admin
def update_user_status(user_id):
    payload = _json_payload()
    try:
        status = validate_user_status(payload.get("status"))
    except AdminError as error:
        return _admin_error(error)

    user = user_repository.update_user_status(user_id, status)
    if not user:
        return error_response("NOT_FOUND", "用户不存在", 404)
    _log(
        "user_status_update",
        "user",
        user_id,
        {"status": status, "username": user.get("username")},
    )
    return success_response(data=user_repository.serialize_user(user), message="用户状态已更新")


@admin_bp.get("/products")
@require_admin
def list_products():
    try:
        filters = parse_admin_product_filters(request.args)
    except AdminError as error:
        return _admin_error(error)
    return success_response(data=product_repository.list_admin_products(filters))


@admin_bp.put("/products/<product_id>/status")
@require_admin
def update_product_status(product_id):
    payload = _json_payload()
    try:
        status = validate_product_status(payload.get("status"))
    except AdminError as error:
        return _admin_error(error)

    product = product_repository.admin_update_product_status(product_id, status)
    if not product:
        return error_response("NOT_FOUND", "商品不存在", 404)
    _log(
        "product_status_update",
        "product",
        product_id,
        {"status": status, "title": product.get("title")},
    )
    return success_response(data=product_repository.serialize_product(product), message="商品状态已更新")


@admin_bp.delete("/products/<product_id>")
@require_admin
def delete_product(product_id):
    product = product_repository.delete_product(product_id)
    if not product:
        return error_response("NOT_FOUND", "商品不存在", 404)
    _log(
        "product_delete",
        "product",
        product_id,
        {"title": product.get("title")},
    )
    return success_response(data={"deleted": True}, message="商品已删除")


@admin_bp.get("/announcements")
@require_admin
def list_announcements():
    try:
        filters = parse_announcement_filters(request.args, include_hidden=True)
    except AdminError as error:
        return _admin_error(error)
    return success_response(data=announcement_repository.list_announcements(filters))


@admin_bp.post("/announcements")
@require_admin
def create_announcement():
    try:
        data = validate_announcement_payload(_json_payload())
    except AdminError as error:
        return _admin_error(error)
    announcement = announcement_repository.create_announcement(data, str(g.current_user["_id"]))
    _log(
        "announcement_create",
        "announcement",
        str(announcement["_id"]),
        {"title": announcement.get("title"), "status": announcement.get("status")},
    )
    return success_response(
        data=announcement_repository.serialize_announcement(announcement),
        message="公告已创建",
        status_code=201,
    )


@admin_bp.put("/announcements/<announcement_id>")
@require_admin
def update_announcement(announcement_id):
    try:
        data = validate_announcement_payload(_json_payload())
    except AdminError as error:
        return _admin_error(error)
    announcement = announcement_repository.update_announcement(announcement_id, data)
    if not announcement:
        return error_response("NOT_FOUND", "公告不存在", 404)
    _log(
        "announcement_update",
        "announcement",
        announcement_id,
        {"title": announcement.get("title"), "status": announcement.get("status")},
    )
    return success_response(
        data=announcement_repository.serialize_announcement(announcement),
        message="公告已更新",
    )


@admin_bp.delete("/announcements/<announcement_id>")
@require_admin
def delete_announcement(announcement_id):
    announcement = announcement_repository.delete_announcement(announcement_id)
    if not announcement:
        return error_response("NOT_FOUND", "公告不存在", 404)
    _log(
        "announcement_delete",
        "announcement",
        announcement_id,
        {"title": announcement.get("title")},
    )
    return success_response(data={"deleted": True}, message="公告已隐藏")


@admin_bp.get("/logs")
@require_admin
def list_logs():
    try:
        filters = parse_log_filters(request.args)
    except AdminError as error:
        return _admin_error(error)
    return success_response(data=log_repository.list_logs(filters))
