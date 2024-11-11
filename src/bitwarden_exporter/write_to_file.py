from typing import Union

from . import BitwardenException


def write_to_file(data: str, path: Union[str, bytes]) -> None:
    if isinstance(data, str):
        mode = "w"
        sys_encoding = "UTF-8"
    elif isinstance(data, bytes):
        mode = "wb"
        sys_encoding = None
    else:
        raise BitwardenException("Type Unable to Write {type(data)}")

    with open(path, mode, encoding=sys_encoding) as file_attach:
        file_attach.write(data)


def write_to_keepass():
    """
    Function to write to Keepass
    """
