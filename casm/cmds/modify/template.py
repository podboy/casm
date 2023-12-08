# coding:utf-8

import os

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file


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
    _arg.add_opt_on("--systemd", help="Control via systemctl")


@run_command(add_cmd_services)
def run_cmd_services(cmds: commands) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    for servive in assemble.template.services:
        # mount host localtime to container
        if cmds.args.mount_localtime:
            servive.mount("/etc/localtime", "/etc/localtime", True)
        # restart via systemd
        if cmds.args.systemd and servive.restart != "no":
            servive.restart = "no"
    return dump(cmds)


@add_command("template", help="Modify template file")
def add_cmd_template(_arg: argp):
    _arg.add_argument("--output", type=str, nargs=1, metavar="PATH",
                      help="Specify output file")


@run_command(add_cmd_template, add_cmd_services)
def run_cmd_template(cmds: commands) -> int:
    return 0
