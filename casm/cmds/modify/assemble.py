# coding:utf-8

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor


@CommandArgument("assemble", help="Modify assemble file")
def add_cmd_assemble(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_assemble)
def run_cmd_assemble(cmds: Command) -> int:
    return 0
