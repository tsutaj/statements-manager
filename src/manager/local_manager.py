from src.project_file import ProjectFile
from src.manager.base_manager import BaseManager
import pathlib


class LocalManager(BaseManager):
    def __init__(self, project: ProjectFile) -> None:
        super().__init__(project)

    def get_contents(self, statement_src: pathlib.Path) -> str:
        with open(statement_src) as f:
            return f.read()
