"""
This module provides a command-line interface (CLI) for interacting with Bitwarden.

Functions:
    bw_exec(cmd: List[str], ret_encoding: str = "UTF-8", env_vars: Optional[Dict[str, str]] = None) -> str:

Exceptions:
    BitwardenException:
        Raised when there is an error executing a Bitwarden CLI command.
"""

import logging
import os
import os.path
import subprocess  # nosec B404
from typing import Dict, List, Optional

from .exceptions import BitwardenException
from .global_settings import BITWARDEN_EXPORTER_GLOBAL_SETTINGS

LOGGER = logging.getLogger(__name__)


def download_file(item_id: str, attachment_id: str, download_location: str) -> None:
    """
    Download an attachment from Bitwarden to a local path.

    Args:
        item_id: The Bitwarden item identifier.
        attachment_id: The attachment identifier within the item.
        download_location: Absolute or relative path where the file will be saved. Parent
            directories are created if missing. If the file already exists, the download is skipped.

    Returns:
        None
    """
    parent_dir = os.path.dirname(download_location)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    if os.path.exists(download_location):
        LOGGER.warning("Skipping download: application detected existing file at target location")
        LOGGER.info("File already exists, skipping download")
        return

    bw_exec(
        ["get", "attachment", attachment_id, "--itemid", item_id, "--output", download_location],
        is_raw=False,
    )


def bw_exec(
    cmd: List[str],
    ret_encoding: str = "UTF-8",
    env_vars: Optional[Dict[str, str]] = None,
    is_raw: bool = True,
    capture_output: bool = True,
) -> str:
    """
    Execute the Bitwarden CLI and return stdout.

    Args:
        cmd: Arguments to pass to the bw executable (e.g., ["list", "items"]).
        ret_encoding: The character encoding for stdout/stderr decoding.
        env_vars: Optional environment variables to add/override for this invocation.
        is_raw: When True, appends --raw to the command to simplify parsing.
        capture_output: When True, captures the output of the command.

    Returns:
        str: The command's stdout content.

    Raises:
        ValueError: If the command returns a non-zero exit status.
    """
    cmd = [BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_executable] + cmd

    if is_raw:
        cmd.append("--raw")

    cli_env_vars = os.environ.copy()

    if env_vars is not None:
        cli_env_vars.update(env_vars)

    if BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_app_data_dir:
        cli_env_vars["BITWARDENCLI_APPDATA_DIR"] = BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_app_data_dir

    if BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_session:
        cli_env_vars["BW_SESSION"] = BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_session

    LOGGER.debug("Executing CLI :: %s", " ".join(cmd))
    try:
        command_out = subprocess.run(
            cmd,
            capture_output=capture_output,
            check=False,
            encoding=ret_encoding,
            env=cli_env_vars,
            timeout=10,
        )  # nosec B603
        if command_out.stderr and len(command_out.stderr) > 0:
            LOGGER.warning("Error while executing a command. Enable debug logging for more information")
            LOGGER.info("Error executing command %s", command_out.stderr)
        command_out.check_returncode()
        return command_out.stdout
    except subprocess.CalledProcessError as e:
        LOGGER.info("Error executing command %s", e)
        raise BitwardenException("Error executing command, enable debug logging for more information")
    except subprocess.TimeoutExpired as e:
        LOGGER.info("Timeout executing command %s", e)
        raise BitwardenException("Timeout executing command, enable debug logging for more information")
