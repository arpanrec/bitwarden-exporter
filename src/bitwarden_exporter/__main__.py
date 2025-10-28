"""
This module provides functionality to manage settings for the Bitwarden Exporter.
"""

from . import cli_global_options


def main() -> None:
    """
    Main entrypoint for the Bitwarden Exporter CLI.
    """
    cli_global_options.app()


if __name__ == "__main__":
    main()
