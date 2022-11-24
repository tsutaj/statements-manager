import pathlib
import re
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any, Dict, List, Union

from jinja2 import DictLoader, Environment, StrictUndefined
from markdown import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from pyquery import PyQuery as pq

from statements_manager.src.variables_converter import VariablesConverter
from statements_manager.template import default_template_markdown


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
        template_html: str,
        sample_template_html: str,
        preprocess_path: Union[str, None],
        postprocess_path: Union[str, None],
    ):
        self.template_html = template_html
        self.sample_template_html = sample_template_html
        self.preprocess_path = preprocess_path
        self.postprocess_path = postprocess_path
        self.replace_sample_format = ReplaceSampleFormatExprExtension()

    def replace_vars(self, problem_attr: Dict[str, Any], statement_str: str) -> str:
        vars_manager = VariablesConverter(problem_attr, self.sample_template_html)
        env = Environment(
            variable_start_string="{@",
            variable_end_string="}",
            loader=DictLoader({"task": statement_str}),
            undefined=StrictUndefined,
        )
        replaced_html = env.get_template("task").render(
            constraints=vars_manager["constraints"],
            samples=vars_manager["samples"],
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
        return contents

    def get_render_context(
        self, problem_attr: Dict[str, Any], problem_ids: List[str], is_problemset: bool
    ) -> Dict[str, Any]:
        context: Dict[str, Any] = {
            "problems": [],
            "is_problemset": is_problemset,
        }
        for problem_id in problem_ids:
            problem_dict = {
                "id": problem_id,
                "lang": problem_attr[problem_id]["lang"],
                "statement": problem_attr[problem_id]["statement"],
            }
            context["problems"].append(problem_dict)
        return context

    def apply_template(
        self,
        problem_attr: Dict[str, Any],
        problem_ids: List[str],
        template: str,
        is_problemset: bool,
    ) -> str:
        env = Environment(
            variable_start_string="{@",
            variable_end_string="}",
            loader=DictLoader({"template": template}),
        )
        problems = self.get_render_context(problem_attr, problem_ids, is_problemset)
        replaced_html = env.get_template("template").render(problemset=problems)
        return replaced_html

    def apply_preprocess(self, markdown_text: str) -> str:
        if self.preprocess_path is None:
            return markdown_text

        proc = Popen(
            ["python", self.preprocess_path],
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

    def apply_postprocess(self, html_text: str) -> str:
        if self.postprocess_path is None:
            return html_text

        proc = Popen(
            ["python", self.postprocess_path],
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

    def generate_html(
        self,
        problem_attr: Dict[str, Any],
        problem_ids: List[str],
        is_problemset: bool,
    ) -> str:
        for problem_id in problem_ids:
            if "statement" not in problem_attr[problem_id]:
                contents = problem_attr[problem_id]["raw_statement"]
                contents = self.apply_preprocess(contents)

                rendered_contents = markdown(
                    contents,
                    extensions=[
                        self.replace_sample_format,
                        "md_in_html",
                        "tables",
                        "fenced_code",
                    ],
                )
                rendered_contents = self.replace_vars(
                    problem_attr[problem_id], rendered_contents
                )
                problem_attr[problem_id]["statement"] = rendered_contents

            # 問題セットの場合、添付ファイルのパスを置換する
            problem_attr[problem_id]["statement"] = self.replace_assets_path(
                problem_attr[problem_id]["statement"], problem_id, is_problemset
            )

        html = self.apply_template(
            problem_attr=problem_attr,
            problem_ids=problem_ids,
            template=self.template_html,
            is_problemset=is_problemset,
        )
        html = self.apply_postprocess(html)
        return html

    def generate_html_for_pdf(
        self,
        problem_attr: Dict[str, Any],
        problem_ids: List[str],
        is_problemset: bool,
        pdf_path: str,
    ) -> str:
        html = self.generate_html(
            problem_attr=problem_attr,
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
        problem_attr: Dict[str, Any],
        problem_ids: List[str],
        is_problemset: bool,
    ) -> str:
        for problem_id in problem_ids:
            if "statement" not in problem_attr[problem_id]:
                contents = problem_attr[problem_id]["raw_statement"]
                contents = self.replace_vars(problem_attr[problem_id], contents)
                problem_attr[problem_id]["statement"] = contents
            problem_attr[problem_id]["statement"] = self.replace_assets_path(
                problem_attr[problem_id]["statement"], problem_id, is_problemset
            )

        md = self.apply_template(
            problem_attr=problem_attr,
            problem_ids=problem_ids,
            template=default_template_markdown,
            is_problemset=is_problemset,
        )
        return md
