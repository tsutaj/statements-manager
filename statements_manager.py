import argparse
import pathlib
import shutil
from typing import Union
from logging import Logger, getLogger, basicConfig
from src.project_file import ProjectFile
from src.manager.docs_manager import DocsManager
from src.manager.local_manager import LocalManager

logger = getLogger(__name__)  # type: Logger


def set_logger(debug_mode: bool) -> None:
    logger_level = "DEBUG" if debug_mode else "INFO"

    try:
        import colorlog
    except ImportError:
        basicConfig(
            format="[%(asctime)s %(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            level=logger_level,
        )
        logger.warn("Please install colorlog: pip3 install colorlog")
    else:
        handler = colorlog.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s %(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        handler.setFormatter(formatter)
        basicConfig(level=logger_level, handlers=[handler])


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    subparsers = parser.add_subparsers(dest="subcommand")

    parser_run = subparsers.add_parser("run")
    parser_run.add_argument(
        "-p",
        "--project",
        type=str,
        default="./config/default.toml",
        help="Path to project file",
    )

    parser_create = subparsers.add_parser("create")
    parser_create.add_argument(
        "-p",
        "--project",
        type=str,
        default="./config/default.toml",
        help="Path to project file",
    )
    return parser


def run(project_path: str, default_project_path: str) -> None:
    logger.debug(
        "run: project_path = '{}', default_project_path = '{}'".format(
            project_path, default_project_path
        )
    )
    project = ProjectFile(project_path, default_project_path)  # ProjectFile

    # check mode
    mode = project.get_attr("mode").lower()  # type: str
    if mode == "docs":
        logger.info("running in 'docs' mode")
        manager = DocsManager(project)  # type: Union[DocsManager, LocalManager]
    elif mode == "local":
        logger.info("running in 'local' mode")
        manager = LocalManager(project)
    else:
        logger.error("unknown mode: {}".format(mode))
        raise ValueError("unknown mode: {}".format(mode))

    # todo
    manager.run()


def create(project_path: str, default_project_path: str) -> None:
    if pathlib.Path(project_path).exists():
        logger.error("file exists: {}".format(project_path))
        raise FileExistsError("file exists:", project_path)
    logger.info("create new project: {}".format(project_path))
    shutil.copy(default_project_path, project_path)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    set_logger(args.debug)
    if args.subcommand == "run":
        run(project_path=args.project, default_project_path="./config/default.toml")
    elif args.subcommand == "create":
        create(project_path=args.project, default_project_path="./config/default.toml")
    else:
        parser.print_help()
