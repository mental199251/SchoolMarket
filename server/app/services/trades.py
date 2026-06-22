from app.repositories import products as product_repository
from app.repositories import trades as trade_repository


TRADE_STATUSES = {"pending", "confirmed", "cancelled", "completed"}


class TradeError(Exception):
    def __init__(self, error_code, message, status_code=400, data=None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.data = data


def _clean_message(value):
    if value in (None, ""):
        return ""
    if not isinstance(value, str):
        raise TradeError("VALIDATION_ERROR", "留言必须为字符串", 400)
    cleaned = value.strip()
    if len(cleaned) > 300:
        raise TradeError("VALIDATION_ERROR", "留言不能超过 300 位", 400)
    return cleaned


def parse_trade_filters(args):
    try:
        page = max(1, int(args.get("page", 1)))
        page_size = min(50, max(1, int(args.get("page_size", 20))))
    except (TypeError, ValueError):
        raise TradeError("VALIDATION_ERROR", "分页参数无效", 400)

    status = (args.get("status") or "").strip()
    if status and status not in TRADE_STATUSES:
        raise TradeError("VALIDATION_ERROR", "交易状态无效", 400)
    return {"page": page, "page_size": page_size, "status": status}


def create_trade_for_product(buyer, payload):
    product_id = (payload.get("product_id") or "").strip()
    if not product_id:
        raise TradeError("VALIDATION_ERROR", "请选择商品", 400)

    product = product_repository.find_product_by_id(product_id)
    if not product:
        raise TradeError("NOT_FOUND", "商品不存在", 404)
    if product.get("status") != "available":
        raise TradeError("PRODUCT_UNAVAILABLE", "商品当前不可购买", 409)
    if str(product["owner_id"]) == str(buyer["_id"]):
        raise TradeError("FORBIDDEN", "不能购买自己发布的商品", 403)
    if trade_repository.has_active_trade(str(buyer["_id"]), product_id):
        raise TradeError("DUPLICATE_TRADE_REQUEST", "已对该商品发起过有效请求", 409)

    return trade_repository.create_trade(
        str(buyer["_id"]),
        product,
        message=_clean_message(payload.get("message")),
    )


def ensure_participant(trade, user):
    if str(user["_id"]) not in {str(trade["buyer_id"]), str(trade["seller_id"])}:
        raise TradeError("FORBIDDEN", "只能操作自己参与的交易", 403)


def ensure_seller(trade, user):
    if str(trade["seller_id"]) != str(user["_id"]):
        raise TradeError("FORBIDDEN", "只有卖家可以确认交易", 403)


def conflict_for_trade(trade, message="交易状态已变化"):
    public_trade = trade_repository.serialize_trade(trade)
    raise TradeError(
        "PRODUCT_UNAVAILABLE",
        message,
        409,
        data={"trade": public_trade},
    )


def confirm_trade(trade, user):
    ensure_seller(trade, user)
    if trade.get("status") != "pending":
        conflict_for_trade(trade, "只有待处理交易可以确认")
    updated = trade_repository.confirm_trade(str(trade["_id"]))
    if not updated:
        latest = trade_repository.find_trade_by_id(str(trade["_id"]))
        conflict_for_trade(latest or trade)
    return updated


def cancel_trade(trade, user):
    ensure_participant(trade, user)
    if trade.get("status") != "pending":
        conflict_for_trade(trade, "只有待处理交易可以取消")
    updated = trade_repository.cancel_trade(str(trade["_id"]))
    if not updated:
        latest = trade_repository.find_trade_by_id(str(trade["_id"]))
        conflict_for_trade(latest or trade)
    return updated


def complete_trade(trade, user):
    ensure_participant(trade, user)
    if trade.get("status") != "confirmed":
        conflict_for_trade(trade, "只有已确认交易可以完成")

    sold_product = product_repository.mark_product_sold(str(trade["product_id"]))
    if not sold_product:
        latest = trade_repository.find_trade_by_id(str(trade["_id"]))
        conflict_for_trade(latest or trade, "商品状态已变化")

    updated = trade_repository.complete_trade(str(trade["_id"]), str(user["_id"]))
    if not updated:
        latest = trade_repository.find_trade_by_id(str(trade["_id"]))
        conflict_for_trade(latest or trade)
    return updated
