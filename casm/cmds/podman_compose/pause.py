# coding:utf-8

from typing import List

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.cmds.podman_compose.service import add_pos_services
from casm.cmds.podman_compose.service import filter_services
from casm.utils.assemble import assemble_file
from casm.utils.podman_compose import podman_compose_cmd


@CommandArgument("pause", help="Pause running services")
def add_cmd_pause(_arg: ArgParser):
    add_pos_services(_arg)


@CommandExecutor(add_cmd_pause)
def run_cmd_pause(cmds: Command) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = filter_services(assemble, cmds.args.services)
    return podman_compose_cmd(assemble.template_file).pause(services)
