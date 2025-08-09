from __future__ import annotations

import json
import os
import pickle
from pathlib import Path
from typing import Any, Union

import toml
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow


def is_ci() -> bool:
    return "GITHUB_ACTIONS" in os.environ


def to_path(path: str | None) -> Path | None:
    return Path(path) if path is not None else None


def find_in_parents(path: Path) -> Path | None:
    path = path.resolve()
    dir, filename = path.parent, path.name
    while not path.exists():
        if dir.parent == dir:
            return None
        dir = dir.parent
        path = dir / filename
    return path


def read_toml_file(path: Path | None) -> dict:
    if path is None or not path.exists():
        return {}
    return toml.load(path)


def read_text_file(path: Path | None, default: str, encoding: str) -> str:
    if path is None or not path.exists():
        return default
    with path.open("r", encoding=encoding) as f:
        return f.read()


def resolve_path(base_path: Path, path_str: str | None) -> str | None:
    if path_str is None:
        return None

    path = Path(path_str)
    if path.is_absolute():
        return str(path)
    else:
        return str(base_path / path)


def ask_ok(question: str, default_response: bool = True) -> bool:
    if default_response:
        print(question, "[Y/n]")
    else:
        print(question, "[y/N]")
    response = input().lower()
    if len(response) == 0:
        return default_response
    return response in ["y", "ye", "yes"]


def dict_merge(dct, merge_dct):
    for k, _ in merge_dct.items():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def create_token_for_ci() -> Any:
    service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_INFO"])
    return service_account.Credentials.from_service_account_info(service_account_info)


def create_token(
    creds_path: str, token_path: Union[str, None] = None, port: int = 0
) -> Any:
    if is_ci():
        return create_token_for_ci()

    scopes = ["https://www.googleapis.com/auth/documents.readonly"]
    if not Path(creds_path).exists():
        return None

    # set credentials
    token_obj = None
    existing_refresh_token = None
    if token_path and Path(token_path).exists():
        with open(token_path, "rb") as token:
            token_obj = pickle.load(token)
            if token_obj and hasattr(token_obj, "refresh_token"):
                existing_refresh_token = token_obj.refresh_token
    if not token_obj or not token_obj.valid:
        if token_obj and token_obj.expired and token_obj.refresh_token:
            token_obj.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
            authorization_url, _ = flow.authorization_url(access_type="offline")
            token_obj = flow.run_local_server(
                port=port, open_browser=True, bind_addr="0.0.0.0"
            )
            if existing_refresh_token and not token_obj.refresh_token:
                token_obj.refresh_token = existing_refresh_token
    if token_path and token_obj:
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "wb") as token:
            pickle.dump(token_obj, token)
    return token_obj
