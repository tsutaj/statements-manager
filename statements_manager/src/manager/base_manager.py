from __future__ import annotations
import pathlib
import shutil
from abc import abstractmethod
from typing import Any
from jinja2 import Environment, DictLoader, StrictUndefined
from markdown import markdown
from logging import Logger, getLogger
from statements_manager.src.params_maker.lang_to_class import lang_to_class
from statements_manager.src.variables_converter import VariablesConverter
from statements_manager.src.utils import resolve_path

logger = getLogger(__name__)  # type: Logger


class BaseManager:
    def __init__(self, problem_attr):
        self._cwd = pathlib.Path.cwd()
        self.problem_attr = problem_attr  # type: dict[str, Any]

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
        style = self.problem_attr["style"]
        if pathlib.Path(style.get("template_path", "")).exists():
            with open(style["template_path"]) as f:
                template = f.read()
        else:
            template = "{@task.statements}"

        env = Environment(
            variable_start_string="{@",
            variable_end_string="}",
            loader=DictLoader({"template": template}),
        )
        replaced_html = env.get_template("template").render(task={"statements": html})
        return replaced_html

    def save_html(self, html: str, output_path: pathlib.Path):
        with open(output_path, "w") as f:
            f.write(html)

    def run(self):
        logger.info(f"rendering [problem id: {self.problem_attr['id']}]")

        # make output directory
        output_path = self.problem_attr["output_path"]
        if output_path.exists():
            logger.info(f"output directory '{output_path}' already exists.")
        else:
            output_path.mkdir()

        # copy files
        logger.info("setting html style")
        style = self.problem_attr["style"]
        for path in style.get("copied_files", []):
            path = resolve_path(self._cwd, pathlib.Path(path))
            shutil.copyfile(path, output_path / pathlib.Path(path.name))

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

        # get contents (main text)
        if "statement_path" not in self.problem_attr:
            logger.error("statement_path is not set")
            raise KeyError("statement_path is not set")
        contents = self.get_contents(pathlib.Path(self.problem_attr["statement_path"]))
        contents = self.replace_vars(contents)

        # convert: markdown -> html
        html = markdown(
            contents,
            extensions=[
                "md_in_html",
                "tables",
                "markdown.extensions.fenced_code",
            ],
        )
        html = self.apply_template(html)

        # save html
        logger.info("saving replaced html")
        output_path = output_path / pathlib.Path(self.problem_attr["id"] + ".html")
        self.save_html(html, output_path)
        logger.info("")
