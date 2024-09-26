# coding:utf-8

from typing import Iterable

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

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
    containers: Iterable[str] = cmds.args.containers or podman_container.list(all=True)  # noqa:E501
    for container_name in containers:
        cmds.logger.info(f"guard container {container_name}")
        podman_container(container_name).guard()
    return 0


@add_command("container", help="Manage podman containers")
def add_cmd_container(_arg: argp):
    pass


@run_command(add_cmd_container, add_cmd_container_guard)
def run_cmd_container(cmds: commands) -> int:
    return 0
