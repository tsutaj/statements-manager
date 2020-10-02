import pathlib
import math
import shutil
from abc import abstractmethod
from typing import Dict, Any
from jinja2 import Environment, DictLoader
from markdown import markdown
from logging import Logger, getLogger
from src.params_maker.lang_to_class import lang_to_class

logger = getLogger(__name__)  # type: Logger


class VariantsManager:
    def __init__(self, problem: Dict[str, Any]) -> None:
        self.vars = {}  # type: Dict[str, Any]
        self.vars["constraints"] = {}  # Dict[str, str]

        if "constraints" in problem:
            for name, value in problem["constraints"].items():
                logger.info("constraints: {} => {}".format(name, value))
                self.vars["constraints"][name] = self.to_string(value)
        else:
            logger.warning("constraints are not set")

        self.vars["samples"] = {}
        if "samples" in problem:
            n_sample = 1
            for sample in problem["samples"]:
                name = sample["id"]
                tp = sample.get("type", "default")
                logger.info("replace sample {} (type: {})".format(n_sample, tp))
                sample_text = ""
                if (tp == "default") or (tp == "input_only"):
                    with open(pathlib.Path(sample["input_path"]), "r") as f:
                        input_txt = f.read()
                        sample_text += "### 入力例 {}\n".format(n_sample)
                        sample_text += "<pre>\n" + input_txt + "</pre>\n"
                if (tp == "default") or (tp == "output_only"):
                    with open(pathlib.Path(sample["output_path"]), "r") as f:
                        output_txt = f.read()
                        sample_text += "### 出力例 {}\n".format(n_sample)
                        sample_text += "<pre>\n" + output_txt + "</pre>\n"
                if tp == "interactive":
                    with open(pathlib.Path(sample["interactive_path"]), "r") as f:
                        interactive_txt = f.read()
                        sample_text += "### 入出力例 {}\n".format(n_sample)
                        sample_text += interactive_txt
                self.vars["samples"][name] = sample_text
                n_sample += 1
        else:
            logger.warning("samples are not set")

    def to_string(self, value: Any) -> str:
        if isinstance(value, int):
            if str(value).endswith("000000"):
                k = math.floor(math.log10(abs(value)))
                if value == 10 ** k:
                    return "10^{{{}}}".format(k)
                elif value % (10 ** k) == 0:
                    return "{} \times 10^{{{}}}".format(value // 10 ** k, k)
                else:
                    return "{} \times 10^{{{}}}".format(value / 10 ** k, k)
            else:
                return format(value, ",").replace(",", "{,}")
        else:
            return str(value)

    def __getitem__(self, key: str) -> Dict[str, str]:
        if key not in self.vars:
            logger.error("unknown key: {}".format(key))
            raise KeyError("unknown key: {}".format(key))
        return self.vars[key]


class BaseManager:
    def __init__(self, project):
        self.project = project

    @abstractmethod
    def get_contents(self, statement_src: pathlib.Path) -> str:
        pass

    def replace_vars(self, html: str, problem: Dict[str, Any]) -> str:
        vars_manager = VariantsManager(problem)
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

        # if output directory exists
        if output_dir.exists():
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

        # for each tasks
        for problem in self.project.get_attr("problem"):
            if "id" not in problem:
                logger.error("problem id is not set")
                raise KeyError("problem id is not set")

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
            logger.info("rendering [problem id: {}]".format(problem["id"]))
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
