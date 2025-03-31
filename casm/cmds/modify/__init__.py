# coding:utf-8

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.cmds.modify.assemble import add_cmd_assemble
from casm.cmds.modify.template import add_cmd_template


@CommandArgument("modify", help="Modify assemble or template")
def add_cmd_modify(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_modify, add_cmd_assemble, add_cmd_template)
def run_cmd_modify(cmds: Command) -> int:
    return 0
