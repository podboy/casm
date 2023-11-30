# coding:utf-8

from typing import List

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file
from ...utils import compose_service
from ...utils import disable_service
from ...utils import enable_service


def add_opt_services(_arg: argp):
    _arg.add_argument(dest="services", type=str, nargs="*", metavar="SERVICE",
                      action="extend", help="Specify services, default ALL")


@add_command("enable", help="enable systemd for containers")
def add_cmd_enable(_arg: argp):
    add_opt_services(_arg)


@run_command(add_cmd_enable)
def run_cmd_enable(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[compose_service] = cmds.args.services
    assert isinstance(services, list)
    for service in assemble.compose.services:
        cmds.logger.debug(f"{service.title}: {service.container_name}")
        if service.title not in services:
            continue
        container_name = assemble.safe_substitute(service.container_name)
        cmds.logger.info(f"enable container {container_name}")
        enable_service(container_name)
    return 0


@add_command("disable", help="disable systemd for containers")
def add_cmd_disable(_arg: argp):
    add_opt_services(_arg)


@run_command(add_cmd_disable)
def run_cmd_disable(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[compose_service] = cmds.args.services
    assert isinstance(services, list)
    for service in assemble.compose.services:
        cmds.logger.debug(f"{service.title}: {service.container_name}")
        if service.title not in services:
            continue
        container_name = assemble.safe_substitute(service.container_name)
        cmds.logger.info(f"disable container {container_name}")
        disable_service(container_name)
    return 0
