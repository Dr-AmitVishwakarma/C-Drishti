from pydantic import BaseModel, Field


class RagSearchRequest(BaseModel):

    query: str = Field(
        min_length=2,
        max_length=1000,
    )

    top_k: int = Field(
        default=4,
        ge=1,
        le=10,
    )


class RagSearchResult(BaseModel):

    text: str

    source: str

    title: str | None = None

    page: int | None = None

    section: str | None = None

    jurisdiction: str | None = None

    authority: str | None = None

    document_type: str | None = None

    distance: float | None = None


class RagSearchResponse(BaseModel):

    query: str

    top_k: int

    retrieved_chunks: int

    results: list[
        RagSearchResult
    ]


class RagIndexResponse(BaseModel):

    status: str

    collection: str

    indexed_chunks: int


class RagStatusResponse(BaseModel):

    collection: str

    indexed_chunks: int

    ready: bool


class RagSource(BaseModel):

    source: str | None = None

    title: str | None = None

    page: int | None = None

    section: str | None = None

    authority: str | None = None

    distance: float | None = None


class RagAskResponse(BaseModel):

    query: str

    answer: str

    model: str | None

    retrieved_chunks: int

    sources: list[
        RagSource
    ]

    disclaimer: str


class OllamaStatusResponse(BaseModel):

    available: bool

    base_url: str

    configured_model: str

    model_available: bool

    installed_models: list[str]