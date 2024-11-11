import logging
import os
import sys

IS_DEBUG: bool = False
LOGGING_LEVEL: int = logging.INFO
if str(os.environ.get("DEBUG", "False")).lower() == "true":
    IS_DEBUG = True
    LOGGING_LEVEL = logging.DEBUG

print("Remove existing log handlers")
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s.%(funcName)s():%(lineno)d:- %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


class BitwardenException(Exception):
    """
    Base Exception for Bitwarden Export
    """