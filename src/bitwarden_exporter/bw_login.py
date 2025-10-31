import json
import logging
from enum import Enum
from typing import Optional

from . import BITWARDEN_EXPORTER_GLOBAL_SETTINGS
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


LOGGER = logging.getLogger(__name__)


def bw_login(
    login_type: BWLoginType = BWLoginType.INTERACTIVE,
    interactive_email: Optional[str] = None,
    interactive_password: Optional[str] = None,
    interactive_code_type: Optional[BWInteractiveCodeType] = None,
    interactive_code: Optional[str] = None,
) -> None:
    """
    bitwarden login
    """
    bw_current_status = BWStatus(**json.loads(bw_exec(["status"], is_raw=False)))
    if bw_current_status.status != BWCurrentStatus.UNAUTHENTICATED:
        LOGGER.warning("Already authenticated")
        return

    match login_type:
        case BWLoginType.INTERACTIVE:
            if not interactive_email or not interactive_password or not interactive_code_type or not interactive_code:
                raise BitwardenException("Interactive login requires email, password, code type, and code")
            __bw_interactive_login(
                email=interactive_email,
                password=interactive_password,
                code_type=interactive_code_type,
                code=interactive_code,
            )
        case BWLoginType.APIKEY:
            raise BitwardenException("API Key login not yet implemented")
        case BWLoginType.SSO:
            raise BitwardenException("SSO login not yet implemented")
        case _:
            raise BitwardenException(f"Unknown login type: {login_type}")


def __bw_interactive_login(
    email: str,
    password: str,
    code_type: BWInteractiveCodeType,
    code: str,
) -> None:
    login_cmd = ["login"]

    email = resolve_secret(email)
    password = resolve_secret(password)
    code = resolve_secret(code)
    login_cmd.extend([email, password])

    cli_method_int: Optional[int] = None

    match code_type:
        case BWInteractiveCodeType.Authenticator:
            cli_method_int = 0
        case BWInteractiveCodeType.Email:
            cli_method_int = 1
        case BWInteractiveCodeType.YubiKey:
            cli_method_int = 2
        case _:
            raise BitwardenException(f"Unknown code type: {code_type}")

    if cli_method_int is None:
        raise BitwardenException("Code type is not set")

    login_cmd.extend(["--method", str(cli_method_int), "--code", code])

    BITWARDEN_EXPORTER_GLOBAL_SETTINGS.bw_session = bw_exec(login_cmd, capture_output=True)
    LOGGER.warning("Setting BW_SESSION")
