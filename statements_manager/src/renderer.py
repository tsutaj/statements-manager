from __future__ import annotations

import pathlib
import re
from logging import Logger, getLogger
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any, Dict, List, Union

from jinja2 import DictLoader, Environment, StrictUndefined
from markdown import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from pyquery import PyQuery as pq

from statements_manager.src.execute_config import ProblemConfig, ProblemSetConfig
from statements_manager.src.variables_converter import VariablesConverter
from statements_manager.template import default_template_markdown

logger: Logger = getLogger(__name__)


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


class Renderer:
    def __init__(
        self,
        template_content: str,
        sample_template_content: str,
        preprocess_path: Union[str, None],
        postprocess_path: Union[str, None],
        preprocess_command: str,
        postprocess_command: str,
    ):
        self.template_content = template_content
        self.sample_template_content = sample_template_content
        self.preprocess_path = preprocess_path
        self.postprocess_path = postprocess_path
        self.preprocess_command = preprocess_command
        self.postprocess_command = postprocess_command
        self.replace_sample_format = ReplaceSampleFormatExprExtension()

    def replace_vars(
        self, problem_config: ProblemConfig, statement_str: str | None, encoding: str
    ) -> str:
        if statement_str is None:
            logger.error("statement_str is None")
            raise RuntimeError("statement_str is None")
        vars_manager = VariablesConverter(
            problem_config, self.sample_template_content, encoding
        )
        env = Environment(
            variable_start_string="{@",
            variable_end_string="}",
            loader=DictLoader({"task": statement_str}),
            undefined=StrictUndefined,
        )
        replaced_html = env.get_template("task").render(
            constraints=vars_manager.constraints,
            samples=vars_manager.samples,
        )
        return replaced_html

    def replace_assets_path(
        self, contents: str, problem_id: str, is_problemset: bool
    ) -> str:
        if is_problemset:
            contents = re.sub(
                r'(<img .*src="(?:|\./+)assets/+)(.+".*>)',
                f"\\1{problem_id}/\\2",
                contents,
            )
            contents = re.sub(
                r"(\\includegraphics\s*(?:\[[^\]]*\])?\s*\{\s*(?:\./+)?assets/)",
                rf"\1{problem_id}/",
                contents,
            )
        return contents

    def get_render_context(
        self,
        problemset_config: ProblemSetConfig,
        problem_ids: List[str],
        is_problemset: bool,
    ) -> Dict[str, Any]:
        context: Dict[str, Any] = {
            "problems": [],
            "is_problemset": is_problemset,
        }
        for problem_id in problem_ids:
            problem_config = problemset_config.get_problem(problem_id)
            problem_dict = {
                "id": problem_id,
                "lang": problem_config.statement.lang,
                "statement": problem_config.statement.rendered_text,
            }
            context["problems"].append(problem_dict)
        return context

    def apply_template(
        self,
        problemset_config: ProblemSetConfig,
        problem_ids: List[str],
        template: str,
        is_problemset: bool,
    ) -> str:
        env = Environment(
            variable_start_string="{@",
            variable_end_string="}",
            loader=DictLoader({"template": template}),
        )
        problems = self.get_render_context(
            problemset_config, problem_ids, is_problemset
        )
        replaced_html = env.get_template("template").render(problemset=problems)
        return replaced_html

    def apply_preprocess(self, markdown_text: str | None) -> str:
        if markdown_text is None:
            logger.error("markdown_text is None")
            raise RuntimeError("markdown_text is None")

        if self.preprocess_path is None:
            return markdown_text

        proc = Popen(
            [self.preprocess_command, self.preprocess_path],
            stdout=PIPE,
            stdin=PIPE,
            stderr=PIPE,
        )
        try:
            processed_text, stderr = proc.communicate(
                input=markdown_text.encode(encoding="utf-8"), timeout=10
            )
            if proc.returncode != 0:
                logger.error("preprocess execution failed!")
                logger.error(stderr.decode(encoding="utf-8"))
                raise RuntimeError("preprocess execution failed")
        except TimeoutExpired:
            proc.kill()
            raise TimeoutError("too long preprocess")
        return processed_text.decode(encoding="utf-8")

    def apply_postprocess(self, html_text: str) -> str:
        if self.postprocess_path is None:
            return html_text

        proc = Popen(
            [self.postprocess_command, self.postprocess_path],
            stdout=PIPE,
            stdin=PIPE,
            stderr=PIPE,
        )
        try:
            processed_text, stderr = proc.communicate(
                input=html_text.encode(encoding="utf-8"), timeout=10
            )
            if proc.returncode != 0:
                logger.error("postprocess execution failed!")
                logger.error(stderr.decode(encoding="utf-8"))
                raise RuntimeError("postprocess execution failed")
        except TimeoutExpired:
            proc.kill()
            raise TimeoutError("too long postprocess")
        return processed_text.decode(encoding="utf-8")

    def generate_html(
        self,
        problemset_config: ProblemSetConfig,
        problem_ids: List[str],
        is_problemset: bool,
    ) -> str:
        for problem_id in problem_ids:
            problem_config = problemset_config.get_problem(problem_id)
            if problem_config.statement.rendered_text is None:
                contents = problem_config.statement.raw_text
                contents = self.apply_preprocess(contents)

                rendered_contents = self.replace_vars(
                    problem_config, contents, problemset_config.encoding
                )
                markdown_extensions = [
                    self.replace_sample_format,
                    *problem_config.statement.markdown_extensions,
                ]
                rendered_contents = markdown(
                    rendered_contents, extensions=markdown_extensions
                )
                problem_config.statement.rendered_text = rendered_contents

            # 問題セットの場合、添付ファイルのパスを置換する
            problem_config.statement.rendered_text = self.replace_assets_path(
                problem_config.statement.rendered_text, problem_id, is_problemset
            )

        html = self.apply_template(
            problemset_config=problemset_config,
            problem_ids=problem_ids,
            template=self.template_content,
            is_problemset=is_problemset,
        )
        html = self.apply_postprocess(html)
        return html

    def generate_html_for_pdf(
        self,
        problemset_config: ProblemSetConfig,
        problem_ids: List[str],
        is_problemset: bool,
        pdf_path: str,
    ) -> str:
        html = self.generate_html(
            problemset_config=problemset_config,
            problem_ids=problem_ids,
            is_problemset=is_problemset,
        )
        # 添付ファイルへのパスを絶対パスにする
        dom = pq(html)
        for img in dom("img").items():
            img_url = img.attr["src"]
            if not img_url.startswith("http"):
                img_url = pathlib.Path(
                    pathlib.Path(pdf_path).resolve().parent / img_url
                )
            img.attr["src"] = str(img_url)
        html = dom.html()
        return html

    def generate_markdown(
        self,
        problemset_config: ProblemSetConfig,
        problem_ids: List[str],
        is_problemset: bool,
    ) -> str:
        for problem_id in problem_ids:
            problem_config = problemset_config.get_problem(problem_id)
            if problem_config.statement.rendered_text is None:
                contents = problem_config.statement.raw_text
                contents = self.replace_vars(
                    problem_config, contents, problemset_config.encoding
                )
                problem_config.statement.rendered_text = contents
            problem_config.statement.rendered_text = self.replace_assets_path(
                problem_config.statement.rendered_text, problem_id, is_problemset
            )

        md = self.apply_template(
            problemset_config=problemset_config,
            problem_ids=problem_ids,
            template=default_template_markdown,
            is_problemset=is_problemset,
        )
        return md

    def generate_custom(
        self,
        problemset_config: ProblemSetConfig,
        problem_ids: List[str],
        is_problemset: bool,
    ) -> str:
        for problem_id in problem_ids:
            problem_config = problemset_config.get_problem(problem_id)
            if problem_config.statement.rendered_text is None:
                contents = problem_config.statement.raw_text
                contents = self.apply_preprocess(contents)

                rendered_contents = self.replace_vars(
                    problem_config, contents, problemset_config.encoding
                )
                problem_config.statement.rendered_text = rendered_contents

            # 問題セットの場合、添付ファイルのパスを置換する
            problem_config.statement.rendered_text = self.replace_assets_path(
                problem_config.statement.rendered_text, problem_id, is_problemset
            )

        result = self.apply_template(
            problemset_config=problemset_config,
            problem_ids=problem_ids,
            template=self.template_content,
            is_problemset=is_problemset,
        )
        result = self.apply_postprocess(result)
        return result
