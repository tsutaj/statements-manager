from __future__ import annotations
from statements_manager.src.params_maker.languages.cplusplus import CppParamsMaker
from typing import Any


lang_to_class = {
    ".cpp": CppParamsMaker,
    ".cc": CppParamsMaker,
    ".hpp": CppParamsMaker,
    ".h": CppParamsMaker,
}  # type: dict[str, Any]
