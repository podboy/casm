# coding:utf-8

from typing import Iterable
from typing import List

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command

from ...utils import podman_container


def add_pos_containers(_arg: argp):
    _arg.add_argument(dest="containers", type=str, nargs="*",
                      metavar="CONTAINER", action="extend",
                      choices=list(podman_container.list(all=True)) + [[]],
                      help="Specify containers, default ALL")


@add_command("guard", help="Guard podman container")
def add_cmd_container_guard(_arg: argp):
    add_pos_containers(_arg)


@run_command(add_cmd_container_guard)
def run_cmd_container_guard(cmds: commands) -> int:
    container_names: Iterable[str] = cmds.args.containers or podman_container.list(all=True)  # noqa:E501
    containers: List[podman_container] = [podman_container(name) for name in container_names]  # noqa:E501
    for container in containers:
        cmds.logger.info(f"guard container {container.container_name}")
        exit_code: int = container.guard()
        if exit_code != 0:
            cmds.logger.error(f"failed to guard container {container.container_name} (exit-code: {exit_code})")  # noqa:E501
            return exit_code
    return 0


@add_command("container", help="Manage podman containers")
def add_cmd_container(_arg: argp):
    pass


@run_command(add_cmd_container, add_cmd_container_guard)
def run_cmd_container(cmds: commands) -> int:
    return 0
