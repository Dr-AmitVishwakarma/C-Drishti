from app.core.config import settings

from app.rag.document_loader import (
    build_chunks,
)

from app.rag.vector_store import (
    get_collection,
    index_chunks,
    search_chunks,
)

from app.services.ollama_service import (
    generate_chat_response,
)


SYSTEM_PROMPT = """
You are the C-Drishti Legal and Policy Assistant.

You must answer only from the RETRIEVED LEGAL EVIDENCE
provided in the user prompt.

STRICT RULES:

1. Never use your own legal memory.
2. Never invent or guess a statute, section, offence,
   penalty, authority, case, rule, procedure, or legal fact.
3. If a legal proposition does not appear in the retrieved
   evidence, state that the evidence is insufficient.
4. Never substitute another Act for the Act asked about.
5. If the user asks about a named Act and the retrieved
   evidence does not contain that Act, do not answer.
6. If the user asks about a section and the retrieved evidence
   does not support that section, do not guess.
7. Do not treat an anomaly, AI alert, risk score, or prediction
   as proof of wrongdoing.
8. Consequential enforcement decisions require authorised
   human review and applicable legal procedure.
9. Cite only source information explicitly present in the
   retrieved evidence.
10. Do not provide legal advice.

If evidence is insufficient, respond:

"The retrieved legal evidence is insufficient to answer this
question reliably."

Do not add legal facts from memory after that statement.
""".strip()


MAX_ACCEPTABLE_DISTANCE = (
    settings.rag_max_distance
)


KNOWN_DOCUMENTS = {
    "motor vehicles act": (
        "Motor Vehicles Act, 1988"
    ),
    "environment protection act": (
        "Environment (Protection) Act, 1986"
    ),
    "environment (protection) act": (
        "Environment (Protection) Act, 1986"
    ),
    "bharatiya sakshya adhiniyam": (
        "Bharatiya Sakshya Adhiniyam, 2023"
    ),
    "co-operative societies act": (
        "Chhattisgarh Co-operative Societies Act, 1960"
    ),
    "cooperative societies act": (
        "Chhattisgarh Co-operative Societies Act, 1960"
    ),
}


def build_legal_index() -> dict:
    chunks = build_chunks()

    indexed_count = index_chunks(
        chunks
    )

    return {
        "status": "success",
        "collection": "c_drishti_legal",
        "indexed_chunks": indexed_count,
    }


def get_index_status() -> dict:
    collection = get_collection()

    count = collection.count()

    return {
        "collection": "c_drishti_legal",
        "indexed_chunks": count,
        "ready": count > 0,
    }


def retrieve_legal_context(
    query: str,
    top_k: int = 4,
) -> dict:

    query = query.strip()

    if not query:
        raise ValueError(
            "Query cannot be empty."
        )

    results = search_chunks(
        query=query,
        top_k=top_k,
    )

    return {
        "query": query,
        "top_k": top_k,
        "retrieved_chunks": len(
            results
        ),
        "results": results,
    }


def detect_requested_document(
    query: str,
) -> str | None:
    """
    Detect whether the user explicitly asked about
    one of the indexed Acts.
    """

    query_lower = query.lower()

    for phrase, title in KNOWN_DOCUMENTS.items():

        if phrase in query_lower:
            return title

    return None


def filter_relevant_results(
    query: str,
    results: list[dict],
) -> list[dict]:

    requested_document = (
        detect_requested_document(
            query
        )
    )

    relevant_results = []

    for result in results:

        distance = result.get(
            "distance"
        )

        if distance is None:
            continue

        if distance > MAX_ACCEPTABLE_DISTANCE:
            continue

        if requested_document:

            result_title = (
                result.get(
                    "title"
                )
                or ""
            )

            if (
                result_title.lower()
                != requested_document.lower()
            ):
                continue

        relevant_results.append(
            result
        )

    return relevant_results


def build_context_block(
    results: list[dict],
) -> str:

    context_parts = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        title = (
            result.get("title")
            or "Unknown document"
        )

        page = result.get(
            "page"
        )

        section = (
            result.get("section")
            or "Section not detected"
        )

        authority = (
            result.get("authority")
            or "Unknown authority"
        )

        text = (
            result.get("text")
            or ""
        )

        context_parts.append(
            (
                f"[SOURCE {index}]\n"
                f"Document: {title}\n"
                f"Authority: {authority}\n"
                f"Page: {page}\n"
                f"Section: {section}\n"
                f"Content:\n{text}"
            )
        )

    return "\n\n".join(
        context_parts
    )


def build_sources(
    results: list[dict],
) -> list[dict]:

    sources = []

    for result in results:

        source_record = {
            "source": result.get(
                "source"
            ),
            "title": result.get(
                "title"
            ),
            "page": result.get(
                "page"
            ),
            "section": result.get(
                "section"
            ),
            "authority": result.get(
                "authority"
            ),
            "distance": result.get(
                "distance"
            ),
        }

        if source_record not in sources:
            sources.append(
                source_record
            )

    return sources


def insufficient_evidence_response(
    query: str,
) -> dict:

    return {
        "query": query,
        "answer": (
            "The retrieved legal evidence is "
            "insufficient to answer this question reliably."
        ),
        "model": None,
        "retrieved_chunks": 0,
        "sources": [],
        "disclaimer": (
            "C-Drishti provides AI-assisted "
            "decision-support information only. "
            "Legal conclusions must be verified "
            "against authoritative sources."
        ),
    }


def ask_legal_assistant(
    query: str,
    top_k: int = 4,
) -> dict:

    retrieval = retrieve_legal_context(
        query=query,
        top_k=top_k,
    )

    raw_results = retrieval[
        "results"
    ]

    relevant_results = (
        filter_relevant_results(
            query=query,
            results=raw_results,
        )
    )

    if not relevant_results:
        return (
            insufficient_evidence_response(
                query=query
            )
        )

    context_block = (
        build_context_block(
            relevant_results
        )
    )

    user_prompt = f"""
USER QUESTION

{query}


RETRIEVED LEGAL EVIDENCE

{context_block}


INSTRUCTIONS

Answer only from the retrieved evidence above.

Do not use general knowledge or model memory.

If the question asks about a particular Act,
answer only if that Act appears in the retrieved evidence.

If the exact proposition cannot be established from the
evidence, say that the evidence is insufficient.

Do not invent section numbers.

End with:

Basis:
- Document
- Section
- Page

Only include information actually present above.
""".strip()

    answer = generate_chat_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    return {
        "query": query,
        "answer": answer,
        "model": settings.ollama_model,
        "retrieved_chunks": len(
            relevant_results
        ),
        "sources": build_sources(
            relevant_results
        ),
        "disclaimer": (
            "C-Drishti provides AI-assisted "
            "decision-support information only. "
            "Retrieved material and generated responses "
            "must be verified against authoritative "
            "sources before real-world use."
        ),
    }