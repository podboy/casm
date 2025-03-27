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
    def guard_container(container: podman_container) -> int:
        cmds.logger.info("guard container %s begin", container.container_name)
        exit_code: int = container.guard()
        cmds.logger.info("guard container %s end, exit-code: %d",
                         container.container_name, exit_code)
        return exit_code

    container_names: Iterable[str] = cmds.args.containers or podman_container.list(all=True)  # noqa:E501
    containers: List[podman_container] = [podman_container(name) for name in container_names]  # noqa:E501
    for container in containers:
        if (exit_code := guard_container(container)) != 0:
            cmds.logger.error("failed to guard container %s",
                              container.container_name)
            return exit_code
    return 0


@add_command("container", help="Manage podman containers")
def add_cmd_container(_arg: argp):
    pass


@run_command(add_cmd_container, add_cmd_container_guard)
def run_cmd_container(cmds: commands) -> int:
    return 0
