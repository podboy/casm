# coding:utf-8

from typing import List

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file
from ...utils import podman_cmd
from ..service import add_pos_services


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
