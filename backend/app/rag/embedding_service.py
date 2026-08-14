from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.

    The first run may download the model.
    """

    return SentenceTransformer(MODEL_NAME)


def embed_documents(
    documents: list[str],
) -> list[list[float]]:
    """
    Generate embeddings for document chunks.
    """

    model = get_embedding_model()

    embeddings = model.encode_document(
        documents,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def embed_query(
    query: str,
) -> list[float]:
    """
    Generate an embedding for a retrieval query.
    """

    model = get_embedding_model()

    embedding = model.encode_query(
        query,
        normalize_embeddings=True,
    )

    return embedding.tolist()