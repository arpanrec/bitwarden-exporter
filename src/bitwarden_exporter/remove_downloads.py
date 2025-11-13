"""
Delete downloaded Files.
"""

import logging
import shutil

from .global_settings import GLOBAL_SETTINGS

LOGGER = logging.getLogger(__name__)


def remove_downloaded() -> None:
    """
    Remove the temporary directory used for downloading attachments.
    """
    if not GLOBAL_SETTINGS.debug:
        shutil.rmtree(GLOBAL_SETTINGS.tmp_dir)
    else:
        LOGGER.warning("Debug enabled: application will keep the temporary directory for troubleshooting")
        LOGGER.info("Keeping temporary directory %s", GLOBAL_SETTINGS.tmp_dir)
