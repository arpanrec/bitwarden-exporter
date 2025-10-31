import tempfile
from typing import Optional

from pydantic import BaseModel, Field

from .bw_models import BWStatus


class GlobalSettings(BaseModel):
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
    bw_app_data_dir: Optional[str] = None
    bw_session: Optional[str] = None
    bw_status: Optional[BWStatus] = None


GLOBAL_SETTINGS: GlobalSettings = GlobalSettings()
