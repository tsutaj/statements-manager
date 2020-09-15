from src.manager.base_manager import BaseManager

class DocsManager(BaseManager):
    def __init__(self, project):
        super().__init__(project)

    def get_contents(self, task_name):
        with open(hoge) as fuga:
            pass
