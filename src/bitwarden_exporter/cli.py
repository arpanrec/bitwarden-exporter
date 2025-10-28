"""
Command line global options.
"""

import logging
import sys
import time
from importlib.metadata import PackageNotFoundError, version

import typer

from bitwarden_exporter import APPLICATION_PACKAGE_NAME, BITWARDEN_EXPORTER_GLOBAL_SETTINGS, CLI_DEBUG_HELP
from bitwarden_exporter.exporter import keepass_exporter

app = typer.Typer(
    name=APPLICATION_PACKAGE_NAME,
    help="Bitwarden Exporter CLI",
    chain=True,
)


def version_callback(value: bool) -> None:
    """
    Show the application's version and exit.
    """
    if value:
        try:
            uv_version = version(APPLICATION_PACKAGE_NAME)
            print(f"{uv_version}")
            raise typer.Exit()
        except PackageNotFoundError as e:
            raise SystemExit(f"Package {APPLICATION_PACKAGE_NAME} not found") from e


def debug_callback(is_debug: bool) -> None:
    """
    Enable verbose logging.
    """

    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.debug = is_debug
    logging.basicConfig(
        level=logging.DEBUG if is_debug else logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s.%(funcName)s():%(lineno)d:- %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def tmp_dir_callback(tmp_dir: str) -> None:
    """
    Set the temporary directory for the application.
    """
    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir = tmp_dir


def bw_executable_callback(bw_executable: str) -> None:
    """
    Set the Bitwarden CLI executable path or command name.
    """
    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_executable = bw_executable


# pylint: disable=missing-function-docstring
@app.callback()
def version_option_register(
    # pylint: disable=unused-argument
    app_version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the application's version and exit.",
    ),
    debug: bool = typer.Option(
        BITWARDEN_EXPORTER_GLOBAL_SETTINGS.debug,
        help=CLI_DEBUG_HELP,
        callback=debug_callback,
        is_eager=True,
    ),
    tmp_dir: str = typer.Option(
        default=BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir,
        help="Temporary directory to store temporary sensitive files.",
        show_default="Temporary directory",
        is_eager=True,
        callback=tmp_dir_callback,
    ),
    bw_executable: str = typer.Option(
        BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_executable,
        "--bw",
        help="Path or command name of the Bitwarden CLI executable.",
        callback=bw_executable_callback,
        is_eager=True,
    ),
) -> None:
    """
    Main command-line interface for Bitwarden to KeePass export.
    """


@app.command(name="keepass")
def keepass_export_cli(
    kdbx_password: str = typer.Option(..., "--kdbx-password", "-p", help=keepass_exporter.KDBX_EXPORT_PASSWORD_HELP),
    kdbx_file: str = typer.Option(
        f"bitwarden_dump_{int(time.time())}.kdbx",
        "--kdbx-file",
        "-k",
        help="Bitwarden Export Location",
        show_default="bitwarden_dump_<timestamp>.kdbx",
    ),
) -> None:
    keepass_exporter.create_database_cli(kdbx_password, kdbx_file)
