"""
Process bitwarden items.
"""

import json
import logging
import os.path
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel

from . import BITWARDEN_EXPORTER_GLOBAL_SETTINGS
from .bw_cli import bw_exec, download_file
from .bw_models import BwCollection, BWCurrentStatus, BwFolder, BwItem, BwItemAttachment, BwOrganization, BWStatus
from .exceptions import BitwardenException

LOGGER = logging.getLogger(__name__)


class RawItems(BaseModel):
    """
    Raw items from Bitwarden.
    """

    status: Dict[str, Any] = {}
    folders: Dict[str, Any] = {}
    organizations: List[Any] = []
    collections: List[Any] = []
    items: List[Any] = []


class BwProcessResult(BaseModel):
    """
    All items processed by the process.
    """

    organizations: Dict[str, BwOrganization] = {}
    folders: Dict[str, BwFolder] = {}
    no_folder_items: List[BwItem] = []
    raw_items: RawItems = RawItems()


def add_items_to_folder(folder_id: str, bw_folders: Dict[str, BwFolder], bw_item: BwItem) -> None:
    """
    Add a Bitwarden item into its corresponding KeePass folder bucket.

    Args:
        folder_id: The ID of the folder to which the item should be added.
        bw_folders: Mapping of folder ID to BwFolder instances.
        bw_item: The Bitwarden item to assign to a folder.
    """

    bw_folders[folder_id].items[bw_item.id] = bw_item


def add_items_to_organization(
    organization_id: str,
    bw_organizations: Dict[str, BwOrganization],
    bw_item: BwItem,
    allow_duplicates: bool = False,
) -> None:
    """
    Add a Bitwarden item into one or more organization collections.

    Behavior:
    - If the item belongs to multiple collections and allow_duplicates is False,
      only the first collection is used, and a warning is logged.

    Args:
        organization_id: The ID of the organization to which the item should be added.
        bw_organizations: Mapping of organization ID to BwOrganization instances.
        bw_item: The Bitwarden item to assign to collections within an organization.
        allow_duplicates: If True, allow multiple collections for an item.
    """

    organization = bw_organizations[organization_id]

    if not bw_item.collectionIds or len(bw_item.collectionIds) < 1:
        error_msg = (
            "There is an item without any collection, but included in organization. "
            "Enable debug logging for more information"
        )
        LOGGER.warning(error_msg)
        LOGGER.info(
            "Item: %s does not belong to any collection, but included in organization %s",
            bw_item.name,
            organization.name,
        )
        raise BitwardenException(error_msg)

    if len(bw_item.collectionIds) > 1 and not allow_duplicates:
        LOGGER.warning(
            "Item belongs to multiple collections. Just using the first one collection."
            "Enable debug logging for more information."
        )
        LOGGER.info(
            'Item: "%s" belongs to multiple collections, Just using the first one collection: "%s"',
            bw_item.name,
            organization.collections[bw_item.collectionIds[0]].name,
        )
        organization.collections[bw_item.collectionIds[0]].items[bw_item.id] = bw_item
    else:
        for collection_id in bw_item.collectionIds:
            collection = organization.collections[collection_id]
            collection.items[bw_item.id] = bw_item


# pylint: disable=too-many-locals,too-many-statements,too-many-branches
def process_list(allow_duplicates: bool = False) -> BwProcessResult:
    """
    Run the Bitwarden-to-KeePass export process end-to-end.

    Steps:
    1. Verify BW vault is unlocked and fetch folders, organizations, collections, and items via the Bitwarden CLI.
    2. Download item attachments and materialize SSH keys into temporary files.
    3. Organize items by organization/collection and by folder; collect items without either.
    4. Persist all content to a KeePass database via KeePassStorage, including JSON exports as attachments.
    5. Optionally, remove the temporary directory when not in debug mode.

    Returns:
        BwProcessResult

    Raises:
        BitwardenException: If the vault is locked or an invariant fails during processing.
        ValueError: If CLI execution fails (propagated from bw_exec).
    """
    bw_process_items: BwProcessResult = BwProcessResult()

    bw_current_status = BWStatus(**json.loads(bw_exec(["status"], is_raw=False)))
    bw_process_items.raw_items.status.update(bw_current_status)

    LOGGER.warning("Current Bitwarden status: %s", bw_current_status.status)

    if bw_current_status.status != BWCurrentStatus.UNLOCKED:
        raise BitwardenException("Vault is not unlocked")

    bw_folders_dict = json.loads((bw_exec(["list", "folders"], is_raw=False)))

    for bw_folder_dict in bw_folders_dict:
        bw_folder = BwFolder(**bw_folder_dict)
        if not bw_folder.id:
            continue

        bw_process_items.folders[bw_folder.id] = bw_folder

    LOGGER.warning("Fetching summary: application retrieved folders from Bitwarden CLI")
    LOGGER.info("Total Folders Fetched: %s", len(bw_process_items.folders))

    bw_organizations_dict = json.loads((bw_exec(["list", "organizations"], is_raw=False)))
    bw_process_items.raw_items.organizations.append(bw_organizations_dict)

    for bw_organization_dict in bw_organizations_dict:
        bw_organization = BwOrganization(**bw_organization_dict)
        bw_process_items.organizations[bw_organization.id] = bw_organization

    LOGGER.warning("Fetching summary: application retrieved organizations from Bitwarden CLI")
    LOGGER.info("Total Organizations Fetched: %s", len(bw_process_items.organizations))

    bw_collections_dict = json.loads((bw_exec(["list", "collections"], is_raw=False)))
    bw_process_items.raw_items.collections.append(bw_collections_dict)
    LOGGER.warning("Fetching summary: application retrieved collections from Bitwarden CLI")
    LOGGER.info("Total Collections Fetched: %s", len(bw_collections_dict))

    for bw_collection_dict in bw_collections_dict:
        bw_collection = BwCollection(**bw_collection_dict)
        organization = bw_process_items.organizations[bw_collection.organizationId]
        organization.collections[bw_collection.id] = bw_collection

    bw_items_dict: List[Dict[str, Any]] = json.loads((bw_exec(["list", "items"], is_raw=False)))
    bw_process_items.raw_items.items.append(bw_items_dict)

    LOGGER.warning("Fetching summary: application retrieved items from Bitwarden CLI")
    LOGGER.info("Total Items Fetched: %s", len(bw_items_dict))
    for bw_item_dict in bw_items_dict:
        bw_item = BwItem(**bw_item_dict)
        LOGGER.debug("Processing Item %s", bw_item.name)
        if bw_item.attachments and len(bw_item.attachments) > 0:
            for attachment in bw_item.attachments:
                attachment.local_file_path = os.path.join(
                    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir, bw_item.id, attachment.id
                )
                LOGGER.warning("Downloading attachment: application is saving Bitwarden attachment to a temporary path")
                LOGGER.info(
                    "%s:: Downloading Attachment %s to %s",
                    bw_item.name,
                    attachment.fileName,
                    attachment.local_file_path,
                )
                download_file(bw_item.id, attachment.id, attachment.local_file_path)

        if bw_item.sshKey:
            LOGGER.debug("Processing SSH Key Item %s", bw_item.name)

            download_location = os.path.join(BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir, bw_item.id)
            if not os.path.exists(download_location):
                os.makedirs(download_location)

            epoch_id = str(datetime.now(timezone.utc).timestamp())
            attachment_priv_key = BwItemAttachment(
                id=epoch_id,
                fileName="id_key",
                size="",
                sizeName="",
                url="",
                local_file_path=os.path.join(BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir, bw_item.id, epoch_id),
            )
            with open(attachment_priv_key.local_file_path, "w", encoding="utf-8") as ssh_priv_file:
                ssh_priv_file.write(bw_item.sshKey.privateKey)
            bw_item.attachments.append(attachment_priv_key)

            attachment_pub_key = BwItemAttachment(
                id=epoch_id + "-pub",
                fileName="id_key.pub",
                size="",
                sizeName="",
                url="",
                local_file_path=os.path.join(BITWARDEN_EXPORTER_GLOBAL_SETTINGS.tmp_dir, bw_item.id, epoch_id + "-pub"),
            )
            with open(attachment_pub_key.local_file_path, "w", encoding="utf-8") as ssh_pub_file:
                ssh_pub_file.write(bw_item.sshKey.publicKey)
            bw_item.attachments.append(attachment_pub_key)

        if bw_item.organizationId:
            add_items_to_organization(bw_item.organizationId, bw_process_items.organizations, bw_item, allow_duplicates)
        elif bw_item.folderId:
            add_items_to_folder(bw_item.folderId, bw_process_items.folders, bw_item)
        else:
            bw_process_items.no_folder_items.append(bw_item)

    LOGGER.warning("Summary: application finished processing items and is about to write to KeePass")
    LOGGER.info("Total Items Fetched: %s", len(bw_items_dict))
    return bw_process_items
