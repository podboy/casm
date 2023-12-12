# coding:utf-8

import os
from typing import List

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file
from ..service import add_pos_services
from ..service import filter_services


def dump(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)

    output_file: str = assemble.template_file
    if isinstance(cmds.args.output, list):
        output_file = os.path.abspath(cmds.args.output[0])

    assert isinstance(output_file, str)
    cmds.logger.info(f"dump '{output_file}'")
    cmds.logger.debug(assemble.template.dump())
    assemble.dump_template(output_file)
    return 0


@add_command("services", help="Modify services")
def add_cmd_services(_arg: argp):
    _arg.add_opt_on("--mount-localtime", help="Mount host localtime")
    _arg.add_opt_on("--privileged", help="Give extended privileges")
    _arg.add_opt_on("--systemd", help="Control via systemctl")
    add_pos_services(_arg)


@run_command(add_cmd_services)
def run_cmd_services(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    services: List[str] = filter_services(assemble, cmds.args.services)
    for service in assemble.template.services:
        if len(services) > 0 and service.title not in services:
            continue
        # Mount host localtime to container
        if cmds.args.mount_localtime:
            service.mount("/etc/localtime", "/etc/localtime", True)
        # Restart via systemd
        if cmds.args.systemd and service.restart != "no":
            service.restart = "no"
        # Give extended privileges to this container
        service.privileged = cmds.args.privileged
    return dump(cmds)


@add_command("template", help="Modify template file")
def add_cmd_template(_arg: argp):
    _arg.add_argument("--output", type=str, nargs=1, metavar="PATH",
                      help="Specify output file")


@run_command(add_cmd_template, add_cmd_services)
def run_cmd_template(cmds: commands) -> int:
    return 0
