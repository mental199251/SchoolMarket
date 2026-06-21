def assert_envelope(payload, success):
    assert payload["success"] is success
    assert set(payload) == {"success", "data", "message", "error_code"}


def test_health_returns_service_status_without_database(client, app, monkeypatch):
    def fail_if_called():
        raise AssertionError("/health must not access MongoDB")

    monkeypatch.setattr(app.extensions["mongo"], "ping", fail_if_called)

    response = client.get("/health")
    payload = response.get_json()

    assert response.status_code == 200
    assert_envelope(payload, True)
    assert payload["data"]["status"] == "healthy"
    assert response.headers["X-Request-ID"]


def test_ready_returns_success_when_database_is_available(client, app, monkeypatch):
    monkeypatch.setattr(
        app.extensions["mongo"],
        "ping",
        lambda: {"ok": 1.0},
    )

    response = client.get("/ready")
    payload = response.get_json()

    assert response.status_code == 200
    assert_envelope(payload, True)
    assert payload["data"]["dependencies"]["mongodb"] == "ready"


def test_ready_returns_503_when_database_is_unavailable(client, app, monkeypatch):
    def unavailable():
        raise TimeoutError("MongoDB is unavailable")

    monkeypatch.setattr(app.extensions["mongo"], "ping", unavailable)

    response = client.get("/ready")
    payload = response.get_json()

    assert response.status_code == 503
    assert_envelope(payload, False)
    assert payload["error_code"] == "DATABASE_UNAVAILABLE"


def test_not_found_uses_standard_error_response(client):
    response = client.get("/missing")
    payload = response.get_json()

    assert response.status_code == 404
    assert_envelope(payload, False)
    assert payload["error_code"] == "NOT_FOUND"


def test_method_not_allowed_uses_standard_error_response(client):
    response = client.post("/health")
    payload = response.get_json()

    assert response.status_code == 405
    assert_envelope(payload, False)
    assert payload["error_code"] == "METHOD_NOT_ALLOWED"


def test_unhandled_error_uses_standard_error_response(app):
    def raise_unhandled_error():
        raise RuntimeError("unexpected")

    app.add_url_rule("/test-error", view_func=raise_unhandled_error)
    response = app.test_client().get("/test-error")
    payload = response.get_json()

    assert response.status_code == 500
    assert_envelope(payload, False)
    assert payload["error_code"] == "INTERNAL_ERROR"
