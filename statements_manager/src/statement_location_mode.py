from __future__ import annotations

import pathlib
from enum import Enum
from logging import Logger, getLogger
from urllib.parse import urlparse

logger: Logger = getLogger(__name__)


class StatementLocationMode(Enum):
    UNKNOWN, LOCAL, DOCS = range(3)

    @staticmethod
    def read(mode: str | None):
        if mode is None:
            return StatementLocationMode.UNKNOWN
        elif mode.lower() == "local":
            return StatementLocationMode.LOCAL
        elif mode.lower() == "docs":
            return StatementLocationMode.DOCS
        else:
            raise NotImplementedError(f"unknown mode: {mode}")


def is_valid_url(url: str) -> bool:
    """
    check whether given string is valid as url format.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except BaseException:
        return False


def recognize_mode(
    statement_path: str, base_path: pathlib.Path
) -> StatementLocationMode:
    """
    recognize execute mode. ("docs" or "local")
    """
    if (base_path / pathlib.Path(statement_path)).exists():
        return StatementLocationMode.LOCAL
    else:
        return StatementLocationMode.DOCS
