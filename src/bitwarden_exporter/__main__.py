"""
This script interacts with the Bitwarden CLI to export data from a Bitwarden vault.

Functions:
    main() -> None:
        Main function that handles the export process, including fetching organizations,
          collections, items, and folders from the Bitwarden vault.

Raises:
    BitwardenException: If there is an error, executing a Bitwarden CLI command, or if the vault is not unlocked.
"""

import json
import logging
import os.path
import shutil
from datetime import datetime, timezone
from typing import Any, Dict, List

from . import BITWARDEN_SETTINGS, BitwardenException
from .bw_models import BwCollection, BwFolder, BwItem, BwItemAttachment, BwOrganization
from .cli import bw_exec, download_file
from .keepass import KeePassStorage

LOGGER = logging.getLogger(__name__)


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
    organization_id: str, bw_organizations: Dict[str, BwOrganization], bw_item: BwItem
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
    """

    organization = bw_organizations[organization_id]

    if not bw_item.collectionIds or len(bw_item.collectionIds) < 1:
        LOGGER.warning("There is no collection for one or more items; skipping")
        LOGGER.info("Item %s does not have any collection, but belongs to an organization; skipping", bw_item.id)
        return

    if len(bw_item.collectionIds) > 1 and not BITWARDEN_SETTINGS.allow_duplicates:
        first_collection_id = bw_item.collectionIds[0]
        collection = organization.collections.get(first_collection_id)
        if collection is None:
            LOGGER.warning(
                "There is a item with multiple collections, but allow_duplicates is False;"
            )
            LOGGER.info(
                "%s: collectionId %s not found in organization %s; skipping this collection",
                bw_item.name,
                first_collection_id,
                organization.name,
            )
            return
        LOGGER.warning(
            'Item: "%s" belongs to multiple collections, Just using the first one collection: "%s"',
            bw_item.name,
            collection.name,
        )
        collection.items[bw_item.id] = bw_item
    else:
        for collection_id in bw_item.collectionIds:
            collection = organization.collections.get(collection_id)
            if collection is None:
                LOGGER.warning(
                    "%s: collectionId %s not found in organization %s; skipping this collection",
                    bw_item.name,
                    collection_id,
                    organization.name,
                )
                continue
            collection.items[bw_item.id] = bw_item


def main() -> None:  # pylint: disable=too-many-locals,too-many-statements
    """
    Run the Bitwarden-to-KeePass export process end-to-end.

    Steps:
    1. Verify BW vault is unlocked and fetch folders, organizations, collections, and items via the Bitwarden CLI.
    2. Download item attachments and materialize SSH keys into temporary files.
    3. Organize items by organization/collection and by folder; collect items without either.
    4. Persist all content to a KeePass database via KeePassStorage, including JSON exports as attachments.
    5. Optionally, remove the temporary directory when not in debug mode.

    Returns:
        None

    Raises:
        BitwardenException: If the vault is locked or an invariant fails during processing.
        ValueError: If CLI execution fails (propagated from bw_exec).
    """

    raw_items: Dict[str, Any] = {}
    bw_current_status = json.loads(bw_exec(["status"]))
    raw_items["status.json"] = bw_current_status

    if bw_current_status["status"] != "unlocked":
        raise BitwardenException("Vault is not unlocked")
    LOGGER.debug("Vault status: %s", json.dumps(bw_current_status))

    bw_folders_dict = json.loads((bw_exec(["list", "folders"])))
    bw_folders: Dict[str, BwFolder] = {folder["id"]: BwFolder(**folder) for folder in bw_folders_dict}
    LOGGER.info("Total Folders Fetched: %s", len(bw_folders))

    no_folder_items: List[BwItem] = []

    bw_organizations_dict = json.loads((bw_exec(["list", "organizations"])))
    raw_items["organizations.json"] = bw_organizations_dict
    bw_organizations: Dict[str, BwOrganization] = {
        organization["id"]: BwOrganization(**organization) for organization in bw_organizations_dict
    }
    LOGGER.info("Total Organizations Fetched: %s", len(bw_organizations))

    bw_collections_dict = json.loads((bw_exec(["list", "collections"])))
    raw_items["collections.json"] = bw_collections_dict
    LOGGER.info("Total Collections Fetched: %s", len(bw_collections_dict))

    for bw_collection_dict in bw_collections_dict:
        bw_collection = BwCollection(**bw_collection_dict)
        organization = bw_organizations[bw_collection.organizationId]
        organization.collections[bw_collection.id] = bw_collection

    bw_items_dict: List[Dict[str, Any]] = json.loads((bw_exec(["list", "items"])))
    raw_items["items.json"] = bw_items_dict

    LOGGER.info("Total Items Fetched: %s", len(bw_items_dict))
    for bw_item_dict in bw_items_dict:
        bw_item = BwItem(**bw_item_dict)
        LOGGER.debug("Processing Item %s", bw_item.name)
        if bw_item.attachments and len(bw_item.attachments) > 0:
            for attachment in bw_item.attachments:
                attachment.local_file_path = os.path.join(BITWARDEN_SETTINGS.tmp_dir, bw_item.id, attachment.id)
                LOGGER.info(
                    "%s:: Downloading Attachment %s to %s",
                    bw_item.name,
                    attachment.fileName,
                    attachment.local_file_path,
                )
                download_file(bw_item.id, attachment.id, attachment.local_file_path)

        if bw_item.sshKey:
            LOGGER.debug("Processing SSH Key Item %s", bw_item.name)

            download_location = os.path.join(BITWARDEN_SETTINGS.tmp_dir, bw_item.id)
            if not os.path.exists(download_location):
                os.makedirs(download_location)

            epoch_id = str(datetime.now(timezone.utc).timestamp())
            attachment_priv_key = BwItemAttachment(
                id=epoch_id,
                fileName="id_key",
                size="",
                sizeName="",
                url="",
                local_file_path=os.path.join(BITWARDEN_SETTINGS.tmp_dir, bw_item.id, epoch_id),
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
                local_file_path=os.path.join(BITWARDEN_SETTINGS.tmp_dir, bw_item.id, epoch_id + "-pub"),
            )
            with open(attachment_pub_key.local_file_path, "w", encoding="utf-8") as ssh_pub_file:
                ssh_pub_file.write(bw_item.sshKey.publicKey)
            bw_item.attachments.append(attachment_pub_key)

        if bw_item.organizationId and not bw_item.folderId:
            add_items_to_organization(bw_item.organizationId, bw_organizations, bw_item)
        elif not bw_item.organizationId and bw_item.folderId:
            add_items_to_folder(bw_item.folderId, bw_folders, bw_item)
        else:
            no_folder_items.append(bw_item)

    LOGGER.info("Total Items Fetched: %s", len(bw_items_dict))

    with KeePassStorage(BITWARDEN_SETTINGS.export_location, BITWARDEN_SETTINGS.export_password) as storage:
        storage.process_organizations(bw_organizations)
        storage.process_folders(bw_folders)
        storage.process_no_folder_items(no_folder_items)
        storage.process_bw_exports(raw_items)

    if not BITWARDEN_SETTINGS.debug:
        shutil.rmtree(BITWARDEN_SETTINGS.tmp_dir)
    else:
        LOGGER.info("Keeping temporary directory %s", BITWARDEN_SETTINGS.tmp_dir)


if __name__ == "__main__":
    main()
