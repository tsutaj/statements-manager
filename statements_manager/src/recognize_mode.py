from __future__ import annotations

import pathlib
from logging import Logger, getLogger
from urllib.parse import urlparse

logger: Logger = getLogger(__name__)


def is_valid_url(url: str) -> bool:
    """
    check whether given string is valid as url format.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except BaseException:
        return False


def recognize_mode(statement_path: str, base_path: pathlib.Path) -> str:
    """
    recognize execute mode. ("docs" or "local")
    """

    # if "statement_path" is valid as local path, it may be "local"
    if (base_path / pathlib.Path(statement_path)).exists():
        return "local"
    # otherwise, it may be "docs"
    # it is either in URL-format or in ID-format.
    # URL-format: https://docs.google.com/document/d/{DOCUMENT_ID}/...
    else:
        return "docs"
