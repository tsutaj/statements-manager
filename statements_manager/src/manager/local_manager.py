from __future__ import annotations

import pathlib
from typing import Any

from statements_manager.src.manager.base_manager import BaseManager


class LocalManager(BaseManager):
    def __init__(self, problem_attr: dict[str, Any]) -> None:
        super().__init__(problem_attr)

    def get_contents(self, statement_path: pathlib.Path) -> str:
        with open(statement_path) as f:
            return f.read()
