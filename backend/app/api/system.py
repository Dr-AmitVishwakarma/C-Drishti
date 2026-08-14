from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(
    prefix="/system",
    tags=["System"],
)


@router.get("/info")
def system_info():

    return {
        "name": "C-Drishti",
        "description": (
            "AI-Assisted Integrated "
            "Enforcement Intelligence Platform"
        ),
        "api_version": (
            settings.app_version
        ),
        "components": {
            "frontend": (
                "HTML / CSS / JavaScript"
            ),
            "backend": "FastAPI",
            "analytics": (
                "Python / Pandas"
            ),
            "retrieval": (
                "Sentence Transformers"
            ),
            "vector_database": (
                "ChromaDB"
            ),
            "local_llm": (
                settings.ollama_model
            ),
            "llm_runtime": "Ollama",
        },
    }