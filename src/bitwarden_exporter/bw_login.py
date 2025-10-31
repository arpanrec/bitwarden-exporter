import logging
from enum import Enum
from typing import Optional

from .bw_cli import bw_exec
from .bw_models import BWCurrentStatus
from .bw_status import reset_bw_status
from .exceptions import BitwardenException
from .global_settings import GLOBAL_SETTINGS
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

    if not GLOBAL_SETTINGS.bw_status:
        reset_bw_status()

    if GLOBAL_SETTINGS.bw_status.status != BWCurrentStatus.UNAUTHENTICATED:
        LOGGER.warning("Already authenticated")
        return

    match login_type:
        case BWLoginType.INTERACTIVE:
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
    email: Optional[str] = None,
    password: Optional[str] = None,
    code_type: Optional[BWInteractiveCodeType] = None,
    code: Optional[str] = None,
) -> None:
    if email and not password:
        raise BitwardenException("Email provided but no password provided")

    if password and not email:
        raise BitwardenException("Password provided but no email provided")

    if code_type and not code:
        raise BitwardenException("Code type provided but no code provided")

    if code and not code_type:
        raise BitwardenException("Code provided but no code type provided")

    login_cmd = ["login"]

    if email and password:
        email = resolve_secret(email)
        password = resolve_secret(password)
        login_cmd.extend([email, password])

    if code_type and code:
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

        if cli_method_int is not None:
            login_cmd.extend(["--method", str(cli_method_int), "--code", code])

    capture_output: bool = (
        (email is not None) and (password is not None) and (code_type is not None) and (code is not None)
    )

    LOGGER.warning("capture_output %s", capture_output)

    bw_session = bw_exec(login_cmd, capture_output=capture_output)

    if bw_session:
        LOGGER.warning("Setting BW_SESSION")
        GLOBAL_SETTINGS.bw_session = bw_session

    reset_bw_status()
