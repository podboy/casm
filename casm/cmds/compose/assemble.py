# coding:utf-8

from errno import ENOENT
import os
from typing import Optional

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file

DEF_INSTANCE = "assemble.yml"


def add_opt_instances(_arg: argp):
    _arg.add_argument(dest="instance", type=str, nargs="?", metavar="INSTANC",
                      help=f"YAML format config file, default {DEF_INSTANCE}")


@add_command("assemble")
def add_cmd_assemble(_arg: argp):
    _arg.add_opt_on("--mount-timezone")
    _arg.add_opt_on("--mount-localtime")
    _arg.add_argument("--template", type=str, nargs=1, metavar="TEMPLATE",
                      help="Specify an alternate template file")
    _arg.add_argument("--compose", type=str, nargs=1, metavar="COMPOSE",
                      help="Specify an alternate compose file")
    add_opt_instances(_arg)


@run_command(add_cmd_assemble)
def run_cmd_assemble(cmds: commands) -> int:
    instance: Optional[str] = cmds.args.instance
    if instance is None:
        instance = DEF_INSTANCE
    assert isinstance(instance, str)

    filepath: str = os.path.abspath(instance)
    if not os.path.isfile(filepath):
        cmds.logger.error(f"No such file '{filepath}'")
        return ENOENT

    template_file: Optional[str] = None
    if isinstance(cmds.args.template, list):
        template_file = os.path.abspath(cmds.args.template[0])
    assert isinstance(template_file, str) or template_file is None

    compose_file: Optional[str] = None
    if isinstance(cmds.args.compose, list):
        compose_file = os.path.abspath(cmds.args.compose[0])
    assert isinstance(compose_file, str) or compose_file is None

    cmds.logger.info(f"load '{filepath}'")
    asmf = assemble_file(filepath, template_file=template_file,
                         compose_file=compose_file)
    # mount host timezone and localtime to container
    for servive in asmf.compose.services:
        if cmds.args.mount_timezone:
            servive.mount("/etc/timezone", "/etc/timezone", True)
        if cmds.args.mount_localtime:
            servive.mount("/etc/localtime", "/etc/localtime", True)

    cmds.logger.info(f"dump '{asmf.compose_file}'")
    cmds.logger.debug(asmf.compose)
    asmf.dump()
    return 0
