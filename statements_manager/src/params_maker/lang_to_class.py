from __future__ import annotations

from typing import Any

from statements_manager.src.params_maker.languages.cplusplus import CppParamsMaker

lang_to_class: dict[str, Any] = {
    ".cpp": CppParamsMaker,
    ".cc": CppParamsMaker,
    ".hpp": CppParamsMaker,
    ".h": CppParamsMaker,
}
