import pathlib
import math
import shutil
from abc import abstractmethod
from typing import List, Dict, Any
from jinja2 import Environment, Template, DictLoader
from markdown import markdown

class VariantsManager:
    def __init__(self, problem: Dict[str, Any]):
        self.vars = {}
        self.vars["constraints"] = {}
        for name, value in problem.get("constraints", {}).items():
            print(name, value)
            self.vars["constraints"][name] = self.to_string(value)
        
        self.vars["samples"] = {}
        for name, path in problem.get("samples", {}).items():
            print(name, path)
            with open(pathlib.Path(path), "r") as f:
                sample_txt = f.read()
            self.vars["samples"][name] = "<pre>\n" + sample_txt + "</pre>\n"

    def to_string(self, value: Any) -> str:
        if isinstance(value, int):
            if str(value).endswith("000000"):
                k = math.floor(math.log10(abs(value)))
                if value == 10**k:
                    return "10^{{{}}}".format(k)
                elif value % (10**k) == 0:
                    return "{} \times 10^{{{}}}".format(value // 10**k, k)
                else:
                    return "{} \times 10^{{{}}}".format(value / 10**k, k)
            else:
                return format(value, ",").replace(",", "{,}")
        else:
            return str(value)
            
    def __getitem__(self, key: str) -> Dict[str, str]:
        return self.vars[key]
        
class BaseManager:
    def __init__(self, project):
        self.project = project

    @abstractmethod
    def get_contents(self, statement_src: pathlib.Path) -> List[str]:
        pass

    def replace_vars(self, html: str, problem: Dict[str, Any]) -> str:
        vars_manager = VariantsManager(problem)
        env = Environment(
            variable_start_string = "{@",
            variable_end_string = "}",
            loader = DictLoader({"task": html})
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
            variable_start_string = "{@",
            variable_end_string = "}",
            loader = DictLoader({"template": template})
        )
        replaced_html = env.get_template("template").render(
            task={"statements": html}
        )
        return replaced_html

    def save_html(self, html: str, output_path: pathlib.Path):
        with open(output_path, "w") as f:
            f.write(html)

    def run(self):
        output_dir = pathlib.Path(
            "./output/{}".format(
                self.project.get_attr("name", raise_error=True)
            )
        )

        # if output directory exists
        if output_dir.exists():
            raise FileExistsError(output_dir, "exists")
        else:
            output_dir.mkdir(parents=True)
        
        # copy files
        style = self.project.get_attr("style")
        for path in style.get("copied_files", []):
            path = pathlib.Path(path)
            shutil.copyfile(path, output_dir / pathlib.Path(path.name))
        
        # for each tasks
        for problem in self.project.get_attr("problem"):
            print(problem)
        
            # get contents (main text)
            contents = self.get_contents(pathlib.Path(problem["statement_src"]))
            contents = self.replace_vars(contents, problem)
            
            # convert: markdown -> html
            html = markdown(
                contents, extensions=[
                    "md_in_html",
                    "markdown.extensions.fenced_code",
                ]
            )
            html = self.apply_template(html)
            
            # save html
            output_path = output_dir / pathlib.Path(problem["id"] + ".html")
            self.save_html(html, output_path)
