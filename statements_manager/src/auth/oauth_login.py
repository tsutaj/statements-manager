"""OAuth2 login functionality for Google Docs API access."""

from __future__ import annotations

import pickle
from logging import getLogger
from typing import Any, Optional

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from statements_manager.src.auth.oauth_config import (
    InstalledAppFlowConfig,
    cleanup_temp_file,
    create_temp_credentials_file,
    get_token_path,
)

logger = getLogger(__name__)


login_config = InstalledAppFlowConfig(
    scopes=["https://www.googleapis.com/auth/drive.file"],
    token_path=get_token_path("token_login.pickle"),
    port_number=37124,
)


def perform_oauth_login(force_reauth: bool = False) -> bool:
    """
    Perform OAuth2 login flow and save the token.

    Args:
        force_reauth: If True, force re-authentication even if valid token exists

    Returns:
        True if login was successful, False otherwise
    """
    token_path = login_config.token_path

    # Create hidden directory if it doesn't exist
    if not token_path.parent.exists():
        logger.info(f"Creating hidden directory: {token_path.parent}")
        token_path.parent.mkdir(parents=True, exist_ok=True)

    # Check existing token
    token_obj = None
    if not force_reauth and token_path.exists():
        try:
            with open(token_path, "rb") as token_file:
                token_obj = pickle.load(token_file)

            # Check if token is valid
            if token_obj and token_obj.valid:
                logger.info("Valid token already exists. Login not required.")
                return True

            # Try to refresh expired token
            if token_obj and token_obj.expired and token_obj.refresh_token:
                logger.info("Refreshing expired token...")
                try:
                    token_obj.refresh(Request())
                    # Save refreshed token
                    with open(token_path, "wb") as token_file:
                        pickle.dump(token_obj, token_file)
                    logger.info("Token refreshed successfully.")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}")
                    token_obj = None
        except Exception as e:
            logger.warning(f"Failed to load existing token: {e}")
            token_obj = None

    # Perform OAuth2 flow
    logger.info("Starting OAuth2 authentication flow...")
    logger.info(
        "A web browser will open for you to authenticate with your Google account."
    )

    temp_creds_file = None
    try:
        # Create temporary credentials file
        temp_creds_file = create_temp_credentials_file()

        # Create OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            temp_creds_file, login_config.scopes
        )

        # Run the OAuth2 flow
        token_obj = flow.run_local_server(
            port=login_config.port_number, open_browser=True, bind_addr="127.0.0.1"
        )

        # Save the token
        with open(token_path, "wb") as token_file:
            pickle.dump(token_obj, token_file)

        logger.info("OAuth2 authentication completed successfully!")
        logger.info(f"Token saved to: {token_path}")
        return True

    except Exception as e:
        logger.error(f"OAuth2 authentication failed: {e}")
        return False

    finally:
        # Clean up temporary credentials file
        if temp_creds_file:
            cleanup_temp_file(temp_creds_file)


def get_oauth_token() -> Optional[Any]:
    """
    Get the OAuth2 token for API access.

    Returns:
        The OAuth2 token object if available, None otherwise
    """
    token_path = login_config.token_path

    if not token_path.exists():
        return None

    try:
        with open(token_path, "rb") as token_file:
            token_obj = pickle.load(token_file)

        # Check if token is valid
        if token_obj and token_obj.valid:
            return token_obj

        # Try to refresh expired token
        if token_obj and token_obj.expired and token_obj.refresh_token:
            try:
                token_obj.refresh(Request())
                # Save refreshed token
                with open(token_path, "wb") as token_file:
                    pickle.dump(token_obj, token_file)
                return token_obj
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}")

    except Exception as e:
        logger.warning(f"Failed to load token: {e}")

    return None


def logout() -> bool:
    """
    Log out by removing the stored token.

    Returns:
        True if logout was successful, False otherwise
    """
    token_path = login_config.token_path

    try:
        if token_path.exists():
            token_path.unlink()
            logger.info("Logged out successfully. Token removed.")
        else:
            logger.info("No active session found.")
        return True
    except Exception as e:
        logger.error(f"Failed to logout: {e}")
        return False
