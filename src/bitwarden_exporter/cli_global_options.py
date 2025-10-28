import logging
import sys
from importlib.metadata import PackageNotFoundError, version

import typer

from . import APPLICATION_NAME_ASCII, BITWARDEN_EXPORTER_GLOBAL_SETTINGS
from . import exporter
APPLICATION_PACKAGE_NAME = "bitwarden-exporter"

CLI_DEBUG_HELP = """
Enable verbose logging, This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION,
This will not delete the temporary directory after the export.
"""

app = typer.Typer(
    name=APPLICATION_PACKAGE_NAME,
    help="Bitwarden Exporter CLI",
    chain=True,
)

app.add_typer(exporter.cli)


def version_callback(value: bool) -> None:
    """
    Show the application's version and exit.
    """
    if value:
        try:
            uv_version = version(APPLICATION_PACKAGE_NAME)
            print(f"{APPLICATION_NAME_ASCII}\nv{uv_version}")
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
    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir = tmp_dir


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
) -> None: ...
