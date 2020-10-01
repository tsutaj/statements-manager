from abc import abstractmethod
from typing import List, Dict, Any
import logging


class ParamsMaker:
    def __init__(self, params: Dict[str, Any], output_path: str) -> None:
        self.params = params
        self.output_path = output_path
        self.log = logging.getLogger(__name__)

    def run(self) -> None:
        params_lines = []  # type: List[str]
        for key, value in self.params.items():
            if not all(ord(c) < 128 for c in str(value)):
                continue

            if isinstance(value, int):
                params_lines.append(self.parse_int(key, value))
            elif isinstance(value, float):
                params_lines.append(self.parse_float(key, value))
            elif isinstance(value, str):
                params_lines.append(self.parse_str(key, value))
            else:
                self.log.info("ignored parameter: {}: {}".format(key, value))

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
