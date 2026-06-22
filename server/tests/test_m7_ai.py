import pytest

from app.repositories import ai_generation_logs as log_repository


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def register(client, username="m7_user"):
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


def test_ai_generates_title_and_description_candidates(client, app, monkeypatch):
    user = register(client)

    def fake_generate(prompt):
        if "商品标题候选" in prompt:
            return '{"candidates":["高数教材带笔记","同济高数二手教材","课堂笔记高数教材"]}'
        return '{"candidates":["八成新教材，页面整洁，适合课程复习，线下自提。"]}'

    monkeypatch.setattr("app.services.ai._post_ollama_generate", fake_generate)

    title = client.post(
        "/api/v1/ai/title",
        json={
            "description": "同济版高等数学教材，八成新，附少量课堂笔记",
            "category_name": "教材资料",
            "condition": "good",
            "price_cents": 2800,
        },
        headers=auth_header(user["token"]),
    )
    assert title.status_code == 200
    title_data = title.get_json()["data"]
    assert title_data["candidates"][0] == "高数教材带笔记"
    assert title_data["model"] == app.config["OLLAMA_MODEL"]
    assert title_data["log_id"]

    description = client.post(
        "/api/v1/ai/description",
        json={
            "title": "高等数学教材",
            "category_name": "教材资料",
            "condition": "good",
            "price_cents": 2800,
        },
        headers=auth_header(user["token"]),
    )
    assert description.status_code == 200
    assert "八成新教材" in description.get_json()["data"]["candidates"][0]

    with app.app_context():
        logs = list(app.extensions["mongo"].db.ai_generation_logs.find({}))
    assert len(logs) == 2
    assert {log["generation_type"] for log in logs} == {"title", "description"}
    assert all(log["status"] == "success" for log in logs)


def test_ai_unavailable_is_logged_and_does_not_require_ollama(client, app, monkeypatch):
    user = register(client, "m7_unavailable")

    def fail_generate(_prompt):
        from app.services.ai import AIUnavailable

        raise AIUnavailable("无法连接 Ollama，请确认服务已启动")

    monkeypatch.setattr("app.services.ai._post_ollama_generate", fail_generate)

    response = client.post(
        "/api/v1/ai/title",
        json={"description": "九成新蓝牙耳机，功能正常"},
        headers=auth_header(user["token"]),
    )
    assert response.status_code == 503
    assert response.get_json()["error_code"] == "AI_UNAVAILABLE"

    with app.app_context():
        log = app.extensions["mongo"].db.ai_generation_logs.find_one({"generation_type": "title"})
    assert log["status"] == "failed"
    assert log["error_code"] == "AI_UNAVAILABLE"


def test_ai_status_reports_ollama_cloud_setup(client, app, monkeypatch):
    user = register(client, "m7_status")
    app.config["OLLAMA_MODEL"] = "gpt-oss:120b-cloud"

    def fake_request(method, path, payload=None):
        assert method == "GET"
        assert path == "/tags"
        assert payload is None
        return {"models": [{"name": "qwen2.5:7b"}]}

    monkeypatch.setattr("app.services.ai._request_ollama", fake_request)

    response = client.get("/api/v1/ai/status", headers=auth_header(user["token"]))
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["cloud_model"] is True
    assert data["service_available"] is True
    assert data["model_listed"] is False
    assert data["ready"] is True
    assert "ollama signin" in data["setup_hint"]


def test_ai_status_reports_unavailable_service(client, monkeypatch):
    user = register(client, "m7_status_down")

    def fake_request(_method, _path, payload=None):
        from app.services.ai import AIUnavailable

        raise AIUnavailable("无法连接 Ollama。后端机器需安装 Ollama，执行 ollama signin。")

    monkeypatch.setattr("app.services.ai._request_ollama", fake_request)

    response = client.get("/api/v1/ai/status", headers=auth_header(user["token"]))
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["service_available"] is False
    assert data["ready"] is False
    assert data["error_code"] == "AI_UNAVAILABLE"


@pytest.mark.parametrize(
    "endpoint,payload",
    [
        ("/api/v1/ai/title", {"description": "太短"}),
        ("/api/v1/ai/description", {"title": "书"}),
    ],
)
def test_ai_validates_minimum_input(client, endpoint, payload):
    user = register(client, "m7_validation")
    response = client.post(endpoint, json=payload, headers=auth_header(user["token"]))
    assert response.status_code == 400
    assert response.get_json()["error_code"] == "VALIDATION_ERROR"


def test_ai_requires_auth(client):
    response = client.post(
        "/api/v1/ai/title",
        json={"description": "九成新教材，页面整洁"},
    )
    assert response.status_code == 401
    assert response.get_json()["error_code"] == "AUTH_REQUIRED"
