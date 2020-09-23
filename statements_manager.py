import argparse
import toml
import pathlib
import shutil
from logging import Logger, basicConfig, getLogger
from typing import Any, MutableMapping
from src.project_file import ProjectFile
from src.manager.docs_manager import DocsManager
from src.manager.local_manager import LocalManager

logger = getLogger(__name__)  # type: Logger


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    subparser = subparsers.add_parser("run")
    subparser = subparsers.add_parser("create")

    parser.add_argument(
        "-p",
        "--project",
        type=str,
        default="./config/default.toml",
        help="Path to project file",
    )
    return parser


def run(project_path: str, default_project_path: str) -> None:
    project = ProjectFile(
        project_path, default_project_path
    )  # ProjectFile

    # check mode
    mode = project.get_attr("mode").lower()  # type: str
    if mode == "docs":
        manager = DocsManager(project)
    elif mode == "local":
        manager = LocalManager(project)
    else:
        raise ValueError("unknown mode: {}".format(mode))

    # todo
    manager.run()

def create(project_path: str, default_project_path: str) -> None:
    if pathlib.Path(project_path).exists():
        raise FileExistsError("file exists:", project_path)
    logger.info("create new project:", project_path)
    shutil.copy(default_project_path, project_path)

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if args.subcommand == "run":
        run(
            project_path=args.project,
            default_project_path="./config/default.toml"
        )
    elif args.subcommand == "create":
        create(
            project_path=args.project,
            default_project_path="./config/default.toml"
        )
    else:
        parser.print_help()
