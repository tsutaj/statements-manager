import json
import os
from typing import Any

from google.oauth2 import service_account


def get_token_for_ci() -> Any:
    service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_INFO"])
    return service_account.Credentials.from_service_account_info(service_account_info)
