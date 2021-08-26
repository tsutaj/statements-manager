from __future__ import annotations

from abc import abstractmethod
from logging import Logger, getLogger
from typing import Any

logger = getLogger(__name__)  # type: Logger


class ParamsMaker:
    def __init__(self, params: dict[str, Any], output_path: str) -> None:
        self.params = params
        self.output_path = output_path

    def run(self) -> None:
        params_lines = []  # type: list[str]
        for key, value in self.params.items():
            if not all(ord(c) < 128 for c in str(value)):
                logger.warning(f"ignored parameter: {key} => {value}")
                continue

            if isinstance(value, int):
                params_lines.append(self.parse_int(key, value))
            elif isinstance(value, float):
                params_lines.append(self.parse_float(key, value))
            elif isinstance(value, str):
                value = value.replace(r'"', r"\"")
                params_lines.append(self.parse_str(key, value))
            else:
                logger.warning(f"ignored parameter: {key} => {value}")

        with open(self.output_path, "w") as f:
            for line in params_lines:
                f.write(line + "\n")

    @abstractmethod
    def parse_int(self, key: str, value: int) -> str:
        pass

    @abstractmethod
    def parse_float(self, key: str, value: float) -> str:
        pass

    @abstractmethod
    def parse_str(self, key: str, value: str) -> str:
        pass
