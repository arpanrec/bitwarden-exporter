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
    - Passkeys (Compatible with KeePassXC passkeys, see [Passkeys](#passkeys))
- **Preserves vault structure**
    - Collection and Folder hierarchy is preserved as Keepass groups.
- Built-in JSON snapshot of vault data for auditing.
- Configurable CLI with options for duplicates handling, custom temp directory, debug logging, and Bitwarden CLI path.

![Bitwarden Web](Screenshot_compare_base.png 'Bitwarden Web')

More in [Screenshots](screenshots.md).

## Passkeys

Bitwarden stores passkeys as FIDO2 credentials on a login item. The exporter writes the first one into the KeePass
entry in the format [KeePassXC](https://keepassxc.org/) 2.7.7 and later reads, so KeePassXC can sign in with it
through its browser integration. The entry gets these attributes and the `Passkey` tag:

- `KPEX_PASSKEY_USERNAME`, `KPEX_PASSKEY_RELYING_PARTY`, `KPEX_PASSKEY_FLAG_BE` and `KPEX_PASSKEY_FLAG_BS`
- `KPEX_PASSKEY_CREDENTIAL_ID`, `KPEX_PASSKEY_PRIVATE_KEY_PEM` and `KPEX_PASSKEY_USER_HANDLE`, stored as protected
  values

Every credential on the item is also saved as JSON in the protected `Fido2Credentials` attribute.

KeePassXC holds one passkey per entry. When an item has more than one, only the first becomes a passkey, and the rest
are kept in the `Fido2Credentials` JSON.

If a credential has a malformed credential ID, private key or user handle, the entry gets no passkey attributes and a
warning is logged. The item and its `Fido2Credentials` JSON are still exported, and the export carries on.

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
