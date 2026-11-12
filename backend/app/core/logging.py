"""Logging setup for the application."""

import logging


def configure_logging() -> None:
    """Configure a concise, consistent application log format."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
