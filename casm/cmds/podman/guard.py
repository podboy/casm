# coding:utf-8

from typing import List

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file
from ...utils import podman_container
from ..service import add_pos_services


@add_command("generate", help="Generate container guard crontab")
def add_cmd_guard_generate(_arg: argp):
    add_pos_services(_arg)


@run_command(add_cmd_guard_generate)
def run_cmd_guard_generate(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = cmds.args.services
    for service in assemble.template.services:
        cmds.logger.debug(f"{service.title}: {service.container_name}")
        if len(services) > 0 and service.title not in services:
            continue
        container_name = assemble.safe_substitute(service.container_name)
        cmds.logger.info(f"generate container {container_name} guard")
        podman_container(container_name).generate_guard_task()
    return 0


@add_command("destroy", help="Destroy container guard crontab")
def add_cmd_guard_destroy(_arg: argp):
    add_pos_services(_arg)


@run_command(add_cmd_guard_destroy)
def run_cmd_guard_destroy(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = cmds.args.services
    for service in assemble.template.services:
        cmds.logger.debug(f"{service.title}: {service.container_name}")
        if len(services) > 0 and service.title not in services:
            continue
        container_name = assemble.safe_substitute(service.container_name)
        cmds.logger.info(f"destroy container {container_name} guard")
        podman_container(container_name).destroy_guard_task()
    return 0


@add_command("guard", help="Manage containers guard")
def add_cmd_guard(_arg: argp):
    pass


@run_command(add_cmd_guard, add_cmd_guard_generate, add_cmd_guard_destroy)
def run_cmd_guard(cmds: commands) -> int:
    return 0
