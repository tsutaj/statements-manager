from __future__ import annotations

import argparse
import pathlib
from collections import Counter
from logging import Logger, getLogger

import toml
from googleapiclient.discovery import build

from statements_manager.src.auth.login_status import get_login_status
from statements_manager.src.auth.oauth_login import get_oauth_token, login_config

logger: Logger = getLogger(__name__)


def get_problem_id(specified_id: str | None, default_id: str) -> str:
    if specified_id is None:
        return default_id
    else:
        return specified_id


def get_initial_content(template_path: str | None) -> str:
    if template_path is None:
        return ""
    template_file = pathlib.Path(template_path)
    if template_file.exists():
        with open(template_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        logger.error(f"Template file {template_path} not found")
        raise FileNotFoundError(f"Template file {template_path} not found")


def create_google_docs(
    problem_id: str,
    initial_content: str,
    lang: str,
    language_count: int,
    language_frequency: Counter,
) -> str:
    title = problem_id
    if language_frequency[lang] > 1:
        title += f"{language_count}"
    if len(language_frequency.keys()) > 1:
        title += f"_{lang}"
    try:
        token = get_oauth_token()
        if token is None:
            raise RuntimeError("Failed to get OAuth token")

        service = build("docs", "v1", credentials=token, cache_discovery=False)
        created_document = service.documents().create(body={"title": title}).execute()
        docs_id = created_document["documentId"]
        if initial_content:
            service.documents().batchUpdate(
                documentId=docs_id,
                body={
                    "requests": [
                        {
                            "insertText": {
                                "location": {"index": 1},
                                "text": initial_content,
                            }
                        }
                    ]
                },
            ).execute()

        logger.info(
            f"Created {title} (located in 'my-drive'): "
            f"https://docs.google.com/document/d/{docs_id}/edit\n"
        )
        return docs_id
    except Exception as e:
        logger.error(f"Failed to create Google Docs: {e}")
        raise e


def create_local_statement(
    initial_content: str,
    dir_path: pathlib.Path,
    lang: str,
    language_count: int,
    language_frequency: Counter,
) -> str:
    if language_frequency[lang] == 1:
        statement_path = dir_path / f"statement/{lang}/statement.md"
    else:
        statement_path = dir_path / f"statement/{lang}/statement_{language_count}.md"
    statement_path.parent.mkdir(parents=True, exist_ok=True)
    with open(statement_path, "w", encoding="utf-8") as f:
        f.write(initial_content)
    logger.info(f"Created local statement file: {statement_path}")
    return str(statement_path.relative_to(dir_path).as_posix())


def setup_problem(args: argparse.Namespace) -> None:
    """Setup a new problem directory with problem.toml."""

    dir_path = pathlib.Path(args.working_dir).resolve()
    problem_toml_path = dir_path / "problem.toml"
    if problem_toml_path.exists():
        logger.error(f"problem.toml already exists in {dir_path}")
        raise FileExistsError(f"problem.toml already exists in {dir_path}")

    use_google_docs = args.mode == "docs"
    is_logged_in = get_login_status(login_config.token_path).is_logged_in
    if use_google_docs and not is_logged_in:
        logger.error(
            "If you want to create Google Docs, authentication required. "
            "Please run 'ss-manager auth login' first."
        )
        logger.error(
            "You can also see your authentication status with 'ss-manager auth status'."
        )
        raise RuntimeError("Authentication required")

    if not dir_path.exists():
        logger.info(f"Creating directory: {dir_path}")
        dir_path.mkdir(parents=True, exist_ok=True)

    tests_dir_path = dir_path / "tests"
    tests_dir_path.mkdir(exist_ok=True)

    problem_id = get_problem_id(args.id, dir_path.name)
    initial_content = get_initial_content(args.template)
    statements = []

    language_frequency = Counter(args.language)
    language_count = {lang: 0 for lang in args.language}
    for lang in args.language:
        language_count[lang] += 1
        if use_google_docs:
            logger.info(f"Creating Google Docs ({lang}) ...")
            statement_path = create_google_docs(
                problem_id,
                initial_content,
                lang,
                language_count[lang],
                language_frequency,
            )
        else:
            statement_path = create_local_statement(
                initial_content,
                dir_path,
                lang,
                language_count[lang],
                language_frequency,
            )

        statements.append(
            {
                "path": statement_path,
                "lang": lang,
                "markdown_extensions": ["md_in_html", "tables", "fenced_code"],
            }
        )

    problem_config = {
        "id": problem_id,
        "params_path": "./tests/constraints.hpp",
        "statements": statements,
        "constraints": {},
    }
    with open(problem_toml_path, "w", encoding="utf-8") as f:
        toml.dump(problem_config, f)
    logger.info(f"Created problem.toml: {problem_toml_path}")
    logger.info("Setup completed successfully!")
