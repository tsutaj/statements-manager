from statements_manager.src.project import Project
from statements_manager.src.manager.base_manager import BaseManager
import pathlib


class LocalManager(BaseManager):
    def __init__(self, project: Project) -> None:
        super().__init__(project)

    def get_contents(self, statement_path: pathlib.Path) -> str:
        with open(statement_path) as f:
            return f.read()
