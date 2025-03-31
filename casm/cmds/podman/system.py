# coding:utf-8

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.utils.podman import podman_cmd


@CommandArgument("prune", help="Remove unused data")
def add_cmd_prune(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_prune)
def run_cmd_prune(cmds: Command) -> int:
    return podman_cmd.system_prune()


@CommandArgument("system", help="Manage podman")
def add_cmd_system(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_system, add_cmd_prune)
def run_cmd_system(cmds: Command) -> int:
    return 0
