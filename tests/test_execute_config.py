import pathlib

import pytest

from statements_manager.src.execute_config import StatementConfig


class TestStatementConfig:
    def test_exponential_threshold_valid(self):
        """Test that valid exponential_threshold values are accepted"""
        config = {"path": "test.md", "exponential_threshold": 1000000}
        statement_config = StatementConfig(pathlib.Path("test.toml"), config)
        assert statement_config.exponential_threshold == 1000000

    def test_exponential_threshold_minimum_valid(self):
        """Test that exponential_threshold = 1 is accepted"""
        config = {"path": "test.md", "exponential_threshold": 1}
        statement_config = StatementConfig(pathlib.Path("test.toml"), config)
        assert statement_config.exponential_threshold == 1

    def test_exponential_threshold_zero_invalid(self):
        """Test that exponential_threshold = 0 raises ValueError"""
        config = {"path": "test.md", "exponential_threshold": 0}
        with pytest.raises(ValueError, match="exponential_threshold must be >= 1"):
            StatementConfig(pathlib.Path("test.toml"), config)

    def test_exponential_threshold_negative_invalid(self):
        """Test that negative exponential_threshold raises ValueError"""
        config = {"path": "test.md", "exponential_threshold": -1}
        with pytest.raises(ValueError, match="exponential_threshold must be >= 1"):
            StatementConfig(pathlib.Path("test.toml"), config)
