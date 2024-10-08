from __future__ import annotations

import argparse
import pathlib
import pickle
import shutil
from logging import Logger, basicConfig, getLogger

from statements_manager.src.output_file_kind import OutputFileKind
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
        default=OutputFileKind.HTML.value,
        choices=OutputFileKind.values(),
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
    subparser.add_argument(
        "-c",
        "--constraints-only",
        action="store_true",
        help="update constraints file only",
    )

    subparser = subparsers.add_parser(
        "reg-creds",
        help="register credentials file",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparser.add_argument(
        "creds_path",
        nargs="?",
        help="path to credentials file (json). "
        "if creds_path is not specified, update existing credentials.\n"
        "how to create credentials file: "
        "see https://statements-manager.readthedocs.io/ja/stable/register_credentials.html",
    )
    return parser


def subcommand_run(
    working_dir: str,
    output: str,
    make_problemset: bool,
    force_dump: bool,
    constraints_only: bool,
) -> None:
    working_dir = str(pathlib.Path(working_dir).resolve())
    logger.debug(f"run: working_dir = '{working_dir}'")
    project = Project(working_dir, output, make_problemset)

    project.run_problems(make_problemset, force_dump, constraints_only)
    logger.debug("run command ended successfully.")


def subcommand_reg_creds(
    creds_path: str | None,
) -> None:
    homedir = str(pathlib.Path.home())
    hidden_dir = pathlib.Path(homedir, ".ss-manager")
    creds_savepath = hidden_dir / "credentials.json"
    token_path = hidden_dir / "token.pickle"
    if creds_path is not None:
        if not hidden_dir.exists():
            logger.info(f"create hidden directory: {hidden_dir}")
            hidden_dir.mkdir()

        # 上書きが発生する場合は確認する
        if token_path.exists() and not ask_ok(
            f"{hidden_dir} already exists. Rewrite this?", default_response=False
        ):
            return
    else:
        creds_path = str(creds_savepath.resolve())

    logger.info("register credentials")
    if not pathlib.Path(creds_path).exists():
        logger.error(f"credentials '{creds_path}' does not exist")
        raise IOError(f"credentials '{creds_path}' does not exist")

    # ファイルを登録
    token = create_token(creds_path)
    with open(token_path, "wb") as f:
        pickle.dump(token, f)
    if not creds_savepath.exists() or not creds_savepath.samefile(creds_path):
        shutil.copy2(creds_path, creds_savepath)
        logger.info("copied credentials successfully.")
    else:
        logger.info("registered credentials successfully.")
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
            constraints_only=args.constraints_only,
        )
    elif args.subcommand == "reg-creds":
        subcommand_reg_creds(
            creds_path=args.creds_path,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
