import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def configure_logging() -> None:
    """
    Configure application-wide logging.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(
                sys.stdout
            )
        ],
        force=True,
    )

    logging.getLogger(
        "uvicorn.access"
    ).setLevel(
        logging.INFO
    )

    logging.getLogger(
        "httpx"
    ).setLevel(
        logging.WARNING
    )

    logging.getLogger(
        "chromadb"
    ).setLevel(
        logging.WARNING
    )