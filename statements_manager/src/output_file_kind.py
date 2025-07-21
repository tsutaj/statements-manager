from __future__ import annotations

import enum


@enum.unique
class OutputFileKind(enum.Enum):
    MARKDOWN = "md"
    HTML = "html"
    PDF = "pdf"
    CUSTOM = "custom"

    @staticmethod
    def values() -> list[str]:
        return [file_kind.value for file_kind in OutputFileKind]
