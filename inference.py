"""取り込み済み全 SPAT データに対する推論処理をサーバーに依頼します。"""
# pyright: basic
import logging
import logging.handlers
import shlex
import sys
from getpass import getuser
from typing import Optional

import click
from fastapi.encoders import jsonable_encoder

from .. import LOG_FORMAT_FOR_CONSOLE
from .._logging import LOG_LEVEL
from ..schemas.learning import StartInferenceRequest
from . import DEFAULT_HOSTNAME, CommandError
from .utils import request

_logger = logging.getLogger("pyfdv.commands.inference")
_help_hostname = f"装置異常監視サーバーのホスト名を指定します。指定を省略すると {DEFAULT_HOSTNAME} を使用します。"


@click.command()
@click.option("-h", "--hostname", help=_help_hostname)
def inference(hostname: Optional[str]) -> None:
    """取り込み済み SPAT ファイルに対する推論処理をサーバーに依頼します。"""
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT_FOR_CONSOLE)
    _logger.info("Starting inference command with:")
    _logger.info("    user=%r", getuser())
    _logger.info("    cmdline=[%s]", shlex.join(sys.argv))

    try:
        if hostname is None:
            hostname = DEFAULT_HOSTNAME

        # 用途指定を行わずに（現行踏襲での）推論タスクの開始を依頼
        url = f"{hostname}/api/v1/inference/start"
        data = StartInferenceRequest(spat_flags=[], inherit_previous_scorer=True)
        data = jsonable_encoder(data)
        resp = request("post", url, json=data)

        if resp.ok:
            _logger.info("Successfully requested to start inference task.")
        else:
            _logger.error("Failed on requesting to start inference task.")
            raise CommandError("inference command failed.")
    except Exception as exc:
        _logger.exception("inference command failed:")
        raise CommandError("inference command failed.") from exc


if __name__ == "__main__":
    inference()
