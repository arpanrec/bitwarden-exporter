"""
This module provides functionality to manage settings for the Bitwarden Exporter.
"""

from importlib.metadata import PackageNotFoundError, version

import typer

# uv run typer src/bitwarden_exporter/__main__.py utils docs --output docs/cli.md
# Relative imports will not work when running as a script to generate docs.
from . import login
from .exporter_cli import exporter_cli

APPLICATION_PACKAGE_NAME = "bitwarden-exporter"

APPLICATION_NAME_ASCII = r"""
 ____  _ _                         _
| __ )(_) |___      ____ _ _ __ __| | ___ _ __
|  _ \| | __\ \ /\ / / _` | '__/ _` |/ _ \ '_ \
| |_) | | |_ \ V  V / (_| | | | (_| |  __/ | | |
|____/|_|\__| \_/\_/ \__,_|_|_ \__,_|\___|_| |_|
| ____|_  ___ __   ___  _ __| |_ ___ _ __
|  _| \ \/ / '_ \ / _ \| '__| __/ _ \ '__|
| |___ >  <| |_) | (_) | |  | ||  __/ |
|_____/_/\_\ .__/ \___/|_|   \__\___|_|
           |_|
"""

app = typer.Typer(
    name=APPLICATION_PACKAGE_NAME,
    help="Bitwarden Exporter CLI",
)

app.pretty_exceptions_enable = True

app.add_typer(login.login_cli)
app.add_typer(exporter_cli)


def version_callback(value: bool) -> None:
    """
    Show the application's version and exit.
    """
    if value:
        try:
            uv_version = version(APPLICATION_PACKAGE_NAME)
            print(f"{APPLICATION_NAME_ASCII}\nv{uv_version}")
            raise typer.Exit()
        except PackageNotFoundError as e:
            raise SystemExit(f"Package {APPLICATION_PACKAGE_NAME} not found") from e


# pylint: disable=missing-function-docstring
@app.callback()
def version_registered(
    # pylint: disable=unused-argument
    app_version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the application's version and exit.",
    )
) -> None: ...


def main() -> None:
    """
    Main entrypoint for the Bitwarden Exporter CLI.
    """
    app()


if __name__ == "__main__":
    main()
