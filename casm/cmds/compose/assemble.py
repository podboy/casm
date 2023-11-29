# coding:utf-8

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ...utils import assemble_file

DEF_INSTANCE = "assemble.yml"


def add_opt_instances(_arg: argp):
    _arg.add_argument(dest="instances", type=str, nargs="*",
                      action="extend", metavar="INSTANC",
                      help=f"YAML format config file, default {DEF_INSTANCE}")


@add_command("assemble")
def add_cmd_assemble(_arg: argp):
    _arg.add_opt_on("--no-timezone")
    _arg.add_opt_on("--no-localtime")
    add_opt_instances(_arg)


@run_command(add_cmd_assemble)
def run_cmd_assemble(cmds: commands) -> int:
    instances = cmds.args.instances
    assert isinstance(instances, list)
    if len(instances) == 0:
        instances.append(DEF_INSTANCE)
    for instance in instances:
        cmds.logger.info(f"load instance '{instance}'")
        asmf = assemble_file(instance)
        for servive in asmf.compose.services:
            servive.mount("/etc/timezone", "/etc/timezone", True)
            servive.mount("/etc/localtime", "/etc/localtime", True)
        cmds.logger.info(f"dump to '{asmf.compose_file}'")
        cmds.logger.debug(asmf.compose)
        asmf.dump()
    return 0
