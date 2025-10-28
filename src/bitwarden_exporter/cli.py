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


select_exporter = typer.Typer()


@select_exporter.command(name="keepass", help="Export Bitwarden data to KDBX file.")
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
    """
    CLI interface for exporting Bitwarden data to KeePass.
    """
    keepass_exporter.create_database_cli(kdbx_password, kdbx_file)


app.add_typer(select_exporter, name="export", help="Select the exporter to use", chain=False)


def main():
    """
    Main entry point for the Bitwarden to KeePass exporter CLI.
    """
    app()


if __name__ == "__main__":
    main()
