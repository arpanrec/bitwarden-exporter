#!/usr/bin/env python3
"""
Command line global options.
"""

import logging
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from typing import Optional

import typer

from bitwarden_exporter import (
    APPLICATION_NAME_ASCII,
    APPLICATION_PACKAGE_NAME,
    BITWARDEN_EXPORTER_GLOBAL_SETTINGS,
    CLI_DEBUG_HELP,
    BW_SESSION_TOKEN_HELP,
)
from bitwarden_exporter.exporter import keepass_exporter
from bitwarden_exporter.utils import resolve_secret

app = typer.Typer(
    name=APPLICATION_PACKAGE_NAME,
    help="Bitwarden Exporter CLI",
    chain=True,
    pretty_exceptions_enable=False,
    pretty_exceptions_short=False,
    pretty_exceptions_show_locals=False,
)


def version_callback(app_version: bool) -> None:
    """
    Show the application's version and exit.
    """
    if app_version:
        try:
            uv_version = version(APPLICATION_PACKAGE_NAME)
            print(f"{uv_version}")
            raise typer.Exit()
        except PackageNotFoundError as e:
            raise SystemExit(f"Package {APPLICATION_PACKAGE_NAME} not found") from e


@app.callback()
def version_option_register(
    # pylint: disable=unused-argument
    app_version: bool = typer.Option(
        None,
        "--version",
        "-v",
        is_eager=True,
        callback=version_callback,
        help="Show the application's version and exit.",
    ),
    debug: bool = typer.Option(
        BITWARDEN_EXPORTER_GLOBAL_SETTINGS.debug,
        help=CLI_DEBUG_HELP,
        is_eager=True,
    ),
    tmp_dir: str = typer.Option(
        default=BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir,
        help="Temporary directory to store temporary sensitive files.",
        show_default="Temporary directory",
        is_eager=True,
    ),
    bw_executable: str = typer.Option(
        BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_executable,
        "--bw",
        help="Path or command name of the Bitwarden CLI executable.",
        is_eager=True,
    ),
    bw_app_data_dir: Optional[str] = typer.Option(
        BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_app_data_dir,
        "--bw-app-data-dir",
        help="Path to the Bitwarden CLI application data directory.",
        is_eager=True,
    ),
    bw_session: Optional[str] = typer.Option(
        BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_session,
        "--bw-session",
        help=BW_SESSION_TOKEN_HELP,
        is_eager=True,
    ),
) -> None:
    """
    Main command-line interface for Bitwarden to KeePass export.
    """
    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.debug = debug

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s.%(funcName)s():%(lineno)d:- %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_executable = bw_executable

    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir = tmp_dir

    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_app_data_dir = bw_app_data_dir

    if bw_session:
        BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_session = resolve_secret(bw_session)


target = typer.Typer()

app.add_typer(target, name="target", help="Select the target to export or import", chain=True)

target_exporter = typer.Typer()


@target_exporter.command(name="keepass", help="Export Bitwarden data to KDBX file.")
def target_exporter_keepass(
    kdbx_password: str = typer.Option(..., "--kdbx-password", "-p", help=keepass_exporter.KDBX_EXPORT_PASSWORD_HELP),
    kdbx_file: str = typer.Option(
        f"bitwarden_dump_{int(time.time())}.kdbx",
        "--kdbx-file",
        "-k",
        help="Bitwarden Export Location",
        show_default="bitwarden_dump_<timestamp>.kdbx",
    ),
) -> None:
    """
    CLI interface for exporting Bitwarden data to KeePass.
    """
    keepass_exporter.create_database_cli(kdbx_password, kdbx_file)


target_importer = typer.Typer()

target.add_typer(target_exporter, name="exporter", help="Select the exporter to use", chain=True)
target.add_typer(target_importer, name="importer", help="TO BE IMPLEMENTED", chain=True, deprecated=True)


def main() -> None:
    """
    Main entry point for the Bitwarden to KeePass exporter CLI.
    """
    print(APPLICATION_NAME_ASCII)
    app()


if __name__ == "__main__":
    main()
