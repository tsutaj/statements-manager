import pickle
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoginStatus:
    token_path: Path
    is_logged_in: bool = False
    token_exists: bool = False
    token_valid: bool = False
    token_expired: bool = True
    has_refresh_token: bool = False

    def to_strings(self) -> list[str]:
        lines = []
        lines.append(
            " ".join(
                [
                    (
                        "✓  Token exists"
                        if self.token_exists
                        else "✗  Token does not exist"
                    ),
                    f"({self.token_path})",
                ]
            )
        )
        lines.append("✓  Logged in" if self.is_logged_in else "✗  Not logged in")
        lines.append("✓  Token is valid" if self.token_valid else "✗  Token is invalid")
        lines.append(
            "✓  Token is available (not expired)"
            if not self.token_expired
            else "✗  Token is not available (or expired)"
        )
        lines.append(
            "✓  Has refresh token" if self.has_refresh_token else "✗  No refresh token"
        )
        return lines


def get_login_status(token_path: Path) -> LoginStatus:
    status = LoginStatus(token_path=token_path)
    try:
        with open(token_path, "rb") as token_file:
            token_obj = pickle.load(token_file)
            if not token_obj:
                return status

            status.token_exists = True
            if token_obj.valid:
                status.token_valid = True
                status.is_logged_in = True
            if not token_obj.expired and token_obj.valid:
                status.token_expired = False
            if token_obj.refresh_token is not None:
                status.has_refresh_token = True
            return status
    except Exception:
        return status
