def test_unknown_route_returns_clean_404(
    client,
):
    response = client.get(
        "/api/v1/does-not-exist"
    )

    assert response.status_code == 404

    data = response.json()

    assert "error" in data

    assert data["error"][
        "type"
    ] == "http_error"

    assert data["error"][
        "status_code"
    ] == 404