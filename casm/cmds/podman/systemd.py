# coding:utf-8

from typing import List

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file
from ...utils import podman_cmd
from ..service import add_pos_services


@add_command("enable", help="Enable systemd for containers")
def add_cmd_enable(_arg: argp):
    add_pos_services(_arg)


@run_command(add_cmd_enable)
def run_cmd_enable(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = cmds.args.services
    for service in assemble.template.services:
        cmds.logger.debug(f"{service.title}: {service.container_name}")
        if len(services) > 0 and service.title not in services:
            continue
        container_name = assemble.safe_substitute(service.container_name)
        cmds.logger.info(f"enable container {container_name}")
        podman_cmd.enable_service(container_name)
    return 0


@add_command("disable", help="Disable systemd for containers")
def add_cmd_disable(_arg: argp):
    add_pos_services(_arg)


@run_command(add_cmd_disable)
def run_cmd_disable(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = cmds.args.services
    for service in assemble.template.services:
        cmds.logger.debug(f"{service.title}: {service.container_name}")
        if len(services) > 0 and service.title not in services:
            continue
        container_name = assemble.safe_substitute(service.container_name)
        cmds.logger.info(f"disable container {container_name}")
        podman_cmd.disable_service(container_name)
    return 0


@add_command("systemd", help="Manage systemd units")
def add_cmd_systemd(_arg: argp):
    pass


@run_command(add_cmd_systemd, add_cmd_enable, add_cmd_disable)
def run_cmd_systemd(cmds: commands) -> int:
    return 0
