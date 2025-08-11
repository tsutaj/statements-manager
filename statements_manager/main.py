from __future__ import annotations

import argparse
import pathlib
import pickle
import shutil
from logging import Logger, basicConfig, getLogger

from statements_manager.src.auth.login_status import get_login_status
from statements_manager.src.auth.oauth_config import (
    get_auth_priority,
    get_credentials_path,
    set_auth_priority,
)
from statements_manager.src.auth.oauth_login import (
    login_config,
    logout,
    perform_oauth_login,
)
from statements_manager.src.auth.oauth_login_reg_creds import (
    get_oauth_token_reg_creds,
    reg_creds_config,
)
from statements_manager.src.output_file_kind import OutputFileKind
from statements_manager.src.project import Project
from statements_manager.src.setup_problem import setup_problem
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
        "setup",
        help="setup a new problem directory with problem.toml",
    )
    subparser.add_argument(
        "working_dir",
        help="directory name for the new problem",
    )
    subparser.add_argument(
        "-i",
        "--id",
        help="problem ID (default: directory name)",
    )
    subparser.add_argument(
        "-m",
        "--mode",
        choices=["local", "docs"],
        default="local",
        help="statement location (default: 'local')",
    )
    subparser.add_argument(
        "-l",
        "--language",
        choices=["ja", "en"],
        nargs="+",
        default=["en"],
        help="statement language (default: 'en')",
    )
    subparser.add_argument(
        "-t",
        "--template",
        help="path to template file (initial content)",
    )

    subparser = subparsers.add_parser(
        "auth",
        help="authentication management",
    )
    auth_subparsers = subparser.add_subparsers(
        dest="auth_action", help="authentication actions", required=True
    )
    auth_login_parser = auth_subparsers.add_parser(
        "login",
        help="authenticate with Google account. "
        "By doing so, ss-manager will be able to read and write only Google Docs "
        "created by ss-manager itself.",
    )
    auth_login_parser.add_argument(
        "--force",
        action="store_true",
        help="force re-authentication even if already logged in",
    )
    auth_subparsers.add_parser("logout", help="logout and remove stored credentials")
    auth_subparsers.add_parser("status", help="check current login status")

    auth_use_parser = auth_subparsers.add_parser(
        "use",
        help="set authentication method priority",
    )
    auth_use_parser.add_argument(
        "priority",
        choices=["login", "creds"],
        help="authentication method to prioritize "
        "('login' for OAuth2 login, 'creds' for registered credentials)",
    )

    subparser = subparsers.add_parser(
        "reg-creds",
        help="register credentials file manually. "
        "By doing so, ss-manager will be able to read and write all Google Docs.",
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
    args: argparse.Namespace,
) -> None:
    """Handle OAuth2 authentication actions."""
    if args.auth_action == "login":
        if not args.force and get_login_status(login_config.token_path).is_logged_in:
            logger.info("✅ You are already logged in. Use --force to re-authenticate.")
            return

        success = perform_oauth_login(force_reauth=args.force)
        if not success:
            logger.error("Login failed. Please try again.")
            exit(1)

        logger.info("✅ Login successful! You can now use the application.")
    elif args.auth_action == "logout":
        success = logout()
        if not success:
            exit(1)
        return
    elif args.auth_action == "use":
        set_auth_priority(args.priority)
        logger.info(f"✅ Authentication priority set to '{args.priority}'")
        logger.info("  - 'login': OAuth2 login system (ss-manager auth login)")
        logger.info("  - 'creds': Registered credentials (ss-manager reg-creds)")
        return
    elif args.auth_action == "status":
        current_priority = get_auth_priority()
        logger.info(f"Current priority: {current_priority}")
        logger.info("  - 'login': OAuth2 login system (ss-manager auth login)")
        logger.info("  - 'creds': Registered credentials (ss-manager reg-creds)")
        logger.info("")

        logger.info("OAuth2 Login (ss-manager auth login):")
        auth_login_status = get_login_status(login_config.token_path)
        for line in auth_login_status.to_strings():
            logger.info(f"  {line}")

        logger.info("")

        logger.info("Manually registered credentials (ss-manager reg-creds):")
        reg_creds_status = get_login_status(reg_creds_config.token_path)
        for line in reg_creds_status.to_strings():
            logger.info(f"  {line}")

        logger.info("")

        logger.info(
            "If a refresh token exists but you are not logged in, "
            "please run the authentication command again."
        )
        return
    else:
        logger.error(f"Unknown auth action: {args.auth_action}")
        exit(1)


def subcommand_reg_creds(
    creds_path: str | None,
) -> None:
    creds_savepath = get_credentials_path()
    token_path = reg_creds_config.token_path
    hidden_dir = creds_savepath.parent
    if creds_path is not None:
        if not hidden_dir.exists():
            logger.info(f"create hidden directory: {hidden_dir}")
            hidden_dir.mkdir()

        # 上書きが発生する場合は確認する
        if token_path.exists():
            if not ask_ok(
                f"{hidden_dir} already exists. Rewrite this?", default_response=False
            ):
                return
            else:
                token_path.unlink()
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
    token = get_oauth_token_reg_creds()
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
    elif args.subcommand == "setup":
        setup_problem(args=args)
    elif args.subcommand == "auth":
        subcommand_auth(
            args=args,
        )
    elif args.subcommand == "reg-creds":
        subcommand_reg_creds(
            creds_path=args.creds_path,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
