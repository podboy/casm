# coding:utf-8

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file
from ...utils import podman_compose_cmd


@add_command("exec", help="Execute a command in a running container")
def add_cmd_exec(_arg: argp):
    _arg.add_opt_on("-d", "--detach", help="Detached mode")
    _arg.add_opt_on("--privileged", help="Default is false")
    _arg.add_argument("-u", "--user", type=str, nargs=1, metavar="USER",
                      action="extend", help="Run as specified username or uid")
    _arg.add_opt_on("-T", help="Disable pseudo-tty allocation.")
    _arg.add_argument("--index", type=int, nargs=1, metavar="INDEX",
                      action="extend", help="Index of multiple instances")
    _arg.add_argument(dest="service", type=str, nargs=1, metavar="SERVICE",
                      action="extend", help="Service name")
    _arg.add_argument(dest="arguments", type=str, nargs="*", metavar="COMMAND",
                      action="extend", help="Command and its arguments")


@run_command(add_cmd_exec)
def run_cmd_exec(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    assert isinstance(cmds.args.service, list) and len(cmds.args.service) == 1
    service = cmds.args.service[0]
    user = cmds.args.user[0] if isinstance(cmds.args.user, list) else None
    index = cmds.args.index[0] if isinstance(cmds.args.index, list) else None
    cmd = podman_compose_cmd(assemble.template_file)
    return cmd.exec(service=service, arguments=cmds.args.arguments,
                    detach=cmds.args.detach, privileged=cmds.args.privileged,
                    user=user, T=cmds.args.T, index=index)
