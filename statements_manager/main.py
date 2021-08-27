import argparse
import pathlib
import pickle
import shutil
from logging import Logger, basicConfig, getLogger

from statements_manager.src.project import Project
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

    subparser = subparsers.add_parser(
        "run",
        help="generate statement file(s)",
    )
    subparser.add_argument(
        "working_dir",
        help="path to a working directory",
    )
    subparser.add_argument(
        "-o",
        "--output",
        default="html",
        choices=["html", "md", "pdf"],
        help="output format (defaults to 'html')",
    )

    subparser = subparsers.add_parser("reg-creds", help="register credentials file")
    subparser.add_argument(
        "working_dir",
        help="path to a working directory",
    )
    subparser.add_argument("creds", help="path to credentials file (json)")
    return parser


def subcommand_run(working_dir: str, output: str) -> None:
    working_dir = str(pathlib.Path(working_dir).resolve())
    logger.debug(f"run: working_dir = '{working_dir}'")
    project = Project(working_dir, output)  # Project

    project.run_problems()
    logger.debug("run for problem set")
    project.run_problemset()
    logger.debug("run command ended successfully.")


def subcommand_reg_creds(working_dir: str, creds_path: str) -> None:
    # 引数は実在するものでなければならない
    if not pathlib.Path(working_dir).exists():
        logger.error(f"working directory '{working_dir}' does not exist")
        raise IOError(f"working directory '{working_dir}' does not exist")
    if not pathlib.Path(creds_path).exists():
        logger.error(f"credentials {creds_path} does not exist")
        raise IOError(f"credentials {creds_path} does not exist")

    # 隠しディレクトリ (すでにディレクトリがある場合は更新するか確認)
    hidden_dir = pathlib.Path(working_dir, ".ss-manager")
    logger.info("register credentials")
    if not hidden_dir.exists():
        logger.info(f"create hidden directory: {hidden_dir}")
        hidden_dir.mkdir()
    elif not ask_ok(f"{hidden_dir} already exists. Rewrite this?", False):
        logger.info("do nothing (not rewrite)")
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
        subcommand_run(working_dir=args.working_dir, output=args.output)
    elif args.subcommand == "reg-creds":
        subcommand_reg_creds(working_dir=args.working_dir, creds_path=args.creds)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
