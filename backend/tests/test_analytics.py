def test_analytics_endpoint_returns_hybrid_data(
    client,
):
    response = client.get(
        "/api/v1/analytics/anomalies"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[
        "method"
    ].startswith(
        "Hybrid anomaly detection"
    )

    assert data[
        "total_centres"
    ] > 0

    assert (
        "statistical_flagged"
        in data
    )

    assert (
        "ml_flagged"
        in data
    )

    assert (
        "hybrid_flagged"
        in data
    )

    assert (
        "anomalies"
        in data
    )


def test_analytics_top_limit(
    client,
):
    response = client.get(
        "/api/v1/analytics/anomalies?top=3"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[
        "returned_results"
    ] <= 3


def test_analytics_rejects_invalid_top(
    client,
):
    response = client.get(
        "/api/v1/analytics/anomalies?top=0"
    )

    assert response.status_code == 422

    data = response.json()

    assert data[
        "error"
    ][
        "type"
    ] == "validation_error"


def test_analytics_summary(
    client,
):
    response = client.get(
        "/api/v1/analytics/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[
        "total_centres"
    ] > 0

    assert (
        data[
            "hybrid_flagged"
        ]
        >= 0
    )