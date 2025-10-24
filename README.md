# Bitwarden Exporter

Python Wrapper for [Password Manager CLI](https://bitwarden.com/help/cli/) for exporting bitwarden vaults.

## Features

- Export your entire Bitwarden vault to a KeePass (.kdbx) database using the official Bitwarden CLI.
- Preserves structure and grouping:
  - Personal items are placed under a top-level "My Vault" group and organized by your Bitwarden folders.
  - Organization items are grouped by Organization → Collection, mirroring Bitwarden.
  - Items without a folder/collection are added to the "My Vault" root.
- Rich item data mapping to KeePass entries:
  - Title, Username, Password, Notes.
  - URIs (primary URL mapped to entry URL; additional URIs stored as custom properties).
  - TOTP/OTP codes are added to the entry so they can be used from KeePass.
  - Custom fields (text/hidden/boolean and linked types) are preserved as KeePass custom properties.
  - Identity and Card details (name, address, card brand/expiry, etc.) are included as custom properties.
- Attachments and SSH keys:
  - All Bitwarden attachments are downloaded and attached to the corresponding KeePass entry.
  - If duplicate attachment names occur, they are de-duplicated automatically (e.g., by appending -1).
  - Items with SSH keys have their private/public keys materialized as files and attached to the entry.
- Built-in Bitwarden JSON snapshot:
  - A "Bitwarden Export" entry is created at the database root with JSON attachments of status, organizations, collections, and items for reference/auditing.
- Duplicate handling for items in multiple collections:
  - By default, items that belong to multiple collections are written only to the first collection (with a warning).
  - Use `--allow-duplicates` to place the item in all of its collections.
- Safe temporary workspace:
  - Attachments and generated SSH key files are stored in a configurable temporary directory during export.
  - The temporary directory is automatically removed after export unless `--debug` is used.
- Configurable and script-friendly CLI:
  - Choose an output path for the KDBX and supply the database password directly or via a file path.
  - Set a custom Bitwarden CLI executable path with `--bw-executable`.
  - Verbose debug logging with `--debug` (may log sensitive data; keeps temp files for troubleshooting).
- Prerequisites and safeguards:
  - Requires the Bitwarden CLI (`bw`) and an unlocked vault; the exporter will error if the vault is locked.


## Prerequisites

- [Bitwarden CLI](https://bitwarden.com/help/article/cli/#download-and-install)

### (Recommended) Run with [uvx](https://docs.astral.sh/uv/guides/tools/)

```bash
BW_SESSION=<session token> uvx bitwarden-exporter==VERSION --help
```

or

```bash
BW_SESSION=<session token> uvx bitwarden-exporter --help
```

### Install with [pipx](https://github.com/pypa/pipx)

```bash
BW_SESSION=<session token> pipx install bitwarden-exporter
```

### Options

```bash
bitwarden-exporter --help
```

```text
usage: bitwarden-exporter [-h] [-l EXPORT_LOCATION] -p EXPORT_PASSWORD [--allow-duplicates | --no-allow-duplicates] [--tmp-dir TMP_DIR] [--bw-executable BW_EXECUTABLE] [--debug | --no-debug]

options:
  -h, --help            show this help message and exit
  -l, --export-location EXPORT_LOCATION
                        Bitwarden Export Location, Default: bitwarden_dump_<timestamp>.kdbx, This is a dynamic value, Just in case if it exists, it will be overwritten
  -p, --export-password EXPORT_PASSWORD
                        Bitwarden Export Password or Path to Password File. File paths can be prefixed with 'file:' to reference a file, e.g. file:secret.txt. Environment variables can be used to reference a file, e.g. env:SECRET_PASSWORD. From vault, jmespath expression on `bw list items`, e.g. jmespath:[?id=='xx-xx-xx-xxx-xxx'].fields[] | [?name=='export-password'].value
  --allow-duplicates, --no-allow-duplicates
                        Allow Duplicates entries in Export, In bitwarden each item can be in multiple collections, Default: --no-allow-duplicates
  --tmp-dir TMP_DIR     Temporary Directory to store temporary sensitive files, Make sure to delete it after the export, Default: /home/arpan/workspace/src/bitwarden-exporter/bitwarden_dump_attachments
  --bw-executable BW_EXECUTABLE
                        Path to the Bitwarden CLI executable, Default: bw
  --debug, --no-debug   Enable Verbose Logging, This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION,This will not delete the temporary directory after the export, Default: --no-debug
```

## Roadmap

- Make a cloud-ready option for bitwarden zero-touch backup, Upload to cloud storage.
- Restore back to bitwarden.

## Credits

[@ckabalan](https://github.com/ckabalan) for [bitwarden-attachment-exporter](https://github.com/ckabalan/bitwarden-attachment-exporter)

## License

MIT
