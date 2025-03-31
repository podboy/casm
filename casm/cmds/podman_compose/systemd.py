# coding:utf-8

from typing import List

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.cmds.podman_compose.service import add_pos_services
from casm.utils.assemble import assemble_file
from casm.utils.podman import podman_container


@CommandArgument("enable", help="Enable systemd unit for containers")
def add_cmd_enable(_arg: ArgParser):
    _arg.add_argument("--restart-policy", dest="restart_policy",
                      type=str, nargs=1, metavar="STR", default=["on-failure"],
                      help='Systemd restart-policy (default "on-failure")')
    add_pos_services(_arg)


@CommandExecutor(add_cmd_enable)
def run_cmd_enable(cmds: Command) -> int:
    restart_policy: str = cmds.args.restart_policy[0]
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = cmds.args.services
    for service in assemble.template.services:
        cmds.logger.debug(f"{service.title}: {service.container_name}")
        if len(services) > 0 and service.title not in services:
            continue
        container_name = assemble.safe_substitute(service.container_name)
        cmds.logger.info(f"enable container {container_name}")
        podman_container(container_name).enable_service(
            restart_policy=restart_policy)
    return 0


@CommandArgument("disable", help="Disable systemd unit for containers")
def add_cmd_disable(_arg: ArgParser):
    add_pos_services(_arg)


@CommandExecutor(add_cmd_disable)
def run_cmd_disable(cmds: Command) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = cmds.args.services
    for service in assemble.template.services:
        cmds.logger.debug(f"{service.title}: {service.container_name}")
        if len(services) > 0 and service.title not in services:
            continue
        container_name = assemble.safe_substitute(service.container_name)
        cmds.logger.info(f"disable container {container_name}")
        podman_container(container_name).disable_service()
    return 0


@CommandArgument("systemd", help="Manage systemd units")
def add_cmd_systemd(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_systemd, add_cmd_enable, add_cmd_disable)
def run_cmd_systemd(cmds: Command) -> int:
    return 0
