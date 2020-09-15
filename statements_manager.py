import argparse
import toml
import pathlib
import shutil
from logging import Logger, basicConfig, getLogger
from typing import Any, MutableMapping
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


class ProjectFile:
    def __init__(self, project_path: str, default_project_path: str) -> None:
        self._project = toml.load(project_path)  # type: MutableMapping[str, Any]
        self._default = toml.load(
            default_project_path
        )  # type: MutableMapping[str, Any]

    def get_attr(self, attr: str, raise_error: bool = False) -> Any:
        if attr not in self._project:
            if raise_error:
                raise KeyError("a key is not in project:", attr)
            elif attr in self._default:
                logger.warning(
                    "'{}' key is not in project. use default value.".format(attr)
                )
                return self._default[attr]
            else:
                raise KeyError("unknown key:", attr)
        else:
            return self._project[attr]


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
