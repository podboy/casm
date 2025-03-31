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


@CommandArgument("logs", help="Show logs from containers")
def add_cmd_logs(_arg: ArgParser):
    _arg.add_opt_on("--follow", help="Follow log output, default is false")
    _arg.add_argument("--tail", type=int, nargs=1, metavar="LINES",
                      help="Number of lines from the end for each container")
    add_pos_services(_arg)


@CommandExecutor(add_cmd_logs)
def run_cmd_logs(cmds: Command) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = filter_services(assemble, cmds.args.services)
    tail = cmds.args.tail[0] if isinstance(cmds.args.tail, list) else None
    cmd = podman_compose_cmd(assemble.template_file)
    return cmd.logs(services, follow=cmds.args.follow, tail=tail)
