# coding:utf-8

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command

from .assemble import add_cmd_assemble
from .template import add_cmd_template


@add_command("modify", help="Modify assemble or template")
def add_cmd_modify(_arg: argp):
    pass


@run_command(add_cmd_modify, add_cmd_assemble, add_cmd_template)
def run_cmd_modify(cmds: commands) -> int:
    return 0
