from flask import Blueprint, g, request

from app.middleware.auth import require_auth
from app.repositories import trades as trade_repository
from app.services.trades import (
    TradeError,
    cancel_trade,
    complete_trade,
    confirm_trade,
    create_trade_for_product,
    parse_trade_filters,
)
from app.utils.response import error_response, success_response


trades_bp = Blueprint("trades", __name__)


def _json_payload():
    return request.get_json(silent=True) or {}


def _trade_error(error):
    return error_response(
        error.error_code,
        error.message,
        error.status_code,
        data=error.data,
    )


def _get_trade_or_404(trade_id):
    trade = trade_repository.find_trade_by_id(trade_id)
    if not trade:
        return None, error_response("NOT_FOUND", "交易请求不存在", 404)
    return trade, None


@trades_bp.post("")
@require_auth
def create_trade():
    try:
        trade = create_trade_for_product(g.current_user, _json_payload())
    except TradeError as error:
        return _trade_error(error)

    return success_response(
        data=trade_repository.serialize_trade(trade),
        message="购买请求已发送",
        status_code=201,
    )


@trades_bp.get("/my-buy")
@require_auth
def my_buy_trades():
    try:
        filters = parse_trade_filters(request.args)
    except TradeError as error:
        return _trade_error(error)
    filters["buyer_id"] = str(g.current_user["_id"])
    return success_response(data=trade_repository.list_trades(filters))


@trades_bp.get("/my-sell")
@require_auth
def my_sell_trades():
    try:
        filters = parse_trade_filters(request.args)
    except TradeError as error:
        return _trade_error(error)
    filters["seller_id"] = str(g.current_user["_id"])
    return success_response(data=trade_repository.list_trades(filters))


@trades_bp.put("/<trade_id>/confirm")
@require_auth
def confirm(trade_id):
    trade, response = _get_trade_or_404(trade_id)
    if response:
        return response
    try:
        updated = confirm_trade(trade, g.current_user)
    except TradeError as error:
        return _trade_error(error)
    return success_response(
        data=trade_repository.serialize_trade(updated),
        message="交易已确认",
    )


@trades_bp.put("/<trade_id>/cancel")
@require_auth
def cancel(trade_id):
    trade, response = _get_trade_or_404(trade_id)
    if response:
        return response
    try:
        updated = cancel_trade(trade, g.current_user)
    except TradeError as error:
        return _trade_error(error)
    return success_response(
        data=trade_repository.serialize_trade(updated),
        message="交易已取消",
    )


@trades_bp.put("/<trade_id>/complete")
@require_auth
def complete(trade_id):
    trade, response = _get_trade_or_404(trade_id)
    if response:
        return response
    try:
        updated = complete_trade(trade, g.current_user)
    except TradeError as error:
        return _trade_error(error)
    return success_response(
        data=trade_repository.serialize_trade(updated),
        message="交易已完成",
    )
