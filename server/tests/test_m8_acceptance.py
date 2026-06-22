from io import BytesIO

from app.repositories.categories import upsert_default_categories


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def assert_envelope(response, success):
    payload = response.get_json()
    assert payload["success"] is success
    assert set(payload) == {"success", "data", "message", "error_code"}
    return payload


def register(client, username, password="Password123"):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password,
            "nickname": username,
            "campus": "东校区",
        },
    )
    assert response.status_code == 201
    return assert_envelope(response, True)["data"]


def create_product(client, token, **overrides):
    payload = {
        "title": "M8 验收教材",
        "description": "九成新，适合课程复习",
        "price_cents": 3600,
        "category_key": "books",
        "condition": "like_new",
        "images": [],
    }
    payload.update(overrides)
    response = client.post("/api/v1/products", json=payload, headers=auth_header(token))
    assert response.status_code == 201
    return assert_envelope(response, True)["data"]


def test_m8_full_acceptance_journey_and_state_conflicts(client, app):
    with app.app_context():
        upsert_default_categories()

    seller = register(client, "m8_seller")
    buyer = register(client, "m8_buyer")
    product = create_product(client, seller["token"])

    list_response = client.get("/api/v1/products?keyword=M8&sort=newest")
    list_payload = assert_envelope(list_response, True)
    assert list_response.status_code == 200
    assert list_payload["data"]["total"] == 1
    assert list_payload["data"]["items"][0]["id"] == product["id"]

    trade_response = client.post(
        "/api/v1/trades",
        json={"product_id": product["id"], "message": "可以今天校园内面交吗"},
        headers=auth_header(buyer["token"]),
    )
    assert trade_response.status_code == 201
    trade = assert_envelope(trade_response, True)["data"]
    assert trade["status"] == "pending"

    duplicate = client.post(
        "/api/v1/trades",
        json={"product_id": product["id"]},
        headers=auth_header(buyer["token"]),
    )
    assert duplicate.status_code == 409
    assert assert_envelope(duplicate, False)["error_code"] == "DUPLICATE_TRADE_REQUEST"

    confirmed = client.put(
        f"/api/v1/trades/{trade['id']}/confirm",
        headers=auth_header(seller["token"]),
    )
    assert confirmed.status_code == 200
    assert assert_envelope(confirmed, True)["data"]["status"] == "confirmed"

    completed = client.put(
        f"/api/v1/trades/{trade['id']}/complete",
        headers=auth_header(buyer["token"]),
    )
    assert completed.status_code == 200
    assert assert_envelope(completed, True)["data"]["status"] == "completed"

    repeat_complete = client.put(
        f"/api/v1/trades/{trade['id']}/complete",
        headers=auth_header(seller["token"]),
    )
    assert repeat_complete.status_code == 409
    conflict_payload = assert_envelope(repeat_complete, False)
    assert conflict_payload["error_code"] == "PRODUCT_UNAVAILABLE"
    assert conflict_payload["data"]["trade"]["status"] == "completed"

    sold_detail = client.get(
        f"/api/v1/products/{product['id']}",
        headers=auth_header(seller["token"]),
    )
    assert sold_detail.status_code == 200
    assert assert_envelope(sold_detail, True)["data"]["status"] == "sold"


def test_m8_upload_security_rejects_spoofed_and_oversized_files(client, app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    app.config["UPLOAD_IMAGE_MAX_BYTES"] = 32
    user = register(client, "m8_uploader")

    spoofed = client.post(
        "/api/v1/uploads/images",
        data={"images": (BytesIO(b"not really png"), "avatar.png")},
        headers=auth_header(user["token"]),
        content_type="multipart/form-data",
    )
    assert spoofed.status_code == 400
    assert assert_envelope(spoofed, False)["error_code"] == "VALIDATION_ERROR"

    oversized_png = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
        b"extra-bytes-that-push-the-file-over-the-test-limit"
    )
    oversized = client.post(
        "/api/v1/uploads/images",
        data={"images": (BytesIO(oversized_png), "too-large.png")},
        headers=auth_header(user["token"]),
        content_type="multipart/form-data",
    )
    assert oversized.status_code == 400
    assert assert_envelope(oversized, False)["error_code"] == "VALIDATION_ERROR"

    app.config["UPLOAD_IMAGE_MAX_BYTES"] = 1024
    safe_png = oversized_png[:33]
    accepted = client.post(
        "/api/v1/uploads/images",
        data={"images": (BytesIO(safe_png), "../../avatar.png")},
        headers=auth_header(user["token"]),
        content_type="multipart/form-data",
    )
    assert accepted.status_code == 201
    url = assert_envelope(accepted, True)["data"]["urls"][0]
    assert url.startswith("/uploads/images/")
    assert ".." not in url
    assert not (tmp_path / "avatar.png").exists()


def test_m8_ai_invalid_response_is_logged_as_failure(client, app, monkeypatch):
    user = register(client, "m8_ai_user")

    def invalid_generate(_prompt):
        return "模型没有按约定返回候选内容" * 20

    monkeypatch.setattr("app.services.ai._post_ollama_generate", invalid_generate)

    response = client.post(
        "/api/v1/ai/title",
        json={"description": "九成新蓝牙耳机，功能正常，续航稳定"},
        headers=auth_header(user["token"]),
    )
    assert response.status_code == 503
    assert assert_envelope(response, False)["error_code"] == "AI_UNAVAILABLE"

    with app.app_context():
        log = app.extensions["mongo"].db.ai_generation_logs.find_one(
            {"generation_type": "title"}
        )
    assert log["status"] == "failed"
    assert log["error_code"] == "AI_UNAVAILABLE"
