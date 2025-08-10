"""Tests for authentication priority functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from statements_manager.src.auth.oauth_config import (
    AuthPriorityConfig,
    get_auth_priority,
    load_auth_priority_config,
    save_auth_priority_config,
    set_auth_priority,
)


class TestAuthPriorityConfig:
    """Test AuthPriorityConfig class."""

    def test_default_config(self):
        """Test default configuration."""
        config = AuthPriorityConfig()
        assert config.auth_priority == "login"

    def test_custom_config(self):
        """Test custom configuration."""
        config = AuthPriorityConfig(auth_priority="creds")
        assert config.auth_priority == "creds"


class TestAuthPriorityFunctions:
    """Test authentication priority functions."""

    def test_get_auth_priority_default(self):
        """Test getting default auth priority when no config file exists."""
        with patch(
            "statements_manager.src.auth.oauth_config.get_auth_config_path"
        ) as mock_path:
            mock_path.return_value = Path("/nonexistent/path")
            priority = get_auth_priority()
            assert priority == "login"

    def test_set_and_get_auth_priority(self):
        """Test setting and getting auth priority."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "auth_config.json"

            with patch(
                "statements_manager.src.auth.oauth_config.get_auth_config_path"
            ) as mock_path:
                mock_path.return_value = config_path

                # Test setting priority
                set_auth_priority("creds")
                assert config_path.exists()

                # Test getting priority
                priority = get_auth_priority()
                assert priority == "creds"

    def test_load_auth_priority_config_valid(self):
        """Test loading valid auth priority config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "auth_config.json"
            config_data = {"auth_priority": "creds"}

            with open(config_path, "w") as f:
                json.dump(config_data, f)

            with patch(
                "statements_manager.src.auth.oauth_config.get_auth_config_path"
            ) as mock_path:
                mock_path.return_value = config_path
                config = load_auth_priority_config()
                assert config.auth_priority == "creds"

    def test_load_auth_priority_config_invalid(self):
        """Test loading invalid auth priority config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "auth_config.json"
            config_data = {"auth_priority": "invalid"}

            with open(config_path, "w") as f:
                json.dump(config_data, f)

            with patch(
                "statements_manager.src.auth.oauth_config.get_auth_config_path"
            ) as mock_path:
                mock_path.return_value = config_path
                config = load_auth_priority_config()
                assert config.auth_priority == "login"  # Should default to login

    def test_load_auth_priority_config_corrupted(self):
        """Test loading corrupted auth priority config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "auth_config.json"

            with open(config_path, "w") as f:
                f.write("invalid json")

            with patch(
                "statements_manager.src.auth.oauth_config.get_auth_config_path"
            ) as mock_path:
                mock_path.return_value = config_path
                config = load_auth_priority_config()
                assert config.auth_priority == "login"  # Should default to login

    def test_save_auth_priority_config(self):
        """Test saving auth priority config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "auth_config.json"

            with patch(
                "statements_manager.src.auth.oauth_config.get_auth_config_path"
            ) as mock_path:
                mock_path.return_value = config_path

                config = AuthPriorityConfig(auth_priority="creds")
                save_auth_priority_config(config)

                assert config_path.exists()
                with open(config_path, "r") as f:
                    data = json.load(f)
                    assert data["auth_priority"] == "creds"
