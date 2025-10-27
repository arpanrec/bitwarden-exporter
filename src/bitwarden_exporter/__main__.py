"""
This module provides functionality to manage settings for the Bitwarden Exporter.
"""

import logging
import sys
import tempfile
import time
from importlib.metadata import PackageNotFoundError, version

import typer

# uv run typer src/bitwarden_exporter/__main__.py utils docs --output docs/cli.md
# Relative imports will not work when running as a script to generate docs.
from bitwarden_exporter import BitwardenExportSettings
from bitwarden_exporter.bw_list_process import process_list

CLI_SESSION_TOKEN_HELP = """
Direct value: --session-token "my-secret-password".
From a file: --session-token file:secret.txt.
From environment: --session-token env:SECRET_PASSWORD.

"""  # nosec B105

CLI_MASTER_PASSWORD_HELP = """
Direct value: --master-password "my-secret-password".
From a file: --master-password file:secret.txt.
From environment: --master-password env:SECRET_PASSWORD.
"""  # nosec B105

CLI_EXPORT_PASSWORD_HELP = r"""
Direct value: --export-password "my-secret-password".
From a file: --export-password file:secret.txt.
From environment: --export-password env:SECRET_PASSWORD.
From vault (JMESPath expression): --export-password "jmespath:[?id=='xx-xx-xx-xxx-xxx'].fields[] | [?name=='export-password'].value".

"""  # nosec B105

CLI_DEBUG_HELP = """
Enable verbose logging, This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION,
This will not delete the temporary directory after the export, Default: --no-debug
"""

APPLICATION_PACKAGE_NAME = "bitwarden-exporter"

APPLICATION_NAME_ASCII = r"""
 ____  _ _                         _
| __ )(_) |___      ____ _ _ __ __| | ___ _ __
|  _ \| | __\ \ /\ / / _` | '__/ _` |/ _ \ '_ \
| |_) | | |_ \ V  V / (_| | | | (_| |  __/ | | |
|____/|_|\__| \_/\_/ \__,_|_|_ \__,_|\___|_| |_|
| ____|_  ___ __   ___  _ __| |_ ___ _ __
|  _| \ \/ / '_ \ / _ \| '__| __/ _ \ '__|
| |___ >  <| |_) | (_) | |  | ||  __/ |
|_____/_/\_\ .__/ \___/|_|   \__\___|_|
           |_|
"""

app = typer.Typer(
    name=APPLICATION_PACKAGE_NAME,
    help="Bitwarden Exporter CLI",
)

app.pretty_exceptions_enable = True


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


# pylint: disable=missing-function-docstring
@app.callback()
def version_registered(
    # pylint: disable=unused-argument
    app_version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the application's version and exit.",
    )
) -> None: ...


# pylint: disable=too-many-arguments,too-many-positional-arguments
@app.command(name="keepass", add_help_option=True)
def get_bitwarden_settings_based_on_args(
    export_location: str = typer.Option(
        default=f"bitwarden_dump_{int(time.time())}.kdbx",
        help="Bitwarden Export Location",
        show_default="bitwarden_dump_<timestamp>.kdbx",
    ),
    export_password: str = typer.Option(
        ...,
        help=CLI_EXPORT_PASSWORD_HELP,
    ),
    allow_duplicates: bool = typer.Option(
        False, help="Allow duplicates entries in export, In bitwarden each item can be in multiple collections,"
    ),
    tmp_dir: str = typer.Option(
        default=tempfile.mkdtemp(prefix="bitwarden_exporter_"),
        help="Temporary directory to store temporary sensitive files.",
        show_default="Temporary directory",
    ),
    bw_executable: str = typer.Option(
        "bw",
        help="Path to the Bitwarden CLI executable.",
    ),
    debug: bool = typer.Option(
        False,
        help=CLI_DEBUG_HELP,
    ),
) -> None:
    """
    Export Bitwarden data to KDBX file.
    """

    print(APPLICATION_NAME_ASCII)

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s.%(funcName)s():%(lineno)d:- %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    settings = BitwardenExportSettings(
        export_location=export_location,
        export_password=export_password,
        allow_duplicates=allow_duplicates,
        tmp_dir=tmp_dir,
        debug=debug,
        bw_executable=bw_executable,
    )

    process_list(settings)


def main() -> None:
    """
    Main entrypoint for the Bitwarden Exporter CLI.
    """
    app()


if __name__ == "__main__":
    main()
