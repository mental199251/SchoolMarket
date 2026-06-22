from flask import Blueprint, g, request

from app.middleware.auth import get_optional_current_user, require_auth
from app.repositories import products as product_repository
from app.services.products import (
    ProductError,
    ensure_editable,
    ensure_owner,
    parse_product_filters,
    resolve_target_status,
    validate_product_payload,
)
from app.utils.response import error_response, success_response


products_bp = Blueprint("products", __name__)


def _json_payload():
    return request.get_json(silent=True) or {}


def _product_error(error):
    return error_response(error.error_code, error.message, error.status_code)


def _get_product_or_404(product_id):
    product = product_repository.find_product_by_id(product_id)
    if not product:
        return None, error_response("NOT_FOUND", "商品不存在", 404)
    return product, None


@products_bp.get("")
def list_products():
    try:
        filters = parse_product_filters(request.args)
    except ProductError as error:
        return _product_error(error)

    if request.args.get("mine") == "true":
        user, error = get_optional_current_user()
        if error:
            return _product_error(error)
        if not user:
            return error_response("AUTH_REQUIRED", "请先登录后再操作", 401)
        filters["owner_id"] = str(user["_id"])

    return success_response(data=product_repository.list_products(filters))


@products_bp.post("")
@require_auth
def create_product():
    try:
        data = validate_product_payload(_json_payload())
    except ProductError as error:
        return _product_error(error)

    product = product_repository.create_product(str(g.current_user["_id"]), data)
    return success_response(
        data=product_repository.serialize_product(product),
        message="商品已发布",
        status_code=201,
    )


@products_bp.get("/<product_id>")
def get_product(product_id):
    product, response = _get_product_or_404(product_id)
    if response:
        return response

    if product.get("status") != "available":
        user, error = get_optional_current_user()
        if error:
            return _product_error(error)
        if not user or str(product["owner_id"]) != str(user["_id"]):
            return error_response("NOT_FOUND", "商品不存在", 404)

    return success_response(data=product_repository.serialize_product(product))


@products_bp.put("/<product_id>")
@require_auth
def update_product(product_id):
    product, response = _get_product_or_404(product_id)
    if response:
        return response

    try:
        ensure_owner(product, g.current_user)
        ensure_editable(product)
        data = validate_product_payload(_json_payload())
    except ProductError as error:
        return _product_error(error)

    updated = product_repository.update_product(product_id, data)
    return success_response(
        data=product_repository.serialize_product(updated),
        message="商品已更新",
    )


@products_bp.delete("/<product_id>")
@require_auth
def delete_product(product_id):
    product, response = _get_product_or_404(product_id)
    if response:
        return response

    try:
        ensure_owner(product, g.current_user)
        ensure_editable(product)
    except ProductError as error:
        return _product_error(error)

    product_repository.delete_product(product_id)
    return success_response(data={"deleted": True}, message="商品已删除")


@products_bp.put("/<product_id>/status")
@require_auth
def update_product_status(product_id):
    product, response = _get_product_or_404(product_id)
    if response:
        return response

    try:
        ensure_owner(product, g.current_user)
        target_status = resolve_target_status(product, _json_payload())
    except ProductError as error:
        return _product_error(error)

    updated = product_repository.update_product_status(product_id, target_status)
    return success_response(
        data=product_repository.serialize_product(updated),
        message="商品状态已更新",
    )
