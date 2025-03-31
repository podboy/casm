# coding:utf-8

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.utils.podman import podman_containers_guard_service


@CommandArgument("enable", help="Enable containers guard service")
def add_cmd_guard_enable(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_guard_enable)
def run_cmd_guard_enable(cmds: Command) -> int:
    return podman_containers_guard_service.enable()


@CommandArgument("disable", help="Disable containers guard service")
def add_cmd_guard_disable(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_guard_disable)
def run_cmd_guard_disable(cmds: Command) -> int:
    return podman_containers_guard_service.disable()


@CommandArgument("guard", help="Manage containers guard")
def add_cmd_guard(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_guard, add_cmd_guard_enable, add_cmd_guard_disable)
def run_cmd_guard(cmds: Command) -> int:
    return 0
