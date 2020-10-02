from statements_manager.src.params_maker.languages.cplusplus import CppParamsMaker
from typing import Dict, Any


lang_to_class = {
    ".cpp": CppParamsMaker,
    ".cc": CppParamsMaker,
    ".hpp": CppParamsMaker,
    ".h": CppParamsMaker,
}  # type: Dict[str, Any]
