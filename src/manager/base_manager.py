import markdown
import pathlib
from abc import abstractmethod
from typing import List

class BaseManager:
    def __init__(self, project):
        self.project = project

    @abstractmethod
    def get_contents(self, statement_src: pathlib.Path) -> List[str]:
        pass

    def replace_vars(self, contents, problem):
        # TODO (変数を置換する)
        return contents

    def add_header_footer(self, html, problem):
        # TODO (html にヘッダーとフッターを追加する)
        return html

    def save_html(self, html: str, output_path: pathlib.Path):
        with open(output_path, "w") as f:
            f.write(html)

    def run(self):
        output_dir = pathlib.Path("./output/{}".format(
            self.project.get_attr("name", raise_error=True)
            )
            )

        # if output directory exists
        if output_dir.exists():
            raise FileExistsError(output_dir, "exists")
        else:
            output_dir.mkdir(parents=True)
        
        # for each tasks
        for problem in self.project.get_attr("problem"):
            print(problem)
        
            # get contents (main text)
            contents = self.get_contents(pathlib.Path(problem["statement_src"]))
            contents = self.replace_vars(contents, problem)
            contents = "".join(contents)
            
            # convert: markdown -> html
            md = markdown.Markdown()
            html = md.convert(contents)
            html = self.add_header_footer(html, problem)
            
            # save html
            output_path = output_dir / pathlib.Path(problem["id"] + ".html")
            self.save_html(html, output_path)
