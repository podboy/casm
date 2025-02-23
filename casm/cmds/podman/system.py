# coding:utf-8

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command

from ...utils import podman_cmd


@add_command("prune", help="Remove unused data")
def add_cmd_prune(_arg: argp):
    pass

@run_command(add_cmd_prune)
def run_cmd_prune(cmds: commands) -> int:
    return podman_cmd.system_prune()


@add_command("system", help="Manage podman")
def add_cmd_system(_arg: argp):
    pass


@run_command(add_cmd_system, add_cmd_prune)
def run_cmd_system(cmds: commands) -> int:
    return 0
