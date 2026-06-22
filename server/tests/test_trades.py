from app.repositories.categories import upsert_default_categories


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def register(client, username):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "Password123",
            "nickname": username,
            "campus": "东校区",
        },
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def create_product(client, token, title="交易测试商品"):
    response = client.post(
        "/api/v1/products",
        json={
            "title": title,
            "description": "用于交易状态机测试",
            "price_cents": 5200,
            "category_key": "books",
            "condition": "good",
            "images": [],
        },
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def create_trade(client, token, product_id, expected=201):
    response = client.post(
        "/api/v1/trades",
        json={"product_id": product_id, "message": "想买这个"},
        headers=auth_header(token),
    )
    assert response.status_code == expected
    return response


def test_trade_happy_path_marks_product_sold(client, app):
    with app.app_context():
        upsert_default_categories()
    seller = register(client, "trade_seller")
    buyer = register(client, "trade_buyer")
    product = create_product(client, seller["token"])

    trade_response = create_trade(client, buyer["token"], product["id"])
    trade = trade_response.get_json()["data"]
    assert trade["status"] == "pending"
    assert trade["buyer"]["username"] == "trade_buyer"
    assert trade["seller"]["username"] == "trade_seller"

    buy_list = client.get("/api/v1/trades/my-buy", headers=auth_header(buyer["token"]))
    assert buy_list.status_code == 200
    assert buy_list.get_json()["data"]["items"][0]["id"] == trade["id"]

    sell_list = client.get("/api/v1/trades/my-sell", headers=auth_header(seller["token"]))
    assert sell_list.status_code == 200
    assert sell_list.get_json()["data"]["items"][0]["id"] == trade["id"]

    confirmed = client.put(
        f"/api/v1/trades/{trade['id']}/confirm",
        headers=auth_header(seller["token"]),
    )
    assert confirmed.status_code == 200
    assert confirmed.get_json()["data"]["status"] == "confirmed"

    completed = client.put(
        f"/api/v1/trades/{trade['id']}/complete",
        headers=auth_header(buyer["token"]),
    )
    assert completed.status_code == 200
    assert completed.get_json()["data"]["status"] == "completed"
    assert completed.get_json()["data"]["completed_by"] == buyer["user"]["id"]

    product_detail = client.get(
        f"/api/v1/products/{product['id']}",
        headers=auth_header(seller["token"]),
    )
    assert product_detail.status_code == 200
    assert product_detail.get_json()["data"]["status"] == "sold"


def test_trade_rejects_self_buy_duplicate_and_wrong_actor(client, app):
    with app.app_context():
        upsert_default_categories()
    seller = register(client, "reject_seller")
    buyer = register(client, "reject_buyer")
    stranger = register(client, "reject_stranger")
    product = create_product(client, seller["token"], title="重复请求商品")

    self_buy = create_trade(client, seller["token"], product["id"], expected=403)
    assert self_buy.get_json()["error_code"] == "FORBIDDEN"

    trade = create_trade(client, buyer["token"], product["id"]).get_json()["data"]
    duplicate = create_trade(client, buyer["token"], product["id"], expected=409)
    assert duplicate.get_json()["error_code"] == "DUPLICATE_TRADE_REQUEST"

    buyer_confirm = client.put(
        f"/api/v1/trades/{trade['id']}/confirm",
        headers=auth_header(buyer["token"]),
    )
    assert buyer_confirm.status_code == 403
    assert buyer_confirm.get_json()["error_code"] == "FORBIDDEN"

    stranger_cancel = client.put(
        f"/api/v1/trades/{trade['id']}/cancel",
        headers=auth_header(stranger["token"]),
    )
    assert stranger_cancel.status_code == 403
    assert stranger_cancel.get_json()["error_code"] == "FORBIDDEN"

    stranger_complete = client.put(
        f"/api/v1/trades/{trade['id']}/complete",
        headers=auth_header(stranger["token"]),
    )
    assert stranger_complete.status_code == 403
    assert stranger_complete.get_json()["error_code"] == "FORBIDDEN"


def test_trade_cancel_and_repeat_complete_conflicts(client, app):
    with app.app_context():
        upsert_default_categories()
    seller = register(client, "state_seller")
    buyer = register(client, "state_buyer")
    product = create_product(client, seller["token"], title="状态冲突商品")

    cancelled_trade = create_trade(client, buyer["token"], product["id"]).get_json()["data"]
    cancelled = client.put(
        f"/api/v1/trades/{cancelled_trade['id']}/cancel",
        headers=auth_header(buyer["token"]),
    )
    assert cancelled.status_code == 200
    assert cancelled.get_json()["data"]["status"] == "cancelled"

    confirm_cancelled = client.put(
        f"/api/v1/trades/{cancelled_trade['id']}/confirm",
        headers=auth_header(seller["token"]),
    )
    assert confirm_cancelled.status_code == 409
    assert confirm_cancelled.get_json()["data"]["trade"]["status"] == "cancelled"

    new_trade = create_trade(client, buyer["token"], product["id"]).get_json()["data"]
    assert (
        client.put(
            f"/api/v1/trades/{new_trade['id']}/confirm",
            headers=auth_header(seller["token"]),
        ).status_code
        == 200
    )
    assert (
        client.put(
            f"/api/v1/trades/{new_trade['id']}/complete",
            headers=auth_header(seller["token"]),
        ).status_code
        == 200
    )

    repeat_complete = client.put(
        f"/api/v1/trades/{new_trade['id']}/complete",
        headers=auth_header(buyer["token"]),
    )
    assert repeat_complete.status_code == 409
    assert repeat_complete.get_json()["data"]["trade"]["status"] == "completed"


def test_trade_rejects_unavailable_product(client, app):
    with app.app_context():
        upsert_default_categories()
    seller = register(client, "unavailable_seller")
    buyer = register(client, "unavailable_buyer")
    product = create_product(client, seller["token"], title="已下架商品")

    off_shelf = client.put(
        f"/api/v1/products/{product['id']}/status",
        json={"action": "off_shelf"},
        headers=auth_header(seller["token"]),
    )
    assert off_shelf.status_code == 200

    response = create_trade(client, buyer["token"], product["id"], expected=409)
    assert response.get_json()["error_code"] == "PRODUCT_UNAVAILABLE"
