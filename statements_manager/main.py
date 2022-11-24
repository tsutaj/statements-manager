import argparse
import pathlib
import pickle
import shutil
from logging import Logger, basicConfig, getLogger

from statements_manager.src.project import Project
from statements_manager.src.utils import ask_ok, create_token

logger: Logger = getLogger(__name__)


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
        nargs="?",
        default=".",
        help="path to a working directory (default: current directory)",
    )
    subparser.add_argument(
        "-o",
        "--output",
        default="html",
        choices=["html", "md", "pdf"],
        help="output format (defaults to 'html')",
    )
    subparser.add_argument(
        "-p",
        "--make-problemset",
        action="store_true",
        help="make problemset file",
    )
    subparser.add_argument(
        "-f",
        "--force-dump",
        action="store_true",
        help="always dump output file",
    )

    subparser = subparsers.add_parser(
        "reg-creds",
        help="register credentials file",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparser.add_argument(
        "creds_path",
        help="path to credentials file (json)\n"
        "how to create credentials file: "
        "see https://github.com/tsutaj/statements-manager/blob/master/README.md#how-to-use",
    )
    return parser


def subcommand_run(
    working_dir: str,
    output: str,
    make_problemset: bool,
    force_dump: bool,
) -> None:
    working_dir = str(pathlib.Path(working_dir).resolve())
    logger.debug(f"run: working_dir = '{working_dir}'")
    project = Project(working_dir, output)  # Project

    project.run_problems(make_problemset, force_dump)
    logger.debug("run command ended successfully.")


def subcommand_reg_creds(
    creds_path: str,
) -> None:
    # 引数は実在するものでなければならない
    if not pathlib.Path(creds_path).exists():
        logger.error(f"credentials '{creds_path}' does not exist")
        raise IOError(f"credentials '{creds_path}' does not exist")

    # 隠しディレクトリ
    homedir = str(pathlib.Path.home())
    hidden_dir = pathlib.Path(homedir, ".ss-manager")
    logger.info("register credentials")
    if not hidden_dir.exists():
        logger.info(f"create hidden directory: {hidden_dir}")
        hidden_dir.mkdir()

    # 上書きが発生する場合は確認する
    token_path = hidden_dir / "token.pickle"
    if token_path.exists() and not ask_ok(
        f"{hidden_dir} already exists. Rewrite this?", default_response=False
    ):
        return

    # ファイルを登録
    token = create_token(creds_path)
    with open(token_path, "wb") as f:
        pickle.dump(token, f)
    creds_savepath = hidden_dir / "credentials.json"
    shutil.copy2(creds_path, creds_savepath)
    logger.info("copied credentials successfully.")
    logger.debug("reg-creds command ended successfully.")


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()
    set_logger(args.debug)
    if args.subcommand == "run":
        subcommand_run(
            working_dir=args.working_dir,
            output=args.output,
            make_problemset=args.make_problemset,
            force_dump=args.force_dump,
        )
    elif args.subcommand == "reg-creds":
        subcommand_reg_creds(
            creds_path=args.creds_path,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
