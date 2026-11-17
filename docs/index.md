# Bitwarden Exporter

A Python wrapper around the [Bitwarden Password Manager CLI](https://bitwarden.com/help/cli/) that exports Bitwarden
vaults to KeePass.

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

![Bitwarden Web](Screenshot_compare_base.png 'Bitwarden Web')

More in [Screenshots](screenshots.md).

## Prerequisites

- [Bitwarden CLI](https://bitwarden.com/help/article/cli/#download-and-install)
- [Python](https://www.python.org/) 3.13 or newer, with one of:
    - [uvx](https://docs.astral.sh/uv/guides/tools/)
    - [pipx](https://github.com/pypa/pipx)
    - a virtual environment

## Installation

Run it with [uvx](https://docs.astral.sh/uv/guides/tools/) from [PyPI](https://pypi.org/project/bitwarden-exporter/)
(recommended):

```bash
BW_SESSION=<session token> uvx bitwarden-exporter --help
```

Run it from [source](https://github.com/arpanrec/bitwarden-exporter):

```bash
BW_SESSION=<session token> uvx git+https://github.com/arpanrec/bitwarden-exporter.git@main --help
```

Install it with [pipx](https://github.com/pypa/pipx) from [PyPI](https://pypi.org/project/bitwarden-exporter/):

```bash
BW_SESSION=<session token> pipx install bitwarden-exporter
```

## Usage

Run `bitwarden-exporter --help` to see all options, or read the [CLI reference](cli.md).

## Credits

[@ckabalan](https://github.com/ckabalan) for
[bitwarden-attachment-exporter](https://github.com/ckabalan/bitwarden-attachment-exporter).

## License

[MIT](https://github.com/arpanrec/bitwarden-exporter/blob/main/LICENSE)
