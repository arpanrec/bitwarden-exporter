import json

from .bw_cli import bw_exec
from .bw_models import BWStatus
from .global_settings import GLOBAL_SETTINGS


def reset_bw_status() -> None:
    """
    Reset the BWStatus object.
    """
    GLOBAL_SETTINGS.bw_status = BWStatus(**json.loads(bw_exec(["status"])))
