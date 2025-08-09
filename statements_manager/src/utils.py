from __future__ import annotations

import os
from pathlib import Path

import toml


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
