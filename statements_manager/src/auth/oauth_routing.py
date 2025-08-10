from logging import Logger, getLogger
from typing import Any

from statements_manager.src.auth.oauth_config import get_auth_priority
from statements_manager.src.auth.oauth_login import (
    get_oauth_token as get_oauth_token_latest,
)
from statements_manager.src.auth.oauth_login_ci import get_token_for_ci
from statements_manager.src.auth.oauth_login_reg_creds import get_oauth_token_reg_creds
from statements_manager.src.utils import is_ci

logger: Logger = getLogger(__name__)


def get_oauth_token() -> Any:
    """
    Create token for Google Docs API access.

    This function uses the authentication priority setting to determine
    which authentication method to try first.
    """
    if is_ci():
        return get_token_for_ci()

    auth_priority = get_auth_priority()
    if auth_priority == "login":
        logger.debug("get oauth token: Trying OAuth2 login system first")
        oauth_token = get_oauth_token_latest()
        if oauth_token is not None:
            logger.debug("get oauth token: OAuth2 login system succeeded")
            return oauth_token

        logger.warning(
            "get oauth token: OAuth2 login system failed, "
            "trying user-registered credential file approach"
        )
        return get_oauth_token_reg_creds()
    else:
        logger.debug(
            "get oauth token: Trying user-registered credential file approach first"
        )
        oauth_token = get_oauth_token_reg_creds()
        if oauth_token is not None:
            logger.debug(
                "get oauth token: User-registered credential file approach succeeded"
            )
            return oauth_token

        logger.warning(
            "get oauth token: User-registered credential file approach failed, "
            "trying OAuth2 login system"
        )
        return get_oauth_token_latest()
