import json
from enum import Enum
from typing import Optional

from .bw_cli import bw_exec
from .bw_models import BWCurrentStatus, BWStatus
from .exceptions import BitwardenException
from .utils import resolve_secret


class BWLoginType(str, Enum):
    """
    Bitwarden Login Type Enum
    """

    INTERACTIVE = "interactive"
    APIKEY = "apikey"
    SSO = "sso"


class BWInteractiveCodeType(str, Enum):
    """
    Bitwarden Interactive Code Type Enum
    """

    Authenticator = "authenticator"
    Email = "email"
    YubiKey = "yubikey"


def bw_login(
    login_type: BWLoginType = BWLoginType.INTERACTIVE,
    interactive_email: Optional[str] = None,
    interactive_password: Optional[str] = None,
    interactive_code_type: Optional[BWInteractiveCodeType] = None,
    interactive_code: Optional[str] = None,
):
    bw_current_status = BWStatus(**json.loads(bw_exec(["status"], is_raw=False)))
    if bw_current_status.status != BWCurrentStatus.UNAUTHENTICATED:
        return


def __bw_interactive_login(
    email: Optional[str] = None,
    password: Optional[str] = None,
    code_type: Optional[BWInteractiveCodeType] = None,
    code: Optional[str] = None,
):
    if email and not password:
        raise BitwardenException("Email provided but no password provided")

    if code_type and not code:
        raise BitwardenException("Code type provided but no code provided")

    login_cmd = ["login"]

    if email and password :
        email = resolve_secret(email)
        password = resolve_secret(password)
        login_cmd.extend([email, password])

    if