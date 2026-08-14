def test_rag_search_rejects_short_query(
    client,
):
    response = client.post(
        "/api/v1/rag/search",
        json={
            "query": "x",
            "top_k": 4,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data[
        "error"
    ][
        "type"
    ] == "validation_error"


def test_rag_search_rejects_invalid_top_k(
    client,
):
    response = client.post(
        "/api/v1/rag/search",
        json={
            "query": (
                "What does the Motor Vehicles Act say?"
            ),
            "top_k": 20,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data[
        "error"
    ][
        "type"
    ] == "validation_error"