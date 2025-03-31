# coding:utf-8

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.utils.assemble import assemble_file
from casm.utils.podman_compose import podman_compose_cmd


@CommandArgument("exec", help="Execute a command in a running container")
def add_cmd_exec(_arg: ArgParser):
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


@CommandExecutor(add_cmd_exec)
def run_cmd_exec(cmds: Command) -> int:
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
