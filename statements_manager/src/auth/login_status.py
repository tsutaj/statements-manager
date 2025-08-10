import pickle
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoginStatus:
    token_path: Path
    is_logged_in: bool
    token_exists: bool
    token_valid: bool
    token_expired: bool
    has_refresh_token: bool

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
            else "✗  Token is expired"
        )
        lines.append(
            "✓  Has refresh token" if self.has_refresh_token else "✗  No refresh token"
        )
        return lines


def get_login_status(token_path: Path) -> LoginStatus:
    status = LoginStatus(
        token_path=token_path,
        token_exists=False,
        is_logged_in=False,
        token_valid=False,
        token_expired=False,
        has_refresh_token=False,
    )
    try:
        with open(token_path, "rb") as token_file:
            token_obj = pickle.load(token_file)
            if not token_obj:
                return status

            status.token_exists = True
            if token_obj.valid:
                status.token_valid = True
                status.is_logged_in = True
            if token_obj.expired:
                status.token_expired = True
            if token_obj.refresh_token is not None:
                status.has_refresh_token = True
            return status
    except Exception:
        return status
