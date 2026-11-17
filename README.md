# Bitwarden Exporter

Python Wrapper for [Password Manager CLI](https://bitwarden.com/help/cli/) for exporting bitwarden vaults to KeePass.

Documentation: <https://bitwarden-exporter.arpanrec.com/>

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
    - Passkeys (Compatible with KeePassXC passkeys, see [Passkeys](https://bitwarden-exporter.arpanrec.com/#passkeys))
- **Preserves vault structure**
    - Collection and Folder hierarchy is preserved as Keepass groups.
- Built-in JSON snapshot of vault data for auditing.
- Configurable CLI with options for duplicates handling, custom temp directory, debug logging, and Bitwarden CLI path.

![Bitwarden Web](./docs/Screenshot_compare_base.png 'Bitwarden Web')

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
BW_SESSION=<session token> uvx bitwarden-exporter --help
```

Run it from [source](https://github.com/arpanrec/bitwarden-exporter)

```bash
BW_SESSION=<session token> uvx git+https://github.com/arpanrec/bitwarden-exporter.git@main --help
```

Install with [pipx](https://github.com/pypa/pipx) from [PyPI](https://pypi.org/project/bitwarden-exporter/)

```bash
BW_SESSION=<session token> pipx install bitwarden-exporter
```

## [CLI Usage](./docs/cli.md)

Run `bitwarden-exporter --help` to see all available options.

## Development

A pre-commit hook in `.git-hooks/` scans staged changes for secrets with
[betterleaks](https://github.com/betterleaks/betterleaks). Install betterleaks, then enable the hook once per clone:

```bash
git config core.hooksPath .git-hooks
```

The documentation site is built with [Zensical](https://zensical.org/) from `docs/` and `zensical.toml`. Preview it
locally, or build the static site into `site/`:

```bash
uv run --only-group docs zensical serve
uv run --only-group docs zensical build --clean
```

Pushes to `main` that touch the docs publish the site to GitHub Pages.

## Credits

[@ckabalan](https://github.com/ckabalan)
for [bitwarden-attachment-exporter](https://github.com/ckabalan/bitwarden-attachment-exporter)

## License

MIT
