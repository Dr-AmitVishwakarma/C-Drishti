import re
from pathlib import Path

from pypdf import PdfReader


RAG_DIRECTORY = Path(__file__).resolve().parent

DOCUMENTS_DIRECTORY = (
    RAG_DIRECTORY
    / "documents"
)


DOCUMENT_METADATA = {
    "motor_vehicles_act_1988.pdf": {
        "title": "Motor Vehicles Act, 1988",
        "jurisdiction": "India",
        "authority": "India Code",
        "document_type": "Central Act",
    },
    "environment_protection_act_1986.pdf": {
        "title": "Environment (Protection) Act, 1986",
        "jurisdiction": "India",
        "authority": "India Code",
        "document_type": "Central Act",
    },
    "bharatiya_sakshya_adhiniyam_2023.pdf": {
        "title": "Bharatiya Sakshya Adhiniyam, 2023",
        "jurisdiction": "India",
        "authority": "India Code",
        "document_type": "Central Act",
    },
    "chhattisgarh_cooperative_societies_act_1960.pdf": {
        "title": (
            "Chhattisgarh Co-operative "
            "Societies Act, 1960"
        ),
        "jurisdiction": "Chhattisgarh, India",
        "authority": "India Code",
        "document_type": "State Act",
    },
}


def clean_page_text(
    text: str,
) -> str:
    """
    Normalize extracted PDF text while retaining
    paragraph and section boundaries where possible.
    """

    text = text.replace(
        "\u00a0",
        " ",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def load_pdf_pages() -> list[dict]:
    """
    Extract text page-by-page from all legal PDFs.
    """

    if not DOCUMENTS_DIRECTORY.exists():
        raise FileNotFoundError(
            f"Documents directory not found: "
            f"{DOCUMENTS_DIRECTORY}"
        )

    pages = []

    pdf_files = sorted(
        DOCUMENTS_DIRECTORY.glob(
            "*.pdf"
        )
    )

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF legal documents were found."
        )

    for file_path in pdf_files:

        metadata = DOCUMENT_METADATA.get(
            file_path.name,
            {
                "title": file_path.stem,
                "jurisdiction": "Unknown",
                "authority": "Unknown",
                "document_type": "Legal document",
            },
        )

        reader = PdfReader(
            str(file_path)
        )

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):

            raw_text = (
                page.extract_text()
                or ""
            )

            clean_text = clean_page_text(
                raw_text
            )

            if not clean_text:
                continue

            pages.append(
                {
                    "source": file_path.name,
                    "title": metadata[
                        "title"
                    ],
                    "jurisdiction": metadata[
                        "jurisdiction"
                    ],
                    "authority": metadata[
                        "authority"
                    ],
                    "document_type": metadata[
                        "document_type"
                    ],
                    "page": page_number,
                    "content": clean_text,
                }
            )

    return pages


def detect_section(
    text: str,
) -> str | None:
    """
    Try to identify a legal section heading contained
    in the chunk.

    Examples:
        3. Necessity for driving licence.
        Section 65...
    """

    patterns = [
        r"(?im)^section\s+(\d+[A-Z]?)\b[.\-\s]*(.{0,100})",
        r"(?im)^(\d+[A-Z]?)\.\s+([A-Z][^\n]{3,100})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
        )

        if match:

            section_number = (
                match.group(1)
                .strip()
            )

            section_title = (
                match.group(2)
                .strip()
            )

            return (
                f"Section {section_number}"
                f" — {section_title}"
            )

    return None


def split_into_paragraphs(
    text: str,
) -> list[str]:
    """
    Preserve logical paragraph boundaries where possible.
    """

    paragraphs = re.split(
        r"\n\s*\n",
        text,
    )

    cleaned = []

    for paragraph in paragraphs:

        paragraph = " ".join(
            paragraph.split()
        ).strip()

        if paragraph:
            cleaned.append(
                paragraph
            )

    return cleaned


def chunk_page(
    text: str,
    max_chars: int = 1800,
) -> list[str]:
    """
    Build paragraph-aware chunks.

    Unlike the previous fixed-character chunker,
    this avoids cutting text every 900 characters
    regardless of sentence or paragraph structure.
    """

    paragraphs = split_into_paragraphs(
        text
    )

    chunks = []

    current_parts = []
    current_length = 0

    for paragraph in paragraphs:

        paragraph_length = len(
            paragraph
        )

        if (
            current_parts
            and current_length
            + paragraph_length
            + 2
            > max_chars
        ):

            chunks.append(
                "\n\n".join(
                    current_parts
                )
            )

            current_parts = []
            current_length = 0

        if paragraph_length > max_chars:

            sentences = re.split(
                r"(?<=[.!?])\s+",
                paragraph,
            )

            for sentence in sentences:

                if (
                    current_parts
                    and current_length
                    + len(sentence)
                    + 1
                    > max_chars
                ):

                    chunks.append(
                        " ".join(
                            current_parts
                        )
                    )

                    current_parts = []
                    current_length = 0

                current_parts.append(
                    sentence
                )

                current_length += (
                    len(sentence)
                    + 1
                )

        else:

            current_parts.append(
                paragraph
            )

            current_length += (
                paragraph_length
                + 2
            )

    if current_parts:

        chunks.append(
            "\n\n".join(
                current_parts
            )
        )

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]


def build_chunks() -> list[dict]:
    """
    Convert official legal PDFs into embedding-ready chunks
    with document and page metadata.
    """

    pages = load_pdf_pages()

    chunks = []

    chunk_counter = 0

    for page in pages:

        page_chunks = chunk_page(
            page["content"]
        )

        for page_chunk_index, chunk in enumerate(
            page_chunks,
            start=1,
        ):

            chunk_counter += 1

            section = detect_section(
                chunk
            )

            chunks.append(
                {
                    "id": (
                        f"legal-chunk-"
                        f"{chunk_counter}"
                    ),
                    "text": chunk,
                    "metadata": {
                        "source": page[
                            "source"
                        ],
                        "title": page[
                            "title"
                        ],
                        "page": page[
                            "page"
                        ],
                        "page_chunk": (
                            page_chunk_index
                        ),
                        "section": (
                            section
                            or "Section not detected"
                        ),
                        "jurisdiction": page[
                            "jurisdiction"
                        ],
                        "authority": page[
                            "authority"
                        ],
                        "document_type": page[
                            "document_type"
                        ],
                    },
                }
            )

    return chunks