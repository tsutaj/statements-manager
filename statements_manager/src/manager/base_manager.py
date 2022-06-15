from __future__ import annotations

import pathlib
import shutil
from abc import abstractmethod
from logging import Logger, getLogger
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any, cast

import pdfkit
import pymdownx  # noqa: F401
from jinja2 import DictLoader, Environment, StrictUndefined
from markdown import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from statements_manager.src.params_maker.lang_to_class import lang_to_class
from statements_manager.src.variables_converter import VariablesConverter
from statements_manager.template import template_pdf_options

logger = getLogger(__name__)  # type: Logger


class ReplaceSampleFormatExpr(Preprocessor):
    def run(self, lines):
        cnt_all = 0
        new_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                match = line.strip() == "```"
                if match and cnt_all % 2 == 0:
                    new_lines.append("``` { .input-format .input-format }")
                else:
                    new_lines.append(line)
                cnt_all += 1
            else:
                new_lines.append(line)
        assert cnt_all % 2 == 0
        return new_lines


class ReplaceSampleFormatExprExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(
            ReplaceSampleFormatExpr(md), "replace_sample_format", 999
        )


class BaseManager:
    def __init__(self, problem_attr: dict[str, Any]):
        self._cwd = pathlib.Path.cwd()
        self.problem_attr = problem_attr  # type: dict[str, Any]
        self.state = True

    @abstractmethod
    def get_contents(self, statement_path: pathlib.Path) -> str:
        pass

    def replace_vars(self, html: str) -> str:
        vars_manager = VariablesConverter(self.problem_attr)
        env = Environment(
            variable_start_string="{@",
            variable_end_string="}",
            loader=DictLoader({"task": html}),
            undefined=StrictUndefined,
        )
        template = env.get_template("task")
        replaced_html = template.render(
            constraints=vars_manager["constraints"],
            samples=vars_manager["samples"],
        )
        return replaced_html

    def apply_template(self, html: str) -> str:
        env = Environment(
            variable_start_string="{@",
            variable_end_string="}",
            loader=DictLoader({"template": self.problem_attr["template_html"]}),
        )
        replaced_html = env.get_template("template").render(task={"statements": html})
        return replaced_html

    def apply_preprocess(self, markdown_text: str) -> str:
        if "preprocess_path" in self.problem_attr:
            proc = Popen(
                ["python", self.problem_attr["preprocess_path"]],
                stdout=PIPE,
                stdin=PIPE,
                stderr=PIPE,
            )
            try:
                processed_text, _ = proc.communicate(
                    input=markdown_text.encode(encoding="utf-8"), timeout=10
                )
            except TimeoutExpired:
                raise TimeoutError("too long preprocess")
            return processed_text.decode(encoding="utf-8")
        else:
            return markdown_text

    def apply_postprocess(self, html_text: str) -> str:
        if "postprocess_path" in self.problem_attr:
            proc = Popen(
                ["python", self.problem_attr["postprocess_path"]],
                stdout=PIPE,
                stdin=PIPE,
                stderr=PIPE,
            )
            try:
                processed_text, _ = proc.communicate(
                    input=html_text.encode(encoding="utf-8"), timeout=10
                )
            except TimeoutExpired:
                raise TimeoutError("too long postprocess")
            return processed_text.decode(encoding="utf-8")
        else:
            return html_text

    def save_html(self, html: str, output_path: pathlib.Path):
        with open(output_path, "w") as f:
            f.write(html)

    def run_problem(self) -> str:
        if not self.state:
            logger.info(f"skipped [problem id: {self.problem_attr['id']}]")
            return ""

        logger.info(f"rendering [problem id: {self.problem_attr['id']}]")

        # get contents (main text)
        if "statement_path" not in self.problem_attr:
            logger.error("statement_path is not set")
            raise KeyError("statement_path is not set")
        contents = self.get_contents(pathlib.Path(self.problem_attr["statement_path"]))
        contents = self.replace_vars(contents)

        # create params
        logger.info("create params file")
        if "params_path" in self.problem_attr and "constraints" in self.problem_attr:
            ext = pathlib.Path(self.problem_attr["params_path"]).suffix  # type: str
            if ext in lang_to_class:
                params_maker = lang_to_class[ext](
                    self.problem_attr["constraints"],
                    self.problem_attr["params_path"],
                )  # type: Any
                params_maker.run()
            else:
                logger.warning(
                    f"skip creating params: no language config which matches '{ext}'"
                )
        elif "constraints" not in self.problem_attr:
            logger.warning("skip creating params: constraints are not set")
        else:
            logger.warning("skip creating params: params_path is not set")

        # make output directory
        output_path = self.problem_attr["output_path"]
        if output_path.exists():
            logger.warning(f"output directory '{output_path}' already exists.")
        else:
            output_path.mkdir()

        # copy assets (related toml: problem)
        if "assets_path" in self.problem_attr:
            assets_src_path = pathlib.Path(self.problem_attr["assets_path"])
            assets_dst_path = output_path / pathlib.Path("assets")
            if assets_src_path.exists():
                logger.info("copy assets file")
                if assets_dst_path.exists():
                    logger.warning(
                        f"assets directory '{assets_dst_path}' already exists."
                    )
                shutil.copytree(assets_src_path, assets_dst_path, dirs_exist_ok=True)
            else:
                logger.warning(
                    f"assets_path '{self.problem_attr['assets_path']}' does not exist."
                )

        output_ext = self.problem_attr["output_ext"]
        result_html = ""
        logger.info(f"saving replaced {output_ext}")
        if output_ext == "html":
            # convert: markdown -> html
            replace_sample_format = ReplaceSampleFormatExprExtension()
            contents = self.apply_preprocess(contents)
            html = markdown(
                contents,
                extensions=[
                    replace_sample_format,
                    "md_in_html",
                    "tables",
                    "markdown.extensions.fenced_code",
                ],
            )
            html = self.apply_template(html)
            html = self.apply_postprocess(html)
            output_path = output_path / pathlib.Path(self.problem_attr["id"] + ".html")
            self.save_html(html, output_path)
        elif output_ext == "pdf":
            # convert: markdown -> html
            replace_sample_format = ReplaceSampleFormatExprExtension()
            contents = self.apply_preprocess(contents)
            html = markdown(
                contents,
                extensions=[
                    replace_sample_format,
                    "md_in_html",
                    "tables",
                    "markdown.extensions.fenced_code",
                    "pymdownx.pathconverter",
                ],
                extension_configs={
                    "pymdownx.pathconverter": {
                        "absolute": True,
                        "base_path": output_path.resolve(),
                    }
                },
            )
            result_html = html
            html = self.apply_template(html)
            html = self.apply_postprocess(html)
            output_path = output_path / pathlib.Path(self.problem_attr["id"] + ".pdf")

            wait_second = (
                int(cast(int, template_pdf_options["javascript-delay"])) // 1000
            )
            logger.info(f"please wait... ({wait_second} sec or greater)")
            pdfkit.from_string(html, output_path, options=template_pdf_options)
        elif output_ext == "md":
            output_path = output_path / pathlib.Path(self.problem_attr["id"] + ".md")
            with open(output_path, "w") as f:
                f.write(contents)
        else:
            logger.error(f"invalid extension '{output_ext}'")
            raise ValueError(f"invalid extension '{output_ext}'")
        return result_html

    def run_problemset(self, problemset_html: str, output_path: pathlib.Path) -> None:
        # PDF 出力モード以外で実行された場合は何もしない
        if len(problemset_html) == 0:
            return

        logger.info("create problemset pdf")
        html = self.apply_template(problemset_html)
        if output_path.exists():
            logger.warning(f"output directory '{output_path}' already exists.")
        else:
            output_path.mkdir()

        output_path = output_path / pathlib.Path("problemset.pdf")
        template_pdf_options["javascript-delay"] = 10000
        wait_second = int(cast(int, template_pdf_options["javascript-delay"])) // 1000
        logger.info(f"please wait... ({wait_second} sec or greater)")
        pdfkit.from_string(html, output_path, options=template_pdf_options)
