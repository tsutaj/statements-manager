import pathlib
import shutil
from abc import abstractmethod
from typing import Dict, Any
from jinja2 import Environment, DictLoader
from markdown import markdown
from logging import Logger, getLogger
from time import sleep
from src.params_maker.lang_to_class import lang_to_class
from src.variables_converter import VariablesConverter

logger = getLogger(__name__)  # type: Logger


class BaseManager:
    def __init__(self, project):
        self.project = project

    @abstractmethod
    def get_contents(self, statement_src: pathlib.Path) -> str:
        pass

    def replace_vars(self, html: str, problem: Dict[str, Any]) -> str:
        vars_manager = VariablesConverter(problem)
        env = Environment(
            variable_start_string="{@",
            variable_end_string="}",
            loader=DictLoader({"task": html}),
        )
        template = env.get_template("task")
        replaced_html = template.render(
            constraints=vars_manager["constraints"],
            samples=vars_manager["samples"],
        )
        return replaced_html

    def apply_template(self, html: str) -> str:
        style = self.project.get_attr("style")
        if pathlib.Path(style.get("template_src", "")).exists():
            with open(style["template_src"]) as f:
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
        output_dir = pathlib.Path(
            "./output/{}".format(self.project.get_attr("name", raise_error=True))
        )

        # make directory
        if self.project.get_attr("allow_rewrite"):
            if output_dir.exists():
                sleep_time = 4.0
                logger.warning(
                    "'{}' ALREADY EXISTS! try to rewrite.".format(output_dir)
                )
                logger.warning(
                    "sleep {}s... (quit if you want to cancel)".format(sleep_time)
                )
                sleep(sleep_time)
                logger.warning("remove existing directory")
                shutil.rmtree(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        elif output_dir.exists():
            logger.error("{} exists".format(output_dir))
            raise FileExistsError(output_dir, "exists")
        else:
            logger.info("making directory: {}".format(output_dir))
            output_dir.mkdir(parents=True)

        # copy files
        logger.info("setting html style")
        style = self.project.get_attr("style")
        for path in style.get("copied_files", []):
            path = pathlib.Path(path)
            shutil.copyfile(path, output_dir / pathlib.Path(path.name))
        logger.info("")

        # for each tasks
        problem_ids = set()
        for problem in self.project.get_attr("problem"):
            if "id" not in problem:
                logger.error("problem id is not set")
                raise KeyError("problem id is not set")
            if problem["id"] in problem_ids:
                logger.error("problem id '{}' appears twice".format(problem["id"]))
                raise ValueError("problem id '{}' appears twice".format(problem["id"]))
            problem_ids.add(problem["id"])
            logger.info("rendering [problem id: {}]".format(problem["id"]))

            # create params
            logger.info("create params file")
            if "params_path" in problem:
                ext = pathlib.Path(problem["params_path"]).suffix  # type: str
                if ext in lang_to_class:
                    params_maker = lang_to_class[ext](
                        problem["constraints"],
                        problem["params_path"],
                    )  # type: Any
                    params_maker.run()
                else:
                    logger.warning(
                        "skip: there is no language config which matches '{}'".format(
                            ext
                        )
                    )
            else:
                logger.warning("skip: params_path is not set")

            # get contents (main text)
            if "statement_src" not in problem:
                logger.error("statement_src is not set")
                raise KeyError("statement_src is not set")
            contents = self.get_contents(pathlib.Path(problem["statement_src"]))
            contents = self.replace_vars(contents, problem)

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
            output_path = output_dir / pathlib.Path(problem["id"] + ".html")
            self.save_html(html, output_path)
            logger.info("")
