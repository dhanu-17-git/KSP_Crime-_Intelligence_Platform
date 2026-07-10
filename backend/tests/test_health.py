def test_health_check_returns_unified_response(client):
    response = client.get("/api/v1/health", headers={"x-request-id": "test-request-id"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request-id"

    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Service is healthy"
    assert body["data"] == {"status": "ok"}
    assert body["errors"] == []
    assert body["request_id"] == "test-request-id"
    assert "timestamp" in body
