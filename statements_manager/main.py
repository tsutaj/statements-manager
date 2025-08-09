from __future__ import annotations

import argparse
import pathlib
import pickle
import shutil
from logging import Logger, basicConfig, getLogger

from statements_manager.src.auth.oauth_config import (
    get_credentials_path,
    get_token_path,
)
from statements_manager.src.auth.oauth_login import (
    is_logged_in,
    logout,
    perform_oauth_login,
)
from statements_manager.src.auth.oauth_login_lecagy import get_oauth_token_legacy
from statements_manager.src.output_file_kind import OutputFileKind
from statements_manager.src.project import Project
from statements_manager.src.utils import ask_ok

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
    subparser.add_argument(
        "-k",
        "--keep-going",
        action="store_true",
        help="continue processing when statement retrieval fails (default: fail immediately)",
    )
    subparser.add_argument(
        "--fail-on-suggestions",
        action="store_true",
        help="treat unresolved Google Docs suggestions as failure",
    )

    subparser = subparsers.add_parser(
        "auth",
        help="authentication management",
    )
    auth_subparsers = subparser.add_subparsers(
        dest="auth_action", help="authentication actions", required=True
    )
    auth_login_parser = auth_subparsers.add_parser(
        "login", help="authenticate with Google account"
    )
    auth_login_parser.add_argument(
        "--force",
        action="store_true",
        help="force re-authentication even if already logged in",
    )
    auth_subparsers.add_parser("logout", help="logout and remove stored credentials")
    auth_subparsers.add_parser("status", help="check current login status")

    subparser = subparsers.add_parser(
        "reg-creds",
        help="register credentials file (legacy - use 'auth login' instead)",
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
    keep_going: bool,
    fail_on_suggestions: bool,
) -> None:
    working_dir = str(pathlib.Path(working_dir).resolve())
    logger.debug(f"run: working_dir = '{working_dir}'")
    project = Project(working_dir, output, make_problemset)

    project.run_problems(
        make_problemset, force_dump, constraints_only, keep_going, fail_on_suggestions
    )
    logger.debug("run command ended successfully.")


def subcommand_auth(
    auth_action: str,
    force: bool = False,
) -> None:
    """Handle OAuth2 authentication actions."""
    if auth_action == "login":
        # Perform login
        if not force and is_logged_in():
            logger.info("✓ You are already logged in. Use --force to re-authenticate.")
            return

        success = perform_oauth_login(force_reauth=force)
        if not success:
            logger.error("Login failed. Please try again.")
            exit(1)

        logger.info("✓ Login successful! You can now use the application.")
    elif auth_action == "logout":
        success = logout()
        if not success:
            exit(1)
        return
    elif auth_action == "status":
        if is_logged_in():
            logger.info("✓ You are currently logged in.")
        else:
            logger.info(
                "✗ You are not logged in. Run 'ss-manager auth login' to authenticate."
            )
        return
    else:
        logger.error(f"Unknown auth action: {auth_action}")
        exit(1)


def subcommand_reg_creds(
    creds_path: str | None,
) -> None:
    logger.warning(
        "reg-creds is deprecated. Please use 'ss-manager auth login' instead."
    )
    creds_savepath = get_credentials_path()
    token_path = get_token_path()
    hidden_dir = creds_savepath.parent
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
    if not creds_savepath.exists() or not creds_savepath.samefile(creds_path):
        shutil.copy2(creds_path, creds_savepath)
        logger.info("copied credentials successfully.")
    else:
        logger.info("registered credentials successfully.")
    token = get_oauth_token_legacy()
    with open(token_path, "wb") as f:
        pickle.dump(token, f)
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
            keep_going=args.keep_going,
            fail_on_suggestions=args.fail_on_suggestions,
        )
    elif args.subcommand == "auth":
        subcommand_auth(
            auth_action=args.auth_action,
            force=getattr(args, "force", False),
        )
    elif args.subcommand == "reg-creds":
        subcommand_reg_creds(
            creds_path=args.creds_path,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
