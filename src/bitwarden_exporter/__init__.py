"""
This module initializes logging for the Bitwarden Exporter application and defines a custom exception.

Classes:
    BitwardenException: Base exception for Bitwarden Export.
"""

import tempfile

from pydantic import BaseModel, Field


class BitwardenExportSettings(BaseModel):
    """
    Configuration for the Bitwarden Exporter CLI.

    Attributes:
        tmp_dir: Directory used to store temporary, sensitive artifacts (attachments, SSH keys) during export.
        debug: Enables verbose logging and keeps the temporary directory after export for troubleshooting.
        bw_executable: Path or command name of the Bitwarden CLI executable (defaults to "bw").
    """

    tmp_dir: str = Field(default_factory=tempfile.mkdtemp)
    debug: bool = False
    bw_executable: str = "bw"


BITWARDEN_EXPORTER_GLOBAL_SETTINGS: BitwardenExportSettings = BitwardenExportSettings()

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

CLI_DEBUG_HELP = """
Enable verbose logging, This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION,
This will not delete the temporary directory after the export.
"""

APPLICATION_PACKAGE_NAME = "bitwarden-exporter"
