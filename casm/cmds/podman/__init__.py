# coding:utf-8

from typing import Optional
from typing import Sequence

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command

from ...utils import __urlhome__
from ...utils import __version__
from .container import add_cmd_container
from .guard import add_cmd_guard  # noqa:F401
from .system import add_cmd_system
from .systemd import add_cmd_systemd  # noqa:F401


@add_command("cman")
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd, add_cmd_container, add_cmd_system)
def run_cmd(cmds: commands) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="Manage pods, containers and images via podman",
        epilog=f"For more, please visit {__urlhome__}.")
