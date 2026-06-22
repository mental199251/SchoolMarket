from io import BytesIO

from app.repositories.categories import upsert_default_categories
from app.repositories.products import update_product_status


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


def create_product(client, token, **overrides):
    payload = {
        "title": "高等数学教材",
        "description": "八成新，附课堂笔记",
        "price_cents": 2800,
        "category_key": "books",
        "condition": "good",
        "images": [],
    }
    payload.update(overrides)
    return client.post("/api/v1/products", json=payload, headers=auth_header(token))


def test_categories_and_public_product_list(client, app):
    with app.app_context():
        upsert_default_categories()
    seller = register(client, "seller_a")
    buyer = register(client, "buyer_a")
    product_response = create_product(
        client,
        seller["token"],
        title="线性代数教材",
        price_cents=2200,
        category_key="books",
    )
    assert product_response.status_code == 201

    categories = client.get("/api/v1/categories")
    assert categories.status_code == 200
    assert {item["key"] for item in categories.get_json()["data"]["items"]} >= {
        "books",
        "electronics",
        "daily",
        "sports",
    }

    list_response = client.get(
        "/api/v1/products?keyword=线性&category_key=books&sort=price_asc"
    )
    payload = list_response.get_json()
    assert list_response.status_code == 200
    assert payload["data"]["total"] == 1
    assert payload["data"]["items"][0]["title"] == "线性代数教材"
    assert payload["data"]["items"][0]["owner"]["username"] == "seller_a"

    detail = client.get(f"/api/v1/products/{payload['data']['items'][0]['id']}")
    assert detail.status_code == 200
    assert detail.get_json()["data"]["price_cents"] == 2200

    # Authenticated non-owner should still only see public available items.
    authed_detail = client.get(
        f"/api/v1/products/{payload['data']['items'][0]['id']}",
        headers=auth_header(buyer["token"]),
    )
    assert authed_detail.status_code == 200


def test_owner_can_update_status_and_delete_product(client, app):
    with app.app_context():
        upsert_default_categories()
    seller = register(client, "seller_b")
    other = register(client, "buyer_b")
    created = create_product(client, seller["token"], title="蓝牙耳机").get_json()["data"]
    product_id = created["id"]

    forbidden = client.put(
        f"/api/v1/products/{product_id}",
        json={**created, "title": "试图修改"},
        headers=auth_header(other["token"]),
    )
    assert forbidden.status_code == 403
    assert forbidden.get_json()["error_code"] == "FORBIDDEN"

    updated = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "title": "蓝牙耳机 Pro",
            "description": "几乎全新",
            "price_cents": 8800,
            "category_key": "electronics",
            "condition": "like_new",
            "images": [],
        },
        headers=auth_header(seller["token"]),
    )
    assert updated.status_code == 200
    assert updated.get_json()["data"]["title"] == "蓝牙耳机 Pro"

    off_shelf = client.put(
        f"/api/v1/products/{product_id}/status",
        json={"action": "off_shelf"},
        headers=auth_header(seller["token"]),
    )
    assert off_shelf.status_code == 200
    assert off_shelf.get_json()["data"]["status"] == "off_shelf"
    assert client.get(f"/api/v1/products/{product_id}").status_code == 404

    restore = client.put(
        f"/api/v1/products/{product_id}/status",
        json={"action": "restore"},
        headers=auth_header(seller["token"]),
    )
    assert restore.status_code == 200
    assert restore.get_json()["data"]["status"] == "available"

    delete_response = client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_header(seller["token"]),
    )
    assert delete_response.status_code == 200
    assert delete_response.get_json()["data"]["deleted"] is True
    assert client.get(f"/api/v1/products/{product_id}").status_code == 404


def test_my_products_and_sold_product_restrictions(client, app):
    with app.app_context():
        upsert_default_categories()
    seller = register(client, "seller_c")
    created = create_product(client, seller["token"], title="羽毛球拍").get_json()["data"]
    product_id = created["id"]

    my_products = client.get(
        "/api/v1/products?mine=true",
        headers=auth_header(seller["token"]),
    )
    assert my_products.status_code == 200
    assert my_products.get_json()["data"]["items"][0]["title"] == "羽毛球拍"

    with app.app_context():
        update_product_status(product_id, "sold")

    edit_sold = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "title": "羽毛球拍",
            "description": "想改已售商品",
            "price_cents": 4500,
            "category_key": "sports",
            "condition": "good",
            "images": [],
        },
        headers=auth_header(seller["token"]),
    )
    assert edit_sold.status_code == 409
    assert edit_sold.get_json()["error_code"] == "PRODUCT_UNAVAILABLE"


def test_image_upload_validation(client, app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    user = register(client, "uploader")
    png = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
    )
    response = client.post(
        "/api/v1/uploads/images",
        data={"images": (BytesIO(png), "image.png")},
        headers=auth_header(user["token"]),
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    url = response.get_json()["data"]["urls"][0]
    assert url.startswith("/uploads/images/")
    assert (tmp_path / "images" / url.rsplit("/", 1)[-1]).exists()

    invalid = client.post(
        "/api/v1/uploads/images",
        data={"images": (BytesIO(b"not an image"), "bad.png")},
        headers=auth_header(user["token"]),
        content_type="multipart/form-data",
    )
    assert invalid.status_code == 400
    assert invalid.get_json()["error_code"] == "VALIDATION_ERROR"
