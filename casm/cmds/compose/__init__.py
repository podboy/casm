# coding:utf-8

from typing import Optional
from typing import Sequence

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import URL_PROG
from ...utils import __prog_compose__
from ...utils import __version__
from .assemble import add_cmd_assemble


@add_command(__prog_compose__)
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd, add_cmd_assemble)
def run_cmd(cmds: commands) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="assemble compose",
        epilog=f"For more, please visit {URL_PROG}.")
