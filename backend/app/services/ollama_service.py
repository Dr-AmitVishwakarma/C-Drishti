import httpx

from app.core.config import settings


class OllamaUnavailableError(Exception):
    """
    Raised when the local Ollama service cannot be reached.
    """


class OllamaGenerationError(Exception):
    """
    Raised when Ollama returns an invalid response.
    """


def check_ollama_status() -> dict:
    """
    Check whether the local Ollama API is available.
    """

    try:
        response = httpx.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=5.0,
        )

        response.raise_for_status()

        payload = response.json()

        models = [
            model.get("name")
            for model in payload.get(
                "models",
                []
            )
        ]

        return {
            "available": True,
            "base_url": settings.ollama_base_url,
            "configured_model": settings.ollama_model,
            "model_available": (
                settings.ollama_model
                in models
            ),
            "installed_models": models,
        }

    except (
        httpx.ConnectError,
        httpx.TimeoutException,
        httpx.HTTPError,
    ):

        return {
            "available": False,
            "base_url": settings.ollama_base_url,
            "configured_model": settings.ollama_model,
            "model_available": False,
            "installed_models": [],
        }


def generate_chat_response(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    Generate a grounded response using the local Ollama
    chat API.
    """

    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "options": {
            "temperature": 0.1,
        },
    }

    try:
        response = httpx.post(
            f"{settings.ollama_base_url}/api/chat",
            json=payload,
            timeout=120.0,
        )

        response.raise_for_status()

    except (
        httpx.ConnectError,
        httpx.TimeoutException,
    ) as exc:

        raise OllamaUnavailableError(
            "Unable to connect to the local Ollama service."
        ) from exc

    except httpx.HTTPStatusError as exc:

        raise OllamaGenerationError(
            "Ollama returned an HTTP error."
        ) from exc

    data = response.json()

    message = data.get(
        "message",
        {}
    )

    content = message.get(
        "content",
        ""
    ).strip()

    if not content:
        raise OllamaGenerationError(
            "Ollama returned an empty response."
        )

    return content