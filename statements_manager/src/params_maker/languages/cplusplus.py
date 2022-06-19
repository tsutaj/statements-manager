from __future__ import annotations

from typing import Any

from statements_manager.src.params_maker.params_maker import ParamsMaker


class CppParamsMaker(ParamsMaker):
    def __init__(self, params: dict[str, Any], output_path: str) -> None:
        super().__init__(params, output_path)

    def header(self) -> str:
        return "#pragma once\n"

    def parse_int(self, key: str, value: int) -> str:
        return f"const long long int {key} = {value};"

    def parse_float(self, key: str, value: float) -> str:
        return f"const double {key} = {value};"

    def parse_str(self, key: str, value: str) -> str:
        return f'const std::string {key} = "{value}";'
