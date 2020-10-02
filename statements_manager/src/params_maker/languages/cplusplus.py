from statements_manager.src.params_maker.params_maker import ParamsMaker
from typing import Dict, Any


class CppParamsMaker(ParamsMaker):
    def __init__(self, params: Dict[str, Any], output_path: str) -> None:
        super().__init__(params, output_path)

    def parse_int(self, key: str, value: int) -> str:
        return "const long long int {} = {};".format(key, value)

    def parse_float(self, key: str, value: float) -> str:
        return "const double {} = {};".format(key, value)

    def parse_str(self, key: str, value: str) -> str:
        return 'const std::string {} = "{}";'.format(key, value)
