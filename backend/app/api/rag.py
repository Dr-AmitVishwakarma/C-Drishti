from fastapi import (
    APIRouter,
    HTTPException,
)

from app.models.rag import (
    OllamaStatusResponse,
    RagAskResponse,
    RagIndexResponse,
    RagSearchRequest,
    RagSearchResponse,
    RagStatusResponse,
)

from app.services.ollama_service import (
    OllamaGenerationError,
    OllamaUnavailableError,
    check_ollama_status,
)

from app.services.rag_service import (
    ask_legal_assistant,
    build_legal_index,
    get_index_status,
    retrieve_legal_context,
)


router = APIRouter(
    prefix="/rag",
    tags=["Legal RAG"],
)


@router.get(
    "/status",
    response_model=RagStatusResponse,
)
def rag_status():

    try:
        return get_index_status()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to read "
                "RAG index status."
            ),
        ) from exc


@router.get(
    "/ollama/status",
    response_model=OllamaStatusResponse,
)
def ollama_status():

    return check_ollama_status()


@router.post(
    "/index",
    response_model=RagIndexResponse,
)
def rebuild_rag_index():

    try:
        return build_legal_index()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to build "
                "legal RAG index."
            ),
        ) from exc


@router.post(
    "/search",
    response_model=RagSearchResponse,
)
def search_legal_knowledge(
    request: RagSearchRequest,
):

    try:
        return retrieve_legal_context(
            query=request.query,
            top_k=request.top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to search "
                "legal knowledge base."
            ),
        ) from exc


@router.post(
    "/ask",
    response_model=RagAskResponse,
)
def ask_legal_knowledge(
    request: RagSearchRequest,
):

    try:
        return ask_legal_assistant(
            query=request.query,
            top_k=request.top_k,
        )

    except OllamaUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "The local Ollama service is unavailable. "
                "Start Ollama and try again."
            ),
        ) from exc

    except OllamaGenerationError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Ollama could not generate a valid response."
            ),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate the "
                "RAG-assisted answer."
            ),
        ) from exc