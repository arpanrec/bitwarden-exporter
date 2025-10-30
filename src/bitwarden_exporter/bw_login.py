import json

from .bw_cli import bw_exec
from .bw_models import BWCurrentStatus, BWStatus


def bw_login():
    bw_current_status = BWStatus(**json.loads(bw_exec(["status"], is_raw=False)))
    if bw_current_status.status != BWCurrentStatus.UNAUTHENTICATED:
        return

    bw_exec(["login"], is_raw=False, capture_output=False)
