from app.services import rag_service


def test_grounded_answer_uses_retrieved_sources(
    monkeypatch,
):
    fake_results = [
        {
            "text": (
                "No person shall drive a motor vehicle "
                "in any public place unless he holds "
                "an effective driving licence."
            ),
            "source": "motor_vehicles_act_1988.pdf",
            "title": "Motor Vehicles Act, 1988",
            "page": 5,
            "section": (
                "Section 3 — Necessity for driving licence"
            ),
            "authority": "India Code",
            "distance": 1.10,
        }
    ]

    def fake_retrieval(
        query,
        top_k=4,
    ):
        return {
            "query": query,
            "top_k": top_k,
            "retrieved_chunks": 1,
            "results": fake_results,
        }

    def fake_generation(
        system_prompt,
        user_prompt,
    ):
        return (
            "The retrieved evidence states that "
            "a person must hold an effective driving "
            "licence to drive a motor vehicle in a "
            "public place.\n\n"
            "Basis:\n"
            "- Motor Vehicles Act, 1988\n"
            "- Section 3\n"
            "- Page 5"
        )

    monkeypatch.setattr(
        rag_service,
        "retrieve_legal_context",
        fake_retrieval,
    )

    monkeypatch.setattr(
        rag_service,
        "generate_chat_response",
        fake_generation,
    )

    result = rag_service.ask_legal_assistant(
        query=(
            "What does the Motor Vehicles Act say "
            "about the requirement for a driving licence?"
        ),
        top_k=4,
    )

    assert result[
        "model"
    ] is not None

    assert result[
        "retrieved_chunks"
    ] == 1

    assert len(
        result["sources"]
    ) == 1

    assert result[
        "sources"
    ][0][
        "title"
    ] == "Motor Vehicles Act, 1988"

    assert (
        "driving licence"
        in result[
            "answer"
        ].lower()
    )


def test_rag_refuses_when_no_relevant_evidence(
    monkeypatch,
):
    fake_results = [
        {
            "text": (
                "Environmental protection material"
            ),
            "source": (
                "environment_protection_act_1986.pdf"
            ),
            "title": (
                "Environment (Protection) Act, 1986"
            ),
            "page": 2,
            "section": (
                "Section 3 — Powers of Central Government"
            ),
            "authority": "India Code",
            "distance": 1.60,
        }
    ]

    def fake_retrieval(
        query,
        top_k=4,
    ):
        return {
            "query": query,
            "top_k": top_k,
            "retrieved_chunks": 1,
            "results": fake_results,
        }

    def should_not_generate(
        system_prompt,
        user_prompt,
    ):
        raise AssertionError(
            "Ollama generation should not run "
            "when retrieval evidence is insufficient."
        )

    monkeypatch.setattr(
        rag_service,
        "retrieve_legal_context",
        fake_retrieval,
    )

    monkeypatch.setattr(
        rag_service,
        "generate_chat_response",
        should_not_generate,
    )

    result = rag_service.ask_legal_assistant(
        query=(
            "What is the tax rate on cryptocurrency?"
        ),
        top_k=4,
    )

    assert result[
        "model"
    ] is None

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