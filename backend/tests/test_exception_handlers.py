def test_missing_route_returns_unified_error_response(client):
    response = client.get("/api/v1/missing", headers={"x-request-id": "missing-route"})

    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["request_id"] == "missing-route"
    assert body["errors"][0]["code"] == "HTTP_ERROR"
