import logging
import sys
import tempfile
import time

import typer

from . import BitwardenExportSettings, login
from .bw_list_process import process_list
from .exporter.keepass import keepass_config_cli

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
This will not delete the temporary directory after the export.
"""

exporter_cli = typer.Typer()

exporter_cli.add_typer(keepass_config_cli)


# pylint: disable=too-many-arguments,too-many-positional-arguments
@exporter_cli.command(name="export", add_help_option=True)
def export(
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
