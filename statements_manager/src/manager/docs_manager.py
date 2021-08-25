import pathlib
from logging import Logger, getLogger

from googleapiclient.discovery import build

from statements_manager.src.manager.base_manager import BaseManager
from statements_manager.src.utils import create_token

logger = getLogger(__name__)  # type: Logger


class DocsManager(BaseManager):
    def __init__(self, problem_attr):
        super().__init__(problem_attr)

        # token / credentials 用のディレクトリが存在するか
        setting_dir = pathlib.Path(pathlib.Path(problem_attr["creds_path"]).parent)
        if not setting_dir.exists():
            logger.error(f"setting dir '{setting_dir}' does not exist")
            logger.warning(
                "tips: try 'ss-manager reg-creds' before running on docs mode."
            )
            self.state = False
            return

        self.token = create_token(
            creds_path=problem_attr["creds_path"],
            token_path=problem_attr["token_path"],
        )

        # launch a service
        self.service = build("docs", "v1", credentials=self.token)

    def get_contents(self, statement_path: pathlib.Path) -> str:
        document = self.service.documents().get(documentId=statement_path).execute()
        text = ""
        for content in document.get("body")["content"]:
            if "paragraph" not in content:
                continue
            for element in content["paragraph"]["elements"]:
                text += element["textRun"]["content"]
        return text
