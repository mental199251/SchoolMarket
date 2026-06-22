from app.repositories import messages as message_repository


def create_trade_created_messages(trade):
    title = "收到新的购买请求"
    product_title = trade.get("product", {}).get("title") if trade.get("product") else "你的商品"
    buyer_name = trade.get("buyer", {}).get("nickname") or trade.get("buyer", {}).get("username") or "买家"
    return message_repository.create_message(
        trade["seller_id"],
        "trade",
        title,
        f"{buyer_name} 想购买「{product_title}」。",
        related_type="trade",
        related_id=trade["id"],
    )


def create_trade_confirmed_message(trade):
    product_title = trade.get("product", {}).get("title") if trade.get("product") else "商品"
    return message_repository.create_message(
        trade["buyer_id"],
        "trade",
        "购买请求已确认",
        f"卖家已确认「{product_title}」，请线下完成交易。",
        related_type="trade",
        related_id=trade["id"],
    )


def create_trade_cancelled_message(trade, actor_id):
    product_title = trade.get("product", {}).get("title") if trade.get("product") else "商品"
    recipients = [trade["buyer_id"], trade["seller_id"]]
    created = []
    for user_id in recipients:
        if user_id == actor_id:
            continue
        created.append(
            message_repository.create_message(
                user_id,
                "trade",
                "交易请求已取消",
                f"「{product_title}」的交易请求已取消。",
                related_type="trade",
                related_id=trade["id"],
            )
        )
    return created


def create_trade_completed_messages(trade):
    product_title = trade.get("product", {}).get("title") if trade.get("product") else "商品"
    created = []
    for user_id in {trade["buyer_id"], trade["seller_id"]}:
        created.append(
            message_repository.create_message(
                user_id,
                "trade",
                "交易已完成",
                f"「{product_title}」已标记为线下交易完成。",
                related_type="trade",
                related_id=trade["id"],
            )
        )
    return created
