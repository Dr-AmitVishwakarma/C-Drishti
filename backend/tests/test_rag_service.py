from app.services.rag_service import (
    detect_requested_document,
    filter_relevant_results,
    insufficient_evidence_response,
)


def test_detect_motor_vehicles_act():
    result = detect_requested_document(
        "What does the Motor Vehicles Act say about driving licences?"
    )

    assert result == "Motor Vehicles Act, 1988"


def test_detect_environment_act():
    result = detect_requested_document(
        "What powers exist under the Environment Protection Act?"
    )

    assert result == "Environment (Protection) Act, 1986"


def test_detect_unknown_document_returns_none():
    result = detect_requested_document(
        "What is the tax rate on cryptocurrency income?"
    )

    assert result is None


def test_filter_relevant_results_by_distance():
    results = [
        {
            "title": "Motor Vehicles Act, 1988",
            "distance": 1.10,
        },
        {
            "title": "Motor Vehicles Act, 1988",
            "distance": 1.60,
        },
    ]

    filtered = filter_relevant_results(
        query="What does the Motor Vehicles Act say?",
        results=results,
    )

    assert len(filtered) == 1
    assert filtered[0]["distance"] == 1.10


def test_filter_relevant_results_by_requested_act():
    results = [
        {
            "title": "Motor Vehicles Act, 1988",
            "distance": 1.10,
        },
        {
            "title": "Environment (Protection) Act, 1986",
            "distance": 1.05,
        },
    ]

    filtered = filter_relevant_results(
        query="What does the Motor Vehicles Act say?",
        results=results,
    )

    assert len(filtered) == 1

    assert filtered[0][
        "title"
    ] == "Motor Vehicles Act, 1988"


def test_insufficient_evidence_response():
    result = insufficient_evidence_response(
        query="What is the tax rate on cryptocurrency?"
    )

    assert result["model"] is None

    assert result[
        "retrieved_chunks"
    ] == 0

    assert result[
        "sources"
    ] == []

    assert (
        "insufficient"
        in result[
            "answer"
        ].lower()
    )