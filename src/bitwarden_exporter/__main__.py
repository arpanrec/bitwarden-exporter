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

import jmespath

from . import BITWARDEN_SETTINGS, BitwardenException
from .bw_models import BwCollection, BwFolder, BwItem, BwItemAttachment, BwOrganization
from .cli import bw_exec, download_file
from .keepass import KeePassStorage

LOGGER = logging.getLogger(__name__)


def __resolve_secret(secret_path: str, all_items_list: list[dict[str, Any]]) -> str:
    """
    Read a secret from a file or environment variable.
    """

    if secret_path.startswith("env:"):
        env_password = os.getenv(secret_path[4:])
        if env_password is None or len(env_password) == 0:
            raise ValueError(f"Environment variable not found: {secret_path}")
        secret_path = env_password
    elif secret_path.startswith("file:"):
        secret_path = secret_path[5:]
        if not os.path.exists(secret_path):
            raise FileNotFoundError(f"File not found: {secret_path}")
        if not os.path.isfile(secret_path):
            raise ValueError(f"File is not a file: {secret_path}")
    elif secret_path.startswith("jmespath:"):
        jmespath_expression = secret_path[len("jmespath:") :]
        jmespath_password = jmespath.search(jmespath_expression, all_items_list)

        if not jmespath_password:
            raise BitwardenException("Vault password is not found")

        if isinstance(jmespath_password, list):
            if len(jmespath_password) == 0:
                raise BitwardenException("JMESPath expression returned empty list")
            jmespath_password = jmespath_password[0]

        if not isinstance(jmespath_password, str):
            raise BitwardenException("Vault password is not a string")

        LOGGER.warning("Vault password is set from JMESPath expression")
        secret_path = jmespath_password

    if os.path.exists(secret_path) and os.path.isfile(secret_path):
        with open(secret_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    return secret_path


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

    if len(bw_item.collectionIds) > 1 and not BITWARDEN_SETTINGS.allow_duplicates:
        LOGGER.warning("Item belongs to multiple collections. Enable debug logging for more information")
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


def main() -> None:  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
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
    bw_current_status = json.loads(bw_exec(["status"], is_raw=False))
    raw_items["status.json"] = bw_current_status

    if bw_current_status["status"] != "unlocked":
        raise BitwardenException("Vault is not unlocked")
    LOGGER.debug("Vault status: %s", json.dumps(bw_current_status))

    bw_folders_dict = json.loads((bw_exec(["list", "folders"], is_raw=False)))
    bw_folders: Dict[str, BwFolder] = {folder["id"]: BwFolder(**folder) for folder in bw_folders_dict}
    LOGGER.warning("Fetching summary: application retrieved folders from Bitwarden CLI")
    LOGGER.info("Total Folders Fetched: %s", len(bw_folders))

    no_folder_items: List[BwItem] = []

    bw_organizations_dict = json.loads((bw_exec(["list", "organizations"], is_raw=False)))
    raw_items["organizations.json"] = bw_organizations_dict
    bw_organizations: Dict[str, BwOrganization] = {
        organization["id"]: BwOrganization(**organization) for organization in bw_organizations_dict
    }
    LOGGER.warning("Fetching summary: application retrieved organizations from Bitwarden CLI")
    LOGGER.info("Total Organizations Fetched: %s", len(bw_organizations))

    bw_collections_dict = json.loads((bw_exec(["list", "collections"], is_raw=False)))
    raw_items["collections.json"] = bw_collections_dict
    LOGGER.warning("Fetching summary: application retrieved collections from Bitwarden CLI")
    LOGGER.info("Total Collections Fetched: %s", len(bw_collections_dict))

    for bw_collection_dict in bw_collections_dict:
        bw_collection = BwCollection(**bw_collection_dict)
        organization = bw_organizations[bw_collection.organizationId]
        organization.collections[bw_collection.id] = bw_collection

    bw_items_dict: List[Dict[str, Any]] = json.loads((bw_exec(["list", "items"], is_raw=False)))

    BITWARDEN_SETTINGS.export_password = __resolve_secret(BITWARDEN_SETTINGS.export_password, bw_items_dict)

    raw_items["items.json"] = bw_items_dict

    LOGGER.warning("Fetching summary: application retrieved items from Bitwarden CLI")
    LOGGER.info("Total Items Fetched: %s", len(bw_items_dict))
    for bw_item_dict in bw_items_dict:
        bw_item = BwItem(**bw_item_dict)
        LOGGER.debug("Processing Item %s", bw_item.name)
        if bw_item.attachments and len(bw_item.attachments) > 0:
            for attachment in bw_item.attachments:
                attachment.local_file_path = os.path.join(BITWARDEN_SETTINGS.tmp_dir, bw_item.id, attachment.id)
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

        if bw_item.organizationId:
            add_items_to_organization(bw_item.organizationId, bw_organizations, bw_item)
        elif bw_item.folderId:
            add_items_to_folder(bw_item.folderId, bw_folders, bw_item)
        else:
            no_folder_items.append(bw_item)

    LOGGER.warning("Summary: application finished processing items and is about to write to KeePass")
    LOGGER.info("Total Items Fetched: %s", len(bw_items_dict))

    with KeePassStorage(BITWARDEN_SETTINGS.export_location, BITWARDEN_SETTINGS.export_password) as storage:
        storage.process_organizations(bw_organizations)
        storage.process_folders(bw_folders)
        storage.process_no_folder_items(no_folder_items)
        storage.process_bw_exports(raw_items)

    if not BITWARDEN_SETTINGS.debug:
        shutil.rmtree(BITWARDEN_SETTINGS.tmp_dir)
    else:
        LOGGER.warning("Debug enabled: application will keep the temporary directory for troubleshooting")
        LOGGER.info("Keeping temporary directory %s", BITWARDEN_SETTINGS.tmp_dir)


if __name__ == "__main__":
    main()
