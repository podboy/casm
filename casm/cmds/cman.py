# coding:utf-8

from typing import Optional
from typing import Sequence

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.attribute import __urlhome__
from casm.attribute import __version__
from casm.cmds.podman.container import add_cmd_container
from casm.cmds.podman.guard import add_cmd_guard
from casm.cmds.podman.system import add_cmd_system


@CommandArgument("cman")
def add_cmd(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd, add_cmd_container, add_cmd_guard, add_cmd_system)
def run_cmd(cmds: Command) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="Manage pods, containers and images via podman",
        epilog=f"For more, please visit {__urlhome__}.")
