# coding:utf-8

from typing import List

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from ...utils import assemble_file
from ...utils import podman_container
from ..service import add_pos_services


@CommandArgument("generate", help="Generate container guard crontab")
def add_cmd_guard_generate(_arg: ArgParser):
    add_pos_services(_arg)


@CommandExecutor(add_cmd_guard_generate)
def run_cmd_guard_generate(cmds: Command) -> int:
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


@CommandArgument("destroy", help="Destroy container guard crontab")
def add_cmd_guard_destroy(_arg: ArgParser):
    add_pos_services(_arg)


@CommandExecutor(add_cmd_guard_destroy)
def run_cmd_guard_destroy(cmds: Command) -> int:
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


@CommandArgument("guard", help="Manage containers guard")
def add_cmd_guard(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_guard, add_cmd_guard_generate, add_cmd_guard_destroy)
def run_cmd_guard(cmds: Command) -> int:
    return 0
