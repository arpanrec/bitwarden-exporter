# Bitwarden Exporter

Python Wrapper for [Password Manager CLI](https://bitwarden.com/help/cli/) for exporting bitwarden vaults to KeePass.

## Features

- **Comprehensive data mapping**
  - Credentials
  - URIs (Compatible with keepass URL)
  - Notes (Compatible with keepass note)
  - TOTP codes (Compatible with keepass totp)
  - Custom Fields (Compatible with additional attributes)
  - Identity/Cards (Backup only, not supported by Keepass yet)
  - Attachments (Compatible with keepass attachment)
  - SSH keys (Compatible with keepass ssh and attachments)
  - Fido U2F Keys (Backup only, not supported by Keepass yet)
- **Preserves vault structure**
  - Collection and Folder hierarchy is preserved as Keepass groups.
- Built-in JSON snapshot of vault data for auditing.
- Configurable CLI with options for duplicates handling, custom temp directory, debug logging, and Bitwarden CLI path.

Bitwarden Web
![Bitwarden Web](./docs/Screenshot_webvault.png 'Bitwarden Web')

Structure TOTP
![Structure TOTP](./docs/Screenshot_structure_totp.png 'Structure TOTP')

[Other screenshots](./docs/screenshots.md).

## Prerequisites

- [Bitwarden CLI](https://bitwarden.com/help/article/cli/#download-and-install)

- [Python](https://www.python.org/)
  - [uvx](https://docs.astral.sh/uv/guides/tools/) (optional)
  - [pipx](https://github.com/pypa/pipx) (optional)
  - venv (optional)

## Installation

(Recommended) Run with [uvx](https://docs.astral.sh/uv/guides/tools/)
from [PyPI](https://pypi.org/project/bitwarden-exporter/)

```bash
BW_SESSION=<session token> uvx bitwarden-exporter==VERSION --help
```

or

```bash
BW_SESSION=<session token> uvx bitwarden-exporter --help
```

Run it from [source](https://github.com/arpanrec/bitwarden-exporter)

```bash
BW_SESSION=<session token> uvx git+https://github.com/arpanrec/bitwarden-exporter.git@main bitwarden-exporter --help
```

Install with [pipx](https://github.com/pypa/pipx) from [PyPI](https://pypi.org/project/bitwarden-exporter/)

```bash
BW_SESSION=<session token> pipx install bitwarden-exporter
```

## Options

Run `bitwarden-exporter --help` to see all available options.

### Required Options

#### `--export-password`, `-p`

**Required** - Password for the exported KeePass database.

You can provide the password in multiple ways:

- **Direct value**: `--export-password "my-secret-password"`
- **From file**: `--export-password file:secret.txt`
- **From environment**: `--export-password env:SECRET_PASSWORD`
- **From vault** (JMESPath expression):
  `--export-password "jmespath:[?id=='xx-xx-xx-xxx-xxx'].fields[] | [?name=='export-password'].value"`

### Optional Configuration

#### `--export-location`, `-l`

Path for the exported KeePass database file.

- **Default**: `bitwarden_dump_<timestamp>.kdbx`
- **Note**: If the file exists, it will be overwritten.

#### `--allow-duplicates`, `-d`

Allow duplicate entries in the export. Since Bitwarden items can belong to multiple collections, this option controls
whether to create duplicate entries in KeePass.

- **Default**: `--no-allow-duplicates`

#### `--tmp-dir`, `-t`

Custom temporary directory for storing temporary sensitive files during export.

- **Default**: System temporary directory
- **⚠️ Security Note**: Make sure to delete this directory after export.

#### `--bw-executable`, `-e`

Path to the Bitwarden CLI executable.

- **Default**: `bw` (from system PATH)

#### `--debug`

Enable verbose logging for troubleshooting.

- **Default**: `--no-debug`
- **⚠️ Warning**: Debug logs may contain sensitive information. When enabled, the temporary directory will NOT be
  automatically deleted.

## Roadmap

- Make a cloud-ready option for bitwarden zero-touch backup, Upload to cloud storage.
- Restore back to bitwarden.

## Credits

[@ckabalan](https://github.com/ckabalan)
for [bitwarden-attachment-exporter](https://github.com/ckabalan/bitwarden-attachment-exporter)

## License

MIT
