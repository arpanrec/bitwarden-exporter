import typer

login_cli = typer.Typer()

@login_cli.command()
def login():
    """
    Login to Bitwarden CLI.
    """
    typer.echo("Logging in to Bitwarden CLI")
