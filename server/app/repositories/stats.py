from flask import current_app

from app.repositories.products import ensure_product_indexes
from app.repositories.trades import ensure_trade_indexes
from app.repositories.users import ensure_user_indexes, serialize_user


PRODUCT_STATUSES = ("available", "off_shelf", "sold")
TRADE_STATUSES = ("pending", "confirmed", "cancelled", "completed")
USER_STATUSES = ("active", "disabled")


def _products_collection():
    return current_app.extensions["mongo"].db.products


def _trades_collection():
    return current_app.extensions["mongo"].db.trade_requests


def _users_collection():
    return current_app.extensions["mongo"].db.users


def _range_query(field, stats_range):
    return {
        field: {
            "$gte": stats_range["start_at"],
            "$lte": stats_range["end_at"],
        }
    }


def _public_range(stats_range):
    return {
        "start_date": stats_range["start_date"],
        "end_date": stats_range["end_date"],
        "days": stats_range["days"],
    }


def _count_by_status(collection, statuses, base_query=None):
    pipeline = [
        {"$match": base_query or {}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    counts = {status: 0 for status in statuses}
    for row in collection.aggregate(pipeline):
        if row["_id"] in counts:
            counts[row["_id"]] = row["count"]
    return counts


def get_overview(stats_range):
    ensure_user_indexes()
    ensure_product_indexes()
    ensure_trade_indexes()

    users = _users_collection()
    products = _products_collection()
    trades = _trades_collection()

    product_base = {"deleted_at": None}
    trade_created_range = _range_query("created_at", stats_range)
    trade_completed_range = {
        "status": "completed",
        **_range_query("completed_at", stats_range),
    }

    user_status_counts = _count_by_status(users, USER_STATUSES)
    product_status_counts = _count_by_status(products, PRODUCT_STATUSES, product_base)
    trade_status_counts = _count_by_status(trades, TRADE_STATUSES)

    users_total = users.count_documents({})
    products_total = products.count_documents(product_base)
    trades_total = trades.count_documents({})
    created_trades = trades.count_documents(trade_created_range)
    completed_trades = trades.count_documents(trade_completed_range)
    completion_rate = round((completed_trades / created_trades) * 100, 1) if created_trades else 0

    return {
        "range": _public_range(stats_range),
        "totals": {
            "users_total": users_total,
            "new_users": users.count_documents(_range_query("created_at", stats_range)),
            "products_total": products_total,
            "published_products": products.count_documents(
                {**product_base, **_range_query("created_at", stats_range)}
            ),
            "trades_total": trades_total,
            "created_trades": created_trades,
            "completed_trades": completed_trades,
            "completion_rate": completion_rate,
        },
        "status": {
            "users": user_status_counts,
            "products": product_status_counts,
            "trades": trade_status_counts,
        },
    }


def get_category_stats(stats_range, limit):
    ensure_product_indexes()

    pipeline = [
        {
            "$match": {
                "deleted_at": None,
                **_range_query("created_at", stats_range),
            }
        },
        {
            "$group": {
                "_id": {
                    "category_key": "$category_key",
                    "category_name": "$category_name",
                    "status": "$status",
                },
                "count": {"$sum": 1},
            }
        },
    ]

    grouped = {}
    for row in _products_collection().aggregate(pipeline):
        category = row["_id"]
        key = category.get("category_key") or "unknown"
        item = grouped.setdefault(
            key,
            {
                "category_key": key,
                "category_name": category.get("category_name") or "未分类",
                "published_count": 0,
                "available_count": 0,
                "off_shelf_count": 0,
                "sold_count": 0,
            },
        )
        count = row["count"]
        item["published_count"] += count
        status = category.get("status")
        if status in PRODUCT_STATUSES:
            item[f"{status}_count"] += count

    items = sorted(
        grouped.values(),
        key=lambda item: (
            -item["published_count"],
            -item["sold_count"],
            item["category_name"],
        ),
    )[:limit]

    return {
        "range": _public_range(stats_range),
        "items": items,
        "limit": limit,
    }


def _aggregate_user_counts(field, match_query):
    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
    ]
    counts = {}
    for row in _trades_collection().aggregate(pipeline):
        if row["_id"]:
            counts[row["_id"]] = row["count"]
    return counts


def _aggregate_product_owner_counts(stats_range):
    pipeline = [
        {
            "$match": {
                "deleted_at": None,
                **_range_query("created_at", stats_range),
            }
        },
        {"$group": {"_id": "$owner_id", "count": {"$sum": 1}}},
    ]
    return {row["_id"]: row["count"] for row in _products_collection().aggregate(pipeline)}


def get_user_stats(stats_range, limit):
    ensure_user_indexes()
    ensure_product_indexes()
    ensure_trade_indexes()

    created_trade_match = _range_query("created_at", stats_range)
    completed_trade_match = {
        "status": "completed",
        **_range_query("completed_at", stats_range),
    }

    published_counts = _aggregate_product_owner_counts(stats_range)
    buyer_counts = _aggregate_user_counts("buyer_id", created_trade_match)
    seller_counts = _aggregate_user_counts("seller_id", created_trade_match)
    buyer_completed_counts = _aggregate_user_counts("buyer_id", completed_trade_match)
    seller_completed_counts = _aggregate_user_counts("seller_id", completed_trade_match)

    user_ids = set()
    for counts in [
        published_counts,
        buyer_counts,
        seller_counts,
        buyer_completed_counts,
        seller_completed_counts,
    ]:
        user_ids.update(counts)

    if not user_ids:
        return {
            "range": _public_range(stats_range),
            "items": [],
            "limit": limit,
        }

    users = {
        user["_id"]: serialize_user(user)
        for user in _users_collection().find({"_id": {"$in": list(user_ids)}})
    }

    items = []
    for user_id in user_ids:
        public_user = users.get(user_id)
        if not public_user:
            continue
        published_count = published_counts.get(user_id, 0)
        buy_request_count = buyer_counts.get(user_id, 0)
        received_request_count = seller_counts.get(user_id, 0)
        completed_count = buyer_completed_counts.get(user_id, 0) + seller_completed_counts.get(user_id, 0)
        activity_score = (
            published_count * 3
            + completed_count * 3
            + buy_request_count
            + received_request_count
        )
        items.append(
            {
                "user": {
                    "id": public_user["id"],
                    "username": public_user["username"],
                    "nickname": public_user["nickname"],
                    "role": public_user["role"],
                    "status": public_user["status"],
                    "campus": public_user["campus"],
                },
                "published_count": published_count,
                "buy_request_count": buy_request_count,
                "received_request_count": received_request_count,
                "completed_count": completed_count,
                "activity_score": activity_score,
            }
        )

    items.sort(
        key=lambda item: (
            -item["activity_score"],
            -item["published_count"],
            -item["completed_count"],
            item["user"]["username"],
        )
    )

    return {
        "range": _public_range(stats_range),
        "items": items[:limit],
        "limit": limit,
    }
