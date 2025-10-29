"""
Delete downloaded Files.
"""

import logging
import shutil

from . import BITWARDEN_EXPORTER_GLOBAL_SETTINGS

LOGGER = logging.getLogger(__name__)


def remove_downloaded() -> None:
    """
    Remove the temporary directory used for downloading attachments.
    """
    if not BITWARDEN_EXPORTER_GLOBAL_SETTINGS.debug:
        shutil.rmtree(BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir)
    else:
        LOGGER.warning("Debug enabled: application will keep the temporary directory for troubleshooting")
        LOGGER.info("Keeping temporary directory %s", BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir)
