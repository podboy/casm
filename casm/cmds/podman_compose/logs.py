# coding:utf-8

from typing import List

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file
from ...utils import podman_compose_cmd
from ..service import add_pos_services
from ..service import filter_services


@add_command("logs", help="Show logs from containers")
def add_cmd_logs(_arg: argp):
    _arg.add_opt_on("--follow", help="Follow log output, default is false")
    _arg.add_argument("--tail", type=int, nargs=1, metavar="LINES",
                      help="Number of lines from the end for each container")
    add_pos_services(_arg)


@run_command(add_cmd_logs)
def run_cmd_logs(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = filter_services(assemble, cmds.args.services)
    tail = cmds.args.tail[0] if isinstance(cmds.args.tail, list) else None
    cmd = podman_compose_cmd(assemble.template_file)
    return cmd.logs(services, follow=cmds.args.follow, tail=tail)
