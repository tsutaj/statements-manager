from logging import Logger, getLogger
from typing import Any

from statements_manager.src.auth.oauth_login import (
    get_oauth_token as get_oauth_token_latest,
)
from statements_manager.src.auth.oauth_login_ci import get_token_for_ci
from statements_manager.src.auth.oauth_login_lecagy import get_oauth_token_legacy
from statements_manager.src.utils import is_ci

logger: Logger = getLogger(__name__)


def get_oauth_token() -> Any:
    """
    Create token for Google Docs API access.

    This function now prioritizes the new OAuth2 login system but maintains
    backward compatibility with the legacy credential file approach.
    """
    if is_ci():
        return get_token_for_ci()

    # Try new OAuth2 login system first
    oauth_token = get_oauth_token_latest()
    if oauth_token is not None:
        return oauth_token

    # Legacy credential file approach (for backward compatibility)
    logger.warning("get oauth token: Legacy credential file approach is used.")
    return get_oauth_token_legacy()
