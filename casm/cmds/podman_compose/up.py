# coding:utf-8

from typing import List

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command

from ...utils import assemble_file
from ...utils import podman_compose_cmd
from ..service import add_pos_services
from ..service import filter_services


@add_command("up", help="Create and start services")
def add_cmd_up(_arg: argp):
    add_pos_services(_arg)


@run_command(add_cmd_up)
def run_cmd_up(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = filter_services(assemble, cmds.args.services)
    return podman_compose_cmd(assemble.template_file).up(services, detach=True)
