"""
Exceptions
"""

from .remove_downloads import remove_downloaded


class BitwardenException(Exception):
    """
    Base Exception for Bitwarden Export
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(args, kwargs)
        remove_downloaded()
