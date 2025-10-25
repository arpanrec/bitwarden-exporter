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

![Bitwarden Web](./docs/Screenshot_20251025_175253.png "Bitwarden Web")
![TOTP](./docs/Screenshot_20251025_175031.png "TOTP")
![SSH KEY](./docs/Screenshot_20251025_175050.png "SSH KEY")

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

#### Export Location (-l, --export-location)

Bitwarden Export Location, Default: `bitwarden_dump_<timestamp>.kdbx`,

This is a dynamic value, Just in case if it exists, it will be overwritten.

#### Export Password (-p, --export-password)

- Required

Bitwarden Export Password or Path to Password File.

File paths can be prefixed with 'file:' to reference a file, e.g. file:secret.txt.

Environment variables can be used to reference a file, e.g. env:SECRET_PASSWORD.

From vault, jmespath expression on `bw list items`,

e.g. `jmespath:[?id=='xx-xx-xx-xxx-xxx'].fields[] | [?name=='export-password'].value`.

#### Allow Duplicates (-d, --allow-duplicates)

Allow Duplicates entries in Export, In bitwarden each item can be in multiple collections.

Default: --no-allow-duplicates

#### Temporary Directory (-t, --tmp-dir)

Temporary Directory to store temporary sensitive files, Make sure to delete it after the export.

Default: ./bitwarden_dump_attachments

#### Bitwarden CLI Executable (-e, --bw-executable)

Path to the Bitwarden CLI executable.

Default: bw

#### Debug (-d, --debug)

Enable Verbose Logging.

This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION.

**This will not delete the temporary directory after the export.**

Default: --no-debug

## Roadmap

- Make a cloud-ready option for bitwarden zero-touch backup, Upload to cloud storage.
- Restore back to bitwarden.

## Credits

[@ckabalan](https://github.com/ckabalan)
for [bitwarden-attachment-exporter](https://github.com/ckabalan/bitwarden-attachment-exporter)

## License

MIT
