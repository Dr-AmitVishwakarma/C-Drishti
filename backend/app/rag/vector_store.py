from pathlib import Path

import chromadb

from app.core.config import settings
from app.rag.embedding_service import (
    embed_documents,
    embed_query,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


CHROMA_PATH = (
    PROJECT_ROOT
    / "backend"
    / "storage"
    / "chroma"
)


COLLECTION_NAME = (
    settings.rag_collection_name
)


def get_chroma_client():
    """
    Create a persistent local ChromaDB client.
    """

    CHROMA_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=str(
            CHROMA_PATH
        )
    )


def get_collection():
    """
    Get or create the C-Drishti legal collection.
    """

    client = get_chroma_client()

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": (
                "Authoritative legal corpus "
                "for C-Drishti RAG"
            )
        },
    )


def reset_collection():
    """
    Completely rebuild the legal vector collection.
    """

    client = get_chroma_client()

    try:
        client.delete_collection(
            COLLECTION_NAME
        )

    except Exception:
        pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": (
                "Authoritative legal corpus "
                "for C-Drishti RAG"
            )
        },
    )


def index_chunks(
    chunks: list[dict],
) -> int:
    """
    Embed and store legal chunks.
    """

    if not chunks:
        return 0

    collection = reset_collection()

    batch_size = 64

    total_indexed = 0

    for start in range(
        0,
        len(chunks),
        batch_size,
    ):

        batch = chunks[
            start:start + batch_size
        ]

        documents = [
            chunk["text"]
            for chunk in batch
        ]

        embeddings = embed_documents(
            documents
        )

        ids = [
            chunk["id"]
            for chunk in batch
        ]

        metadatas = [
            chunk["metadata"]
            for chunk in batch
        ]

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        total_indexed += len(
            batch
        )

    return total_indexed


def search_chunks(
    query: str,
    top_k: int = 4,
) -> list[dict]:
    """
    Perform semantic retrieval over official legal documents.
    """

    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embed_query(
        query
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=min(
            top_k,
            collection.count(),
        ),
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = (
        results.get(
            "documents",
            [[]],
        )[0]
    )

    metadatas = (
        results.get(
            "metadatas",
            [[]],
        )[0]
    )

    distances = (
        results.get(
            "distances",
            [[]],
        )[0]
    )

    retrieved = []

    for index, document in enumerate(
        documents
    ):

        metadata = (
            metadatas[index]
            if index < len(
                metadatas
            )
            else {}
        )

        distance = (
            distances[index]
            if index < len(
                distances
            )
            else None
        )

        retrieved.append(
            {
                "text": document,
                "source": metadata.get(
                    "source",
                    "unknown",
                ),
                "title": metadata.get(
                    "title",
                    "Unknown document",
                ),
                "page": metadata.get(
                    "page"
                ),
                "section": metadata.get(
                    "section"
                ),
                "jurisdiction": metadata.get(
                    "jurisdiction"
                ),
                "authority": metadata.get(
                    "authority"
                ),
                "document_type": metadata.get(
                    "document_type"
                ),
                "distance": (
                    round(
                        float(
                            distance
                        ),
                        4,
                    )
                    if distance
                    is not None
                    else None
                ),
            }
        )

    return retrieved