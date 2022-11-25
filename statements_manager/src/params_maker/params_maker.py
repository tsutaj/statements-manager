from __future__ import annotations

import pathlib
from abc import abstractmethod
from logging import Logger, getLogger
from typing import Any

logger: Logger = getLogger(__name__)


class ParamsMaker:
    def __init__(self, params: dict[str, Any], output_path: str) -> None:
        self.params = params
        self.output_path = output_path

    def run(self) -> None:
        params_lines: list[str] = []
        params_lines.append(self.header())
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
        params_lines.append("")

        # if params file is the same as the existing one, do nothing
        params_text = "\n".join(params_lines)
        if pathlib.Path(self.output_path).exists():
            with open(self.output_path, "r") as f:
                reference = f.read()
                if params_text == reference:
                    logger.warning(
                        "skip dumping constraints file: same result as before"
                    )
                    return

        with open(self.output_path, "w") as f:
            f.write(params_text)

    @abstractmethod
    def header(self) -> str:
        pass

    @abstractmethod
    def parse_int(self, key: str, value: int) -> str:
        pass

    @abstractmethod
    def parse_float(self, key: str, value: float) -> str:
        pass

    @abstractmethod
    def parse_str(self, key: str, value: str) -> str:
        pass
