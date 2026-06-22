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


def seed_admin(app, username="admin_m5"):
    with app.app_context():
        user = upsert_seed_user(
            username=username,
            password_hash=hash_password(PASSWORD),
            role="admin",
            profile={"nickname": "M5 管理员"},
        )
    return str(user["_id"])


def login(client, username):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 200
    return response.get_json()["data"]


def create_product(client, token, title="M5 测试商品"):
    response = client.post(
        "/api/v1/products",
        json={
            "title": title,
            "description": "用于 M5 验收",
            "price_cents": 3200,
            "category_key": "books",
            "condition": "good",
            "images": [],
        },
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def create_trade(client, token, product_id):
    response = client.post(
        "/api/v1/trades",
        json={"product_id": product_id, "message": "想线下交易"},
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def message_titles(client, token, read=None):
    query = "" if read is None else f"?read={str(read).lower()}"
    response = client.get(f"/api/v1/messages{query}", headers=auth_header(token))
    assert response.status_code == 200
    data = response.get_json()["data"]
    return [item["title"] for item in data["items"]], data


def test_trade_events_create_readable_messages(client, app):
    with app.app_context():
        upsert_default_categories()
    seller = register(client, "m5_seller")
    buyer = register(client, "m5_buyer")
    product = create_product(client, seller["token"])

    trade = create_trade(client, buyer["token"], product["id"])
    seller_titles, seller_messages = message_titles(client, seller["token"])
    assert "收到新的购买请求" in seller_titles
    assert seller_messages["unread_count"] == 1
    assert seller_messages["items"][0]["related_id"] == trade["id"]

    read = client.put(
        f"/api/v1/messages/{seller_messages['items'][0]['id']}/read",
        headers=auth_header(seller["token"]),
    )
    assert read.status_code == 200
    assert read.get_json()["data"]["is_read"] is True

    confirmed = client.put(
        f"/api/v1/trades/{trade['id']}/confirm",
        headers=auth_header(seller["token"]),
    )
    assert confirmed.status_code == 200
    buyer_titles, buyer_messages = message_titles(client, buyer["token"])
    assert "购买请求已确认" in buyer_titles
    assert buyer_messages["unread_count"] == 1

    completed = client.put(
        f"/api/v1/trades/{trade['id']}/complete",
        headers=auth_header(buyer["token"]),
    )
    assert completed.status_code == 200
    buyer_titles, buyer_messages = message_titles(client, buyer["token"])
    assert "交易已完成" in buyer_titles
    assert buyer_messages["unread_count"] == 2

    read_all = client.put(
        "/api/v1/messages/read-all",
        headers=auth_header(buyer["token"]),
    )
    assert read_all.status_code == 200
    assert read_all.get_json()["data"]["updated"] == 2
    _, unread_after = message_titles(client, buyer["token"], read=False)
    assert unread_after["total"] == 0

    second_product = create_product(client, seller["token"], title="M5 取消商品")
    second_trade = create_trade(client, buyer["token"], second_product["id"])
    cancelled = client.put(
        f"/api/v1/trades/{second_trade['id']}/cancel",
        headers=auth_header(buyer["token"]),
    )
    assert cancelled.status_code == 200
    seller_titles, _ = message_titles(client, seller["token"])
    assert "交易请求已取消" in seller_titles


def test_admin_governance_disables_users_and_writes_logs(client, app):
    with app.app_context():
        upsert_default_categories()
    seed_admin(app)
    admin = login(client, "admin_m5")
    user = register(client, "m5_managed_user")
    seller = register(client, "m5_product_seller")
    product = create_product(client, seller["token"], title="M5 管理商品")

    forbidden = client.get("/api/v1/admin/users", headers=auth_header(user["token"]))
    assert forbidden.status_code == 403
    assert forbidden.get_json()["error_code"] == "FORBIDDEN"

    users = client.get("/api/v1/admin/users", headers=auth_header(admin["token"]))
    assert users.status_code == 200
    assert users.get_json()["data"]["total"] >= 3

    disabled = client.put(
        f"/api/v1/admin/users/{user['user']['id']}/status",
        json={"status": "disabled"},
        headers=auth_header(admin["token"]),
    )
    assert disabled.status_code == 200
    assert disabled.get_json()["data"]["status"] == "disabled"

    old_token = client.get("/api/v1/users/me", headers=auth_header(user["token"]))
    assert old_token.status_code == 403
    assert old_token.get_json()["error_code"] == "USER_DISABLED"

    restored = client.put(
        f"/api/v1/admin/users/{user['user']['id']}/status",
        json={"status": "active"},
        headers=auth_header(admin["token"]),
    )
    assert restored.status_code == 200
    assert restored.get_json()["data"]["status"] == "active"

    product_status = client.put(
        f"/api/v1/admin/products/{product['id']}/status",
        json={"status": "off_shelf"},
        headers=auth_header(admin["token"]),
    )
    assert product_status.status_code == 200
    assert product_status.get_json()["data"]["status"] == "off_shelf"

    admin_products = client.get(
        "/api/v1/admin/products?status=off_shelf",
        headers=auth_header(admin["token"]),
    )
    assert admin_products.status_code == 200
    assert admin_products.get_json()["data"]["items"][0]["id"] == product["id"]

    announcement = client.post(
        "/api/v1/admin/announcements",
        json={
            "title": "M5 验收公告",
            "content": "今晚操场旁完成线下交易。",
            "status": "published",
        },
        headers=auth_header(admin["token"]),
    )
    assert announcement.status_code == 201
    announcement_id = announcement.get_json()["data"]["id"]

    public_list = client.get("/api/v1/announcements")
    assert public_list.status_code == 200
    assert public_list.get_json()["data"]["items"][0]["title"] == "M5 验收公告"

    hidden = client.put(
        f"/api/v1/admin/announcements/{announcement_id}",
        json={
            "title": "M5 验收公告更新",
            "content": "公告已隐藏。",
            "status": "hidden",
        },
        headers=auth_header(admin["token"]),
    )
    assert hidden.status_code == 200
    assert hidden.get_json()["data"]["status"] == "hidden"

    public_after_hidden = client.get("/api/v1/announcements")
    assert public_after_hidden.status_code == 200
    assert public_after_hidden.get_json()["data"]["total"] == 0

    deleted = client.delete(
        f"/api/v1/admin/announcements/{announcement_id}",
        headers=auth_header(admin["token"]),
    )
    assert deleted.status_code == 200

    logs = client.get("/api/v1/admin/logs", headers=auth_header(admin["token"]))
    assert logs.status_code == 200
    actions = {item["action"] for item in logs.get_json()["data"]["items"]}
    assert {
        "user_status_update",
        "product_status_update",
        "announcement_create",
        "announcement_update",
        "announcement_delete",
    }.issubset(actions)

    bad_logs = client.get(
        "/api/v1/admin/logs?operator_id=bad-id",
        headers=auth_header(admin["token"]),
    )
    assert bad_logs.status_code == 400
    assert bad_logs.get_json()["error_code"] == "VALIDATION_ERROR"
