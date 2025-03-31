# coding:utf-8

from typing import List

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from ...utils import assemble_file
from ...utils import podman_compose_cmd
from ..service import add_pos_services
from ..service import filter_services


@CommandArgument("restart", help="Restart services")
def add_cmd_restart(_arg: ArgParser):
    add_pos_services(_arg)


@CommandExecutor(add_cmd_restart)
def run_cmd_restart(cmds: Command) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = filter_services(assemble, cmds.args.services)
    return podman_compose_cmd(assemble.template_file).restart(services)
