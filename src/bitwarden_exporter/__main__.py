"""
This script interacts with the Bitwarden CLI to export data from a Bitwarden vault.

Functions:
    bw_exec(cmd: List[str], ret_encoding: str = "UTF-8", env_vars: Optional[Dict[str, str]] = None) -> str:
        Executes a Bitwarden CLI command and returns the output as a string.
    
    main() -> None:
        Main function that handles the export process, including fetching organizations,
          collections, items, and folders from the Bitwarden vault.

Raises:
    BitwardenException: If there is an error executing a Bitwarden CLI command or if the vault is not unlocked.

"""

import argparse
import json
import logging
import os.path
import time
from typing import Any, Dict, List

from . import BitwardenException
from .cli import bw_exec, download_file
from .keepass import KeePassStorage
from .models import BwCollection, BwFolder, BwItem, BwOrganization

LOGGER = logging.getLogger(__name__)


def main() -> None:  # pylint: disable=too-many-locals
    """
    Main function that handles the export process, including fetching organizations,
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--export-location", help="Bitwarden Export Location", default=f"bitwarden_dump_{int(time.time())}.kdbx"
    )
    parser.add_argument("-p", "--export-password", help="Bitwarden Export Password", required=True)
    parser.add_argument(
        "--allow-duplicates",
        help="Allow Duplicates entries in Export, In bitwarden each item can be in multiple collections",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--tmp-dir",
        help="Temporary Directory to store attachments",
        default=os.path.abspath("bitwarden_dump_attachments"),
    )

    args, _ = parser.parse_known_args()
    bw_current_status = json.loads(bw_exec(["status"]))
    if bw_current_status["status"] != "unlocked":
        raise BitwardenException("Vault is not unlocked")

    bw_organizations_dict = json.loads((bw_exec(["list", "organizations"])))
    bw_organizations: Dict[str, BwOrganization] = {
        organization["id"]: BwOrganization(**organization) for organization in bw_organizations_dict
    }
    LOGGER.info("Total Organizations Fetched: %s", len(bw_organizations))

    bw_collections_dict = json.loads((bw_exec(["list", "collections"])))
    LOGGER.info("Total Collections Fetched: %s", len(bw_collections_dict))

    for bw_collection_dict in bw_collections_dict:
        bw_collection = BwCollection(**bw_collection_dict)
        organization = bw_organizations[bw_collection.organizationId]
        organization.collections[bw_collection.id] = bw_collection

    bw_items_dict: List[Dict[str, Any]] = json.loads((bw_exec(["list", "items"])))

    LOGGER.info("Total Items Fetched: %s", len(bw_items_dict))
    for bw_item_dict in bw_items_dict:
        bw_item = BwItem(**bw_item_dict)
        LOGGER.debug("Processing Item %s", bw_item.name)
        if bw_item.attachments and len(bw_item.attachments) > 0:
            for attachment in bw_item.attachments:
                attachment.local_file_path = os.path.join(args.tmp_dir, bw_item.id, attachment.id)
                LOGGER.info(
                    "%s:: Downloading Attachment %s to %s",
                    bw_item.name,
                    attachment.fileName,
                    attachment.local_file_path,
                )
                download_file(bw_item.id, attachment.id, attachment.local_file_path)
        if not bw_item.organizationId:
            continue

        organization = bw_organizations[bw_item.organizationId]

        if not bw_item.collectionIds or len(bw_item.collectionIds) < 1:
            raise BitwardenException(f"Item {bw_item.id} does not have any collection, but belongs to an organization")

        if len(bw_item.collectionIds) > 1 and args.allow_duplicates:
            LOGGER.warning(
                "Item %s belongs to multiple collections Just using the first one %s",
                bw_item.id,
                organization.collections[bw_item.collectionIds[0]].name,
            )
            organization.collections[bw_item.collectionIds[0]].items[bw_item.id] = bw_item
        else:
            for collection_id in bw_item.collectionIds:
                collection = organization.collections[collection_id]
                collection.items[bw_item.id] = bw_item

    LOGGER.info("Total Items Fetched: %s", len(bw_items_dict))

    bw_folders: List[BwFolder] = [BwFolder(**folder) for folder in json.loads((bw_exec(["list", "folders"])))]
    LOGGER.info("Total Folders Fetched: %s", len(bw_folders))

    with KeePassStorage(args.export_location, args.export_password) as storage:
        storage.process_organization(bw_organizations)

    # if not is_debug():
    #     LOGGER.info("Removing Temporary Directory %s", args.tmp_dir)
    #     shutil.rmtree(args.tmp_dir)
    #     LOGGER.info("Clearing Bitwarden Cache")
    #     bw_exec.clear_cache()


if __name__ == "__main__":
    main()
