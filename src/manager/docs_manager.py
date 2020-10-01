import pathlib
import pickle
from src.manager.base_manager import BaseManager
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class DocsManager(BaseManager):
    def __init__(self, project):
        super().__init__(project)
        self.creds = None
        self.SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

        # set credentials
        docs_setting = project.get_attr("docs")
        token_path = pathlib.Path(docs_setting.get("token_src", ""))
        creds_path = pathlib.Path(docs_setting.get("credentials_src", ""))
        if token_path.exists():
            with open(token_path, "rb") as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "wb") as token:
                pickle.dump(self.creds, token)

        # launch a service
        self.service = build("docs", "v1", credentials=self.creds)

    def get_contents(self, statement_src: pathlib.Path) -> str:
        document = self.service.documents().get(documentId=statement_src).execute()
        text = ""
        for content in document.get("body")["content"]:
            if "paragraph" not in content:
                continue
            for element in content["paragraph"]["elements"]:
                text += element["textRun"]["content"]
        return text
