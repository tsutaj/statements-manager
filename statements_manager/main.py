import argparse
import pathlib
import pickle
import shutil
from typing import Union
from logging import Logger, getLogger, basicConfig
from statements_manager.src.project_file import ProjectFile
from statements_manager.src.manager.docs_manager import DocsManager
from statements_manager.src.manager.local_manager import LocalManager
from statements_manager.src.config.default import default_toml
from statements_manager.src.utils import ask_ok, create_token

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

    subparser = subparsers.add_parser("run")
    subparser.add_argument(
        "project",
        help="Path to a directory which contains 'project.toml'",
    )

    subparser = subparsers.add_parser("reg-creds")
    subparser.add_argument(
        "project",
        help="Path to a directory which contains 'project.toml'",
    )
    subparser.add_argument(
        "creds",
        help="Path to credentials file (json)"
    )
    return parser


def subcommand_run(project_path: str) -> None:
    project_path = str(pathlib.Path(project_path, "project.toml").resolve())
    logger.debug(f"run: project_path = '{project_path}'")
    project = ProjectFile(project_path, default_toml)  # ProjectFile

    # check mode
    for project_id, config in project.problem_attr.items():
        mode = config["mode"].lower()  # type: str
        if mode == "docs":
            logger.info("running in 'docs' mode")
            manager = DocsManager(config)  # type: Union[DocsManager, LocalManager]
        elif mode == "local":
            logger.info("running in 'local' mode")
            manager = LocalManager(config)
        else:
            logger.error(f"unknown mode: {mode}")
            raise ValueError(f"unknown mode: {mode}")
        manager.run()
    logger.debug("run command ended successfully.")


def subcommand_reg_creds(project_path: str, creds_path: str) -> None:
    # 引数は実在するものでなければならない
    if not pathlib.Path(project_path).exists():
        logger.error(f"project {project_path} does not exist")
        raise IOError(f"project {project_path} does not exist")
    if not pathlib.Path(creds_path).exists():
        logger.error(f"credentials {creds_path} does not exist")
        raise IOError(f"credentials {creds_path} does not exist")

    # 隠しディレクトリ (すでにディレクトリがある場合は更新するか確認)
    hidden_dir = pathlib.Path(project_path, ".ss-manager")
    logger.info("register credentials")
    if not hidden_dir.exists():
        logger.info(f"create hidden directory: {hidden_dir}")
        hidden_dir.mkdir()
    elif not ask_ok(f"{hidden_dir} already exists. Rewrite this?", False):
        logger.info(f"do nothing (not rewrite)")
        return

    # ファイルを登録
    token_path = str(pathlib.Path(hidden_dir, "token.pickle"))
    token = create_token(creds_path=creds_path, token_path=token_path)
    with open(token_path, "wb") as f:
        pickle.dump(token, f)
    shutil.copy2(creds_path, hidden_dir / pathlib.Path("credentials.json"))
    logger.info("copied credentials successfully.")
    logger.debug("reg-creds command ended successfully.")


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()
    set_logger(args.debug)
    if args.subcommand == "run":
        subcommand_run(project_path=args.project)
    elif args.subcommand == "reg-creds":
        subcommand_reg_creds(project_path=args.project, creds_path=args.creds)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
