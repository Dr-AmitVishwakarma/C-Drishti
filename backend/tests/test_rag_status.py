def test_rag_status_endpoint(
    client,
):
    response = client.get(
        "/api/v1/rag/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[
        "collection"
    ] == "c_drishti_legal"

    assert isinstance(
        data[
            "ready"
        ],
        bool,
    )