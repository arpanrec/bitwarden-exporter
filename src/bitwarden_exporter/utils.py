"""
General utilities.
"""

import logging
import os
from typing import Any, Optional

import jmespath

from .exceptions import BitwardenException

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-many-branches
def resolve_secret(secret_path: str, all_items_list: Optional[list[dict[str, Any]]]) -> str:
    """
    Resolve a secret from multiple sources with optional file indirection.

    Supports three prefix types:
    - env:<VAR_NAME>: Read from environment variable
    - file:<PATH>: Read from a file at the given path
    - jmespath:<EXPR>: Evaluate JMESPath expression against all_items_list

    After prefix resolution, if the result is a valid file path, its contents
    are read and returned. Otherwise, the resolved value is returned as-is.

    Args:
        secret_path: The secret identifier with optional prefix
        all_items_list: List of Bitwarden items for JMESPath evaluation

    Returns:
        The resolved secret string
    """

    error_msg = "Unable to resolve secret, enable debug logging for more information"

    if secret_path.startswith("env:"):
        env_password = os.getenv(secret_path[4:])
        if env_password is None or len(env_password) == 0:
            LOGGER.info("Environment variable not found: %s", secret_path)
            raise BitwardenException(error_msg)
        secret_path = env_password
    elif secret_path.startswith("file:"):
        secret_path = secret_path[5:]
        if not os.path.exists(secret_path):
            LOGGER.info("File does not exist: %s", secret_path)
            raise BitwardenException(error_msg)
        if not os.path.isfile(secret_path):
            LOGGER.info("File is not a file: %s", secret_path)
            raise BitwardenException(error_msg)
    elif secret_path.startswith("jmespath:"):
        if not all_items_list:
            LOGGER.info("Cannot use JMESPath expressions: vault items not available")
            raise BitwardenException(error_msg)
        jmespath_expression = secret_path[len("jmespath:") :]
        jmespath_password = jmespath.search(jmespath_expression, all_items_list)

        if not jmespath_password:
            LOGGER.info("Vault password is not found")
            raise BitwardenException(error_msg)

        if isinstance(jmespath_password, list):
            if len(jmespath_password) == 0:
                LOGGER.info("JMESPath expression returned empty list")
                raise BitwardenException(error_msg)
            jmespath_password = jmespath_password[0]

        if not isinstance(jmespath_password, str):
            LOGGER.info("Vault password is not a string")
            raise BitwardenException(error_msg)

        LOGGER.info("Vault password is set from JMESPath expression")
        secret_path = jmespath_password

    if os.path.exists(secret_path) and os.path.isfile(secret_path):
        with open(secret_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                LOGGER.info("File is empty: %s", secret_path)
                raise BitwardenException(error_msg)
            return content

    return secret_path
