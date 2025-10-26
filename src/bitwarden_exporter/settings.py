"""
This module provides functionality to manage settings for the Bitwarden Exporter.

Classes:
    BitwardenExportSettings: A Pydantic model that defines the settings for the Bitwarden Exporter.

Functions:
    get_bitwarden_settings_based_on_args: Parses command-line arguments to populate
      and return a BitwardenExportSettings instance.

The settings include:
    - export_location: The location where the Bitwarden export will be saved.
    - export_password: The password used for the Bitwarden export.
    - allow_duplicates: A flag to allow duplicate entries in the export.
    - tmp_dir: The temporary directory to store sensitive files during the export process.
    - verbose: A flag to enable verbose logging, which may include sensitive information.
"""

import argparse
import tempfile
import time
from importlib.metadata import PackageNotFoundError, version
from typing import Optional

from pydantic import BaseModel

from . import constants


class BitwardenExportSettings(BaseModel):
    """
    Configuration for the Bitwarden Exporter CLI.

    Attributes:
        export_location: Absolute or relative path to the output KeePass (.kdbx) file.
        export_password: KeePass database password as plain text (read from a file if a path is supplied).
        allow_duplicates: If True, items that belong to multiple collections will be duplicated across them.
        tmp_dir: Directory used to store temporary, sensitive artifacts (attachments, SSH keys) during export.
        debug: Enables verbose logging and keeps the temporary directory after export for troubleshooting.
        bw_executable: Path or command name of the Bitwarden CLI executable (defaults to "bw").
        master_password: Master password for a Bitwarden account, if not using session token.
        session_token: Session token for a Bitwarden account, if not using master password.
    """

    export_location: str
    export_password: str
    allow_duplicates: bool
    tmp_dir: str
    debug: bool
    bw_executable: str = "bw"
    master_password: Optional[str] = None
    session_token: Optional[str] = None


def get_bitwarden_settings_based_on_args() -> BitwardenExportSettings:
    """
    Parse CLI arguments and build a BitwardenExportSettings instance.

    Behavior:
    - If --export-password points to an existing file, its contents are read and used as the password.
    - A temporary directory path and other flags can be configured with switches.

    Returns:
        BitwardenExportSettings: Parsed and validated settings for the current run.

    Raises:
        SystemExit: If required arguments are missing (handled by argparse).
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-l",
        "--export-location",
        help="Bitwarden Export Location, Default: bitwarden_dump_<timestamp>.kdbx, This is a dynamic value,"
        " Just in case if it exists, it will be overwritten",
        default=f"bitwarden_dump_{int(time.time())}.kdbx",
    )

    parser.add_argument(
        "-p",
        "--export-password",
        help=constants.CLI_EXPORT_PASSWORD_HELP,
        required=True,
    )

    parser.add_argument(
        "--allow-duplicates",
        help="Allow duplicates entries in export, In bitwarden each item can be in multiple collections,"
        " Default: --no-allow-duplicates",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    parser.add_argument(
        "--tmp-dir",
        help="Temporary directory to store temporary sensitive files,"
        " Make sure to delete it after the export,"
        " Default: Temporary directory",
    )

    parser.add_argument(
        "--bw-executable",
        help="Path to the Bitwarden CLI executable, Default: bw",
        default="bw",
    )

    parser.add_argument(
        "--debug",
        help=constants.CLI_DEBUG_HELP,
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    try:
        uv_version = version(constants.APPLICATION_PACKAGE_NAME)
    except PackageNotFoundError as e:
        raise SystemExit(f"Package {constants.APPLICATION_PACKAGE_NAME} not found") from e

    parser.add_argument(
        "--version",
        action="version",
        version=uv_version,
    )

    parser.add_argument(
        "--master-password",
        help=constants.CLI_MASTER_PASSWORD_HELP,
        default=None,
        required=False,
    )

    parser.add_argument(
        "--session-token",
        help=constants.CLI_SESSION_TOKEN_HELP,
        default=None,
        required=False,
    )

    args = parser.parse_args()

    print(constants.APPLICATION_NAME_ASCII)

    if args.export_password is None:
        parser.error("Please provide --export-password")

    if not args.tmp_dir:
        args.tmp_dir = tempfile.mkdtemp(prefix="bitwarden_exporter_")

    return BitwardenExportSettings(
        export_location=args.export_location,
        export_password=args.export_password,
        allow_duplicates=args.allow_duplicates,
        tmp_dir=args.tmp_dir,
        debug=args.debug,
        bw_executable=args.bw_executable,
        master_password=args.master_password,
        session_token=args.session_token,
    )
