"""
Writes the given data to a file at the specified path.
"""

import logging
import time
from typing import Dict, List, Union

from pykeepass import PyKeePass, create_database  # type: ignore
from pykeepass.entry import Entry  # type: ignore
from pykeepass.group import Group  # type: ignore

from . import BitwardenException
from .models import BwItem, BwItemLogin, BwOrganization

LOGGER = logging.getLogger(__name__)


def write_to_file(data: str, path: Union[str, bytes]) -> None:
    """
    Function to write to a file.
    """
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


def add_group_recursive(py_kee_pass: PyKeePass, parent_group: Group, group_path: str) -> Group:
    """
    Recursively add group to Keepass
    """

    if "/" in group_path:
        group_name = group_path.split("/")[0]
        existing_subgroups: List[Group] = parent_group.subgroups
        for subgroup in existing_subgroups:
            if subgroup.name == group_name:
                add_group_recursive(py_kee_pass, subgroup, "/".join(group_path.split("/")[1:]))
        group = py_kee_pass.add_group(destination_group=parent_group, group_name=group_name)
        add_group_recursive(py_kee_pass, group, "/".join(group_path.split("/")[1:]))
    else:
        return py_kee_pass.add_group(parent_group, group_name=group_path)


def add_entry(py_kee_pass: PyKeePass, group: Group, item: BwItem) -> Entry:
    """
    Add an entry to Keepass
    """
    if not item.login:
        LOGGER.warning("No Login for %s, skipping", item.name)
        item.login = BwItemLogin(username="No Username", password="No Password")
    else:
        if not item.login.username:
            LOGGER.warning("No Username for %s, setting it to No Username", item.name)
            item.login.username = "No Username"
        if not item.login.password:
            LOGGER.warning("No Password for %s, setting it to No Password", item.name)
            item.login.password = "No Password"

    return py_kee_pass.add_entry(
        destination_group=group,
        title=item.name,
        username=item.login.username,
        password=item.login.password,
    )


def write_to_keepass(bw_organizations: Dict[str, BwOrganization]) -> None:
    """
    Function to write to Keepass
    """
    epoch_time = int(time.time())
    file_name = f"bitwarden_dump_{epoch_time}.kdbx"
    LOGGER.info("Creating Keepass Database: %s, Password: password", file_name)
    py_kee_pass: PyKeePass = create_database(file_name, password="password")
    for organization in bw_organizations.values():
        organization_group: Group = py_kee_pass.add_group(
            destination_group=py_kee_pass.root_group, group_name=organization.name
        )
        for collection in organization.collections.values():
            collection_group = add_group_recursive(py_kee_pass, organization_group, collection.name)
            for item in collection.items.values():
                try:
                    add_entry(py_kee_pass, collection_group, item)
                except Exception as e:  # pylint: disable=broad-except
                    LOGGER.error("Error adding entry %s", e)
                    continue

    py_kee_pass.save()
