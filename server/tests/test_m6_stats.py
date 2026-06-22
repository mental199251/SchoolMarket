from app.repositories.categories import upsert_default_categories
from app.repositories.users import upsert_seed_user
from app.services.auth import hash_password


PASSWORD = "Password123"


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def register(client, username):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": PASSWORD,
            "nickname": username,
            "campus": "东校区",
        },
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def seed_admin(app, username="admin_m6"):
    with app.app_context():
        user = upsert_seed_user(
            username=username,
            password_hash=hash_password(PASSWORD),
            role="admin",
            profile={"nickname": "M6 管理员"},
        )
    return str(user["_id"])


def login(client, username):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 200
    return response.get_json()["data"]


def create_product(client, token, title, category_key="books", condition="good"):
    response = client.post(
        "/api/v1/products",
        json={
            "title": title,
            "description": "用于 M6 统计",
            "price_cents": 3200,
            "category_key": category_key,
            "condition": condition,
            "images": [],
        },
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def create_trade(client, token, product_id):
    response = client.post(
        "/api/v1/trades",
        json={"product_id": product_id, "message": "想买这个"},
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def complete_trade(client, seller_token, buyer_token, trade_id):
    confirmed = client.put(
        f"/api/v1/trades/{trade_id}/confirm",
        headers=auth_header(seller_token),
    )
    assert confirmed.status_code == 200
    completed = client.put(
        f"/api/v1/trades/{trade_id}/complete",
        headers=auth_header(buyer_token),
    )
    assert completed.status_code == 200


def test_stats_reports_use_admin_aggregate_counts(client, app):
    with app.app_context():
        upsert_default_categories()
    seed_admin(app)
    admin = login(client, "admin_m6")
    seller = register(client, "m6_seller")
    buyer = register(client, "m6_buyer")

    book = create_product(client, seller["token"], "M6 教材", "books")
    headset = create_product(client, seller["token"], "M6 耳机", "electronics", "like_new")
    completed_trade = create_trade(client, buyer["token"], book["id"])
    create_trade(client, buyer["token"], headset["id"])
    complete_trade(client, seller["token"], buyer["token"], completed_trade["id"])

    forbidden = client.get("/api/v1/stats/overview", headers=auth_header(buyer["token"]))
    assert forbidden.status_code == 403
    assert forbidden.get_json()["error_code"] == "FORBIDDEN"

    overview = client.get(
        "/api/v1/stats/overview?days=30",
        headers=auth_header(admin["token"]),
    )
    assert overview.status_code == 200
    overview_data = overview.get_json()["data"]
    assert overview_data["totals"]["users_total"] == 3
    assert overview_data["totals"]["new_users"] == 3
    assert overview_data["totals"]["products_total"] == 2
    assert overview_data["totals"]["published_products"] == 2
    assert overview_data["totals"]["created_trades"] == 2
    assert overview_data["totals"]["completed_trades"] == 1
    assert overview_data["totals"]["completion_rate"] == 50.0
    assert overview_data["status"]["products"]["available"] == 1
    assert overview_data["status"]["products"]["sold"] == 1
    assert overview_data["status"]["trades"]["pending"] == 1
    assert overview_data["status"]["trades"]["completed"] == 1

    categories = client.get(
        "/api/v1/stats/categories?days=30&limit=5",
        headers=auth_header(admin["token"]),
    )
    assert categories.status_code == 200
    category_items = {item["category_key"]: item for item in categories.get_json()["data"]["items"]}
    assert category_items["books"]["published_count"] == 1
    assert category_items["books"]["sold_count"] == 1
    assert category_items["electronics"]["published_count"] == 1
    assert category_items["electronics"]["available_count"] == 1

    users = client.get(
        "/api/v1/stats/users?days=30&limit=5",
        headers=auth_header(admin["token"]),
    )
    assert users.status_code == 200
    user_items = {item["user"]["username"]: item for item in users.get_json()["data"]["items"]}
    assert user_items["m6_seller"]["published_count"] == 2
    assert user_items["m6_seller"]["received_request_count"] == 2
    assert user_items["m6_seller"]["completed_count"] == 1
    assert user_items["m6_buyer"]["buy_request_count"] == 2
    assert user_items["m6_buyer"]["completed_count"] == 1
    assert user_items["m6_seller"]["activity_score"] > user_items["m6_buyer"]["activity_score"]

    invalid_days = client.get(
        "/api/v1/stats/overview?days=0",
        headers=auth_header(admin["token"]),
    )
    assert invalid_days.status_code == 400
    assert invalid_days.get_json()["error_code"] == "VALIDATION_ERROR"
