import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from statements_manager.src.convert_task_runner import ContentsStatus, ConvertTaskRunner


def test_fail_on_suggestions_option_with_sample_h():
    """
    Test that --fail-on-suggestions option causes non-zero exit code
    when running with sample/H (which uses Google Docs)
    """
    current_dir = os.getcwd()

    # Run ss-manager with --fail-on-suggestions on sample/H
    result = subprocess.run(
        [
            "python3",
            "statements_manager/main.py",
            "run",
            "--fail-on-suggestions",
            "sample/H",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=current_dir,
    )

    # Should fail with non-zero exit code
    assert result.returncode != 0, (
        "Expected non-zero exit code when using --fail-on-suggestions with Google Docs "
        "that requires authentication or has unresolved suggestions"
    )


def test_get_docs_contents_with_suggestions_fail_enabled():
    """
    Test get_docs_contents method with fail_on_suggestions=True
    """
    # Create a mock problemset config
    mock_problemset_config = MagicMock()
    mock_problem = MagicMock()
    mock_problem.statement.path = "test_doc_id"
    mock_problemset_config.get_problem.return_value = mock_problem

    # Create ConvertTaskRunner instance
    runner = ConvertTaskRunner(mock_problemset_config)

    # Mock the Google Docs API calls
    with (
        patch(
            "statements_manager.src.convert_task_runner.get_oauth_token"
        ) as mock_get_oauth_token,
        patch("statements_manager.src.convert_task_runner.build") as mock_build,
        patch("pathlib.Path.home") as mock_home,
    ):
        # Setup mocks
        mock_get_oauth_token.return_value = MagicMock()
        mock_home.return_value = Path("/fake/home")

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create a mock document with unresolved suggestions
        mock_document = {
            "body": {
                "content": [
                    {
                        "paragraph": {
                            "elements": [
                                {
                                    "textRun": {
                                        "content": "Normal text.\n",
                                    }
                                },
                                {
                                    "textRun": {
                                        "content": "Text with suggestion.\n",
                                        "suggestedInsertionIds": ["suggestion1"],
                                    }
                                },
                            ]
                        }
                    }
                ]
            }
        }

        mock_service.documents.return_value.get.return_value.execute.return_value = (
            mock_document
        )

        # Test with fail_on_suggestions=True - should return NG status
        status, content = runner.get_docs_contents(
            "test_problem", fail_on_suggestions=True
        )
        assert (
            status == ContentsStatus.NG
        ), "Expected NG status when suggestions exist and fail_on_suggestions=True"

        # Test with fail_on_suggestions=False - should return OK status
        status, content = runner.get_docs_contents(
            "test_problem", fail_on_suggestions=False
        )
        assert (
            status == ContentsStatus.OK
        ), "Expected OK status when fail_on_suggestions=False"
        assert "Normal text.\n" in content, "Expected normal text to be included"
        assert (
            "Text with suggestion.\n" not in content
        ), "Expected suggested text to be excluded"


def test_get_docs_contents_without_suggestions():
    """
    Test get_docs_contents method with no suggestions in document
    """
    # Create a mock problemset config
    mock_problemset_config = MagicMock()
    mock_problem = MagicMock()
    mock_problem.statement.path = "test_doc_id"
    mock_problemset_config.get_problem.return_value = mock_problem

    # Create ConvertTaskRunner instance
    runner = ConvertTaskRunner(mock_problemset_config)

    # Mock the Google Docs API calls
    with (
        patch(
            "statements_manager.src.convert_task_runner.get_oauth_token"
        ) as mock_get_oauth_token,
        patch("statements_manager.src.convert_task_runner.build") as mock_build,
        patch("pathlib.Path.home") as mock_home,
    ):
        # Setup mocks
        mock_get_oauth_token.return_value = MagicMock()
        mock_home.return_value = Path("/fake/home")

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create a mock document with NO suggestions
        mock_document = {
            "body": {
                "content": [
                    {
                        "paragraph": {
                            "elements": [
                                {
                                    "textRun": {
                                        "content": "Normal text without suggestions.\n",
                                    }
                                },
                            ]
                        }
                    }
                ]
            }
        }

        mock_service.documents.return_value.get.return_value.execute.return_value = (
            mock_document
        )

        # Test with fail_on_suggestions=True - should return OK status since no suggestions
        status, content = runner.get_docs_contents(
            "test_problem", fail_on_suggestions=True
        )
        assert (
            status == ContentsStatus.OK
        ), "Expected OK status when no suggestions exist"
        assert (
            "Normal text without suggestions.\n" in content
        ), "Expected normal text to be included"


def test_fail_on_suggestions_option_help():
    """
    Test that --fail-on-suggestions option appears in help
    """
    current_dir = os.getcwd()

    result = subprocess.run(
        [
            "python3",
            "statements_manager/main.py",
            "run",
            "--help",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=current_dir,
    )

    assert result.returncode == 0, "Help command should succeed"
    assert (
        "--fail-on-suggestions" in result.stdout
    ), "Expected --fail-on-suggestions option to appear in help"
    assert (
        "treat unresolved Google Docs suggestions as failure" in result.stdout
    ), "Expected help text for --fail-on-suggestions option"
