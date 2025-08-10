"""OAuth2 configuration for Google Docs API access."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

# OAuth Secret value used to initiate OAuth2Client class.
# Note: It's ok to save this in git because this is an installed application
# as described here: https://developers.google.com/identity/protocols/oauth2#installed
# "The process results in a client ID and, in some cases, a client secret,
# which you embed in the source code of your application. (In this context,
# the client secret is obviously not treated as a secret.)"
OAUTH2_CLIENT_CONFIG = {
    "installed": {
        "client_id": "363852694560-mf0pr4e03cgskad3kci344oiq82bh1ht.apps.googleusercontent.com",
        "client_secret": "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",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["http://localhost"],
    }
}


@dataclass
class InstalledAppFlowConfig:
    scopes: list[str]
    token_path: Path
    port_number: int


def get_token_path(filename: str) -> Path:
    homedir = Path.home()
    hidden_dir = homedir / ".ss-manager"
    token_path = hidden_dir / filename
    return token_path


def get_credentials_path() -> Path:
    homedir = Path.home()
    hidden_dir = homedir / ".ss-manager"
    credential_path = hidden_dir / "credentials.json"
    return credential_path


def create_temp_credentials_file() -> str:
    """
    Create a temporary credentials file from the embedded configuration.
    Returns the path to the temporary file.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(OAUTH2_CLIENT_CONFIG, f, indent=2)
        return f.name


def cleanup_temp_file(file_path: str) -> None:
    """Clean up a temporary file."""
    try:
        Path(file_path).unlink()
    except FileNotFoundError:
        pass
