import pickle
from pathlib import Path
from typing import Any, Tuple, Union

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


def resolve_path(base_path: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    else:
        return base_path / path


def ask_ok(question: str, default_response: bool = True) -> bool:
    if default_response:
        print(question, "[Y/n]")
    else:
        print(question, "[y/N]")
    response = input().lower()
    if len(response) == 0:
        return default_response
    return response in ["y", "ye", "yes"]


def create_token(
    creds_path: str, token_path: Union[str, None] = None
) -> Tuple[Any, Any]:
    scopes = ["https://www.googleapis.com/auth/documents.readonly"]
    token_obj = None

    # set credentials
    if token_path and Path(token_path).exists():
        with open(token_path, "rb") as token:
            token_obj = pickle.load(token)
    if not token_obj or not token_obj.valid:
        if token_obj and token_obj.expired and token_obj.refresh_token:
            token_obj.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
            token_obj = flow.run_local_server(port=0)
    return token_obj
