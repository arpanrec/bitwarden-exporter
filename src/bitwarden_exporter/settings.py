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

import pyfiglet  # type: ignore
from pydantic import BaseModel


class BitwardenExportSettings(BaseModel):
    """
    Configuration for the Bitwarden Exporter CLI.

    Attributes:
        export_location: Absolute or relative path to the output KeePass (.kdbx) file.
        export_password: KeePass database password as plain text (read from file if a path is supplied).
        allow_duplicates: If True, items that belong to multiple collections will be duplicated across them.
        tmp_dir: Directory used to store temporary, sensitive artifacts (attachments, SSH keys) during export.
        debug: Enables verbose logging and keeps the temporary directory after export for troubleshooting.
        bw_executable: Path or command name of the Bitwarden CLI executable (defaults to "bw").
    """

    export_location: str
    export_password: str
    allow_duplicates: bool
    tmp_dir: str
    debug: bool
    bw_executable: str = "bw"


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
        help="Bitwarden Export Password or Path to Password File."
        " File paths can be prefixed with 'file:' to reference a file, e.g. file:secret.txt."
        " Environment variables can be used to reference a file, e.g. env:SECRET_PASSWORD."
        " From vault, jmespath expression on `bw list items`, e.g. jmespath:["
        "?id=='xx-xx-xx-xxx-xxx'].fields[] | ["
        "?name=='export-password'].value",
        required=True,
    )

    parser.add_argument(
        "--allow-duplicates",
        help="Allow Duplicates entries in Export, In bitwarden each item can be in multiple collections,"
        " Default: --no-allow-duplicates",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    parser.add_argument(
        "--tmp-dir",
        help="Temporary Directory to store temporary sensitive files,"
        " Make sure to delete it after the export,"
        " Default: Temporary Directory",
    )

    parser.add_argument(
        "--bw-executable",
        help="Path to the Bitwarden CLI executable, Default: bw",
        default="bw",
    )

    parser.add_argument(
        "--debug",
        help="Enable Verbose Logging, This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION,"
        "This will not delete the temporary directory after the export,"
        " Default: --no-debug",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    if __name__ == "__main__":
        print(pyfiglet.figlet_format("Bitwarden Exporter"))
    args = parser.parse_args()

    if args.export_password is None:
        parser.error("Please provide --export-password")

    if args.tmp_dir is None or args.tmp_dir == "":
        args.tmp_dir = tempfile.TemporaryDirectory(delete=False).name  # pylint: disable=consider-using-with

    return BitwardenExportSettings(
        export_location=args.export_location,
        export_password=args.export_password,
        allow_duplicates=args.allow_duplicates,
        tmp_dir=args.tmp_dir,
        debug=args.debug,
        bw_executable=args.bw_executable,
    )
