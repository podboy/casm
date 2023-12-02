# coding:utf-8

from typing import Optional
from typing import Sequence

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import URL_PROG
from ...utils import __version__
from .system import add_cmd_system
from .systemd import add_cmd_systemd


@add_command("cman")
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd, add_cmd_system)
def run_cmd(cmds: commands) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="Manage pods, containers and images via podman",
        epilog=f"For more, please visit {URL_PROG}.")
