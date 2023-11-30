# coding:utf-8

from typing import List

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file
from ...utils import podman_compose_unpause
from .service import add_opt_services
from .service import filter_services


@add_command("unpause", help="Unpause running services")
def add_cmd_unpause(_arg: argp):
    add_opt_services(_arg)


@run_command(add_cmd_unpause)
def run_cmd_unpause(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = filter_services(assemble, cmds.args.services)
    return podman_compose_unpause(assemble.compose_file, *services)
