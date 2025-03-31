# coding:utf-8

from typing import List

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.cmds.service import add_pos_services
from casm.cmds.service import filter_services
from casm.utils import assemble_file
from casm.utils import podman_compose_cmd


@CommandArgument("start", help="Start services")
def add_cmd_start(_arg: ArgParser):
    add_pos_services(_arg)


@CommandExecutor(add_cmd_start)
def run_cmd_start(cmds: Command) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = filter_services(assemble, cmds.args.services)
    return podman_compose_cmd(assemble.template_file).start(services)
