# coding:utf-8

from logging import DEBUG
from typing import List

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.cmds.podman_compose.service import add_pos_services
from casm.cmds.podman_compose.service import filter_services
from casm.utils.assemble import assemble_file
from casm.utils.podman_compose import podman_compose_cmd


@CommandArgument("down", help="Tear down services")
def add_cmd_down(_arg: ArgParser):
    add_pos_services(_arg)


@CommandExecutor(add_cmd_down)
def run_cmd_down(cmds: Command) -> int:
    debug_mode: bool = cmds.logger.level <= DEBUG
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file), f"TypeError: {type(assemble)}"
    pcommand: podman_compose_cmd = podman_compose_cmd(assemble.template_file, debug=debug_mode)  # noqa:E501
    services: List[str] = filter_services(assemble, cmds.args.services)
    return pcommand.down(services)
