"""Constants for the application."""

CLI_SESSION_TOKEN_HELP = """
Direct value: `--session-token "my-secret-password"`
From a file: `--session-token file:secret.txt`
From environment: `--session-token env:SECRET_PASSWORD`
"""

CLI_MASTER_PASSWORD_HELP = """
Direct value: `--master-password "my-secret-password"`
From a file: `--master-password file:secret.txt`
From environment: `--master-password env:SECRET_PASSWORD`
"""

CLI_EXPORT_PASSWORD_HELP = """
Direct value: `--export-password "my-secret-password"`
From a file: `--export-password file:secret.txt`
From environment: `--export-password env:SECRET_PASSWORD`
From vault (JMESPath expression): `--export-password "jmespath:[?id=='xx-xx-xx-xxx-xxx'].fields[] | [?name=='export-password'].value"`
"""

CLI_DEBUG_HELP = """
Enable verbose logging, This will print debug logs, THAT MAY CONTAIN SENSITIVE INFORMATION, This will not delete the
temporary directory after the export, Default: --no-debug
"""

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
