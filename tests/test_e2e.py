import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import pytest


@pytest.fixture
def create_tempdir():
    """
    Create a temporary directory

    When the test is run, a temporary directory is created, and it is automatically
    deleted after the test is finished. This ensures that the test environment is
    always kept clean.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def compare_directories(
    dir_actual: Path,
    dir_expected: Path,
    extension: str,
    exclude_patterns: Optional[list[str]] = None,
) -> bool:
    """
    Compare the contents of two directories

    Args:
        dir_actual: Actual directory
        dir_expected: Expected directory
        extension: Extension of the files to compare
        exclude_patterns: List of patterns to exclude from comparison
    """
    exclude_patterns = exclude_patterns or []

    def should_exclude(path):
        return any(re.search(pattern, path.as_posix()) for pattern in exclude_patterns)

    files_in_actual_dir = [
        p
        for p in Path(dir_actual).glob("**/*")
        if p.is_file()
        and re.search(rf"\.({extension}|jpg|png)", p.as_posix())
        and not should_exclude(p)
    ]
    files_in_expected_dir = [
        p
        for p in Path(dir_expected).glob("**/*")
        if p.is_file()
        and re.search(rf"\.({extension}|jpg|png)", p.as_posix())
        and not should_exclude(p)
    ]

    rel_files_in_actual_dir = {p.relative_to(dir_actual) for p in files_in_actual_dir}
    rel_files_in_expected_dir = {
        p.relative_to(dir_expected) for p in files_in_expected_dir
    }
    assert len(rel_files_in_actual_dir) > 0, "Actual directory is empty"
    assert len(rel_files_in_expected_dir) > 0, "Expected directory is empty"
    if rel_files_in_actual_dir != rel_files_in_expected_dir:
        print(
            "\n".join(
                [
                    "File sets do not match: ",
                    "Exists in actual dir only: ",
                    f"{rel_files_in_actual_dir - rel_files_in_expected_dir}",
                    "Exists in expected dir only: ",
                    f"{rel_files_in_expected_dir - rel_files_in_actual_dir}",
                ]
            )
        )
        return False

    # PDF files comparison is not supported yet
    if extension != "pdf":
        for rel_path in rel_files_in_actual_dir:
            file_actual = Path(dir_actual) / rel_path
            file_expected = Path(dir_expected) / rel_path

            with open(file_actual, "rb") as f_actual, open(
                file_expected, "rb"
            ) as f_expected:
                if f_actual.read() != f_expected.read():
                    print(f"File contents do not match: {rel_path}")
                    return False

    return True


def execute_and_verify_match(create_tempdir: str, extension: str):
    """
    Run 'ss-manager run sample/' command and verify the result

    Notes:
        - If the expected output is changed, you need to update the
          tests/expected_output directory.
    """
    current_dir = os.getcwd()

    try:
        sample_dir = Path(current_dir) / "sample"
        temp_sample_dir = Path(create_tempdir) / "sample"
        shutil.copytree(sample_dir, temp_sample_dir)

        result = subprocess.run(
            [
                "python",
                "statements_manager/main.py",
                "run",
                "-o",
                extension,
                "-p",
                str(temp_sample_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Command execution failed: {result.stderr}"

        actual_output_dir = temp_sample_dir
        assert actual_output_dir.exists(), "Output directory was not generated"
        expected_output_dir = Path(current_dir) / "tests" / "expected_output"

        assert compare_directories(
            actual_output_dir,
            expected_output_dir,
            extension,
            exclude_patterns=[
                ".git",
                "__pycache__",
                ".DS_Store",
                "templates",  # template html files
                r".*_sample_.*\.md",  # explanation files of samples
                r"/statement/",  # statement files
            ],
        ), "Generated files do not match the expected output"

    finally:
        os.chdir(current_dir)


def test_e2e_html(create_tempdir: str):
    execute_and_verify_match(create_tempdir, "html")


def test_e2e_md(create_tempdir: str):
    execute_and_verify_match(create_tempdir, "md")


# TODO: test on Windows and macOS
def test_e2e_pdf(create_tempdir: str):
    if "GITHUB_ACTIONS" not in os.environ or os.environ.get("RUNNER_OS") == "Linux":
        execute_and_verify_match(create_tempdir, "pdf")
