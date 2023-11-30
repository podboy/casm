# coding:utf-8

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file


def add_opt_services(_arg: argp):
    _arg.add_argument(dest="services", type=str, nargs="*", metavar="SERVICE",
                      action="extend", help="Specify services, default ALL")


@add_command("services", help="List all services")
def add_cmd_services(_arg: argp):
    mgrp = _arg.add_mutually_exclusive_group()
    mgrp.add_argument("--service-name", action="store_true",
                      help="Only output service_name")
    mgrp.add_argument("--container-name", action="store_true",
                      help="Only output container_name")


@run_command(add_cmd_services)
def run_cmd_services(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    for service in assemble.compose.services:
        if cmds.args.service_name:
            cmds.stdout(service.title)
            continue
        if cmds.args.container_name:
            cmds.stdout(service.container_name)
            continue
        cmds.stdout(f"{service.title}: {service.container_name}")
    return 0
