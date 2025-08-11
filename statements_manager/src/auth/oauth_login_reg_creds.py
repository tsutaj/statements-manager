import pickle
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from statements_manager.src.auth.oauth_config import (
    InstalledAppFlowConfig,
    get_credentials_path,
    get_token_path,
)

reg_creds_config = InstalledAppFlowConfig(
    scopes=["https://www.googleapis.com/auth/documents.readonly"],
    token_path=get_token_path("token.pickle"),
    port_number=37123,
)


def get_oauth_token_reg_creds() -> Any:
    creds_path = get_credentials_path()
    token_path = reg_creds_config.token_path
    if not Path(creds_path).exists():
        return None

    # set credentials
    token_obj = None
    if token_path and Path(token_path).exists():
        with open(token_path, "rb") as token:
            token_obj = pickle.load(token)
    if not token_obj or not token_obj.valid:
        if token_obj and token_obj.expired and token_obj.refresh_token:
            token_obj.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, reg_creds_config.scopes
            )
            token_obj = flow.run_local_server(
                port=reg_creds_config.port_number,
                open_browser=False,
                bind_addr="0.0.0.0",
            )
    return token_obj
