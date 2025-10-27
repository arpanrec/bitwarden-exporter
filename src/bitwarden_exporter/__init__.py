"""
This module initializes logging for the Bitwarden Exporter application and defines a custom exception.

Classes:
    BitwardenException: Base exception for Bitwarden Export.
"""

from pydantic import BaseModel


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
    """

    export_location: str
    export_password: str
    allow_duplicates: bool
    tmp_dir: str
    debug: bool
    bw_executable: str = "bw"


class BitwardenException(Exception):
    """
    Base Exception for Bitwarden Export
    """
