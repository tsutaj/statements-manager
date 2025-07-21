from __future__ import annotations

import pathlib
from logging import Logger, getLogger
from typing import Any
from urllib.parse import urlparse

import toml

from statements_manager.src.statement_location_mode import (
    StatementLocationMode,
    is_valid_url,
    recognize_mode,
)
from statements_manager.src.utils import read_text_file, resolve_path, to_path
from statements_manager.template import (
    default_sample_template,
    default_template,
    template_pdf_options,
)

logger: Logger = getLogger(__name__)


class AttributeConstraints:
    def required(self, name: str | pathlib.Path, config: dict, key: str):
        if key not in config:
            logger.error(f"{name} has not '{key}' key.")
            raise KeyError(f"{name} has not '{key}' key.")
        return config[key]

    def optional(
        self, name: str | pathlib.Path, config: dict, key: str, default_value: Any
    ):
        if key not in config:
            logger.debug(f"{name} has not '{key}' key. set {default_value}.")
        return config.get(key, default_value)


class StatementConfig(AttributeConstraints):
    def __init__(self, filename: pathlib.Path, config: dict) -> None:
        self.path: str = self.required(filename, config, "path")
        self.lang: str = self.optional(filename, config, "lang", "en")
        self.digit_separator: str = self.optional(
            filename, config, "digit_separator", ","
        )
        self.exponential_threshold: int = self.optional(
            filename, config, "exponential_threshold", 1000000
        )
        self.markdown_extensions: list[Any] = self.optional(
            filename, config, "markdown_extensions", []
        )
        self.mode = StatementLocationMode.read(
            self.optional(filename, config, "mode", None)
        )
        if self.mode == StatementLocationMode.UNKNOWN:
            dirname = filename.parent.resolve()
            self.mode = recognize_mode(self.path, dirname)
            logger.debug(f"recognize mode: file = {self.path}, mode = {self.mode}")
            # When docs mode, the path is either in URL-format or in ID-format.
            # URL-format: https://docs.google.com/document/d/{DOCUMENT_ID}/...
            if self.mode == StatementLocationMode.DOCS and is_valid_url(self.path):
                self.path = urlparse(self.path).path.split("/")[3]

        # below are used on rendering.
        self.raw_text: str | None = None
        self.rendered_text: str | None = None


class RawProblemConfig(AttributeConstraints):
    def __init__(self, filename: pathlib.Path, config: dict) -> None:
        dirname = filename.parent.resolve()
        self.id: str = self.required(filename, config, "id")
        self.assets_path: str | None = self.optional(
            filename, config, "assets_path", None
        )
        self.sample_path: str = self.optional(
            filename, config, "sample_path", dirname / pathlib.Path("tests")
        )
        self.ignore_samples: list[str] = self.optional(
            filename, config, "ignore_samples", []
        )
        self.params_path: str | None = self.optional(
            filename, config, "params_path", None
        )
        self.statements: list[StatementConfig] = [
            StatementConfig(filename, c)
            for c in self.required(filename, config, "statements")
        ]
        self.constraints: dict | None = self.optional(
            filename, config, "constraints", None
        )


class TemplatePathConfig(AttributeConstraints):
    def __init__(self, filename: pathlib.Path, config: dict):
        self.template_path: str | None = self.optional(
            filename, config, "template_path", None
        )
        self.sample_template_path: str | None = self.optional(
            filename, config, "sample_template_path", None
        )
        self.preprocess_path: str | None = self.optional(
            filename, config, "preprocess_path", None
        )
        self.postprocess_path: str | None = self.optional(
            filename, config, "postprocess_path", None
        )
        self.preprocess_command: str = self.optional(
            filename, config, "preprocess_command", "python3"
        )
        self.postprocess_command: str = self.optional(
            filename, config, "postprocess_command", "python3"
        )
        self.output_extension: str | None = self.optional(
            filename, config, "output_extension", None
        )

        dirname = filename.parent.resolve()
        self.template_path = resolve_path(dirname, self.template_path)
        self.sample_template_path = resolve_path(dirname, self.sample_template_path)
        self.preprocess_path = resolve_path(dirname, self.preprocess_path)
        self.postprocess_path = resolve_path(dirname, self.postprocess_path)


class PDFRenderingConfig(AttributeConstraints):
    def __init__(self, filename: pathlib.Path, config: dict) -> None:
        self.common: dict = self.optional(
            filename, config, "common", template_pdf_options
        )
        self.problem: dict = self.optional(filename, config, "problem", {})
        self.problemset: dict = self.optional(filename, config, "problemset", {})


class ProblemConfig(AttributeConstraints):
    def __init__(
        self,
        filename: pathlib.Path,
        id: str,
        raw_config: RawProblemConfig,
        statement_config: StatementConfig,
    ) -> None:
        self.id = id
        self.assets_path: str | None = raw_config.assets_path
        self.sample_path: str = raw_config.sample_path
        self.ignore_samples: list[str] = raw_config.ignore_samples
        self.params_path: str | None = raw_config.params_path
        self.statement: StatementConfig = statement_config
        self.constraints: dict | None = raw_config.constraints

        dirname = filename.parent.resolve()
        self.assets_path = resolve_path(dirname, self.assets_path)
        self.sample_path = resolve_path(dirname, self.sample_path)  # type: ignore
        self.params_path = resolve_path(dirname, self.params_path)
        self.output_path: str = resolve_path(dirname, "ss-out")  # type: ignore
        if self.statement.mode == StatementLocationMode.LOCAL:
            self.statement.path = resolve_path(dirname, self.statement.path)  # type: ignore


def get_numbered_ids(config: RawProblemConfig) -> list[str]:
    statements = config.statements
    original_id = config.id
    lang_count: dict[str, int] = {}
    lang_number: dict[str, int] = {}
    for statement_info in statements:
        lang = statement_info.lang
        lang_number.setdefault(lang, 0)
        lang_count.setdefault(lang, 0)
        lang_count[lang] += 1

    numbered_ids = []
    for statement_info in statements:
        id = original_id
        lang = statement_info.lang
        lang_number[lang] += 1
        # 1 個しかないならナンバリングしない
        problem_id = f"{id}"
        if lang_count[lang] > 1:
            problem_id += f"{lang_number[lang]}"
        if len(lang_count) > 1:
            problem_id += f"_{lang}"
        numbered_ids.append(problem_id)
    return numbered_ids


class ProblemSetConfig(AttributeConstraints):
    def __init__(self, problemset_filename: pathlib.Path, config: dict) -> None:
        self.template = TemplatePathConfig(
            problemset_filename, config.get("template", {})
        )
        self.pdf_config = PDFRenderingConfig(problemset_filename, config.get("pdf", {}))
        self.known_ids: set[str] = set()
        self.id_groups: list[list[str]] = list()
        self.problem_configs: dict[str, ProblemConfig] = dict()
        self.encoding: str = self.optional(
            problemset_filename, config, "encoding", "utf-8"
        )
        logger.info(f"encoding = {self.encoding}")

        dirname = problemset_filename.parent.resolve()
        self.output_path = dirname / "problemset"
        self.template_content: str = read_text_file(
            to_path(self.template.template_path), default_template, self.encoding
        )
        self.sample_template_content: str = read_text_file(
            to_path(self.template.sample_template_path),
            default_sample_template,
            self.encoding,
        )

    def get_problem(self, id: str) -> ProblemConfig:
        return self.required("ProblemConfigs", self.problem_configs, id)

    def get_problem_ids(self) -> list[str]:
        return sorted(list(self.problem_configs.keys()))

    def get_problem_group(self, id: str) -> list[str]:
        for group in self.id_groups:
            if id in group:
                return group
        logger.error("problem id not found in any group")
        raise ValueError("problem id not found in any group")

    def add_problem_configs(self, filename: pathlib.Path) -> None:
        raw_config = RawProblemConfig(filename, toml.load(filename))
        self._check_id(raw_config)
        numbered_ids = get_numbered_ids(raw_config)
        self.id_groups.append(numbered_ids)
        for id, statement_config in zip(numbered_ids, raw_config.statements):
            self.problem_configs[id] = ProblemConfig(
                filename, id, raw_config, statement_config
            )

    def _check_id(self, config: RawProblemConfig) -> None:
        if config.id in self.known_ids:
            logger.error(f"problem id '{config.id}' appears twice")
            raise ValueError(f"problem id '{config.id}' appears twice")
        self.known_ids.add(config.id)
