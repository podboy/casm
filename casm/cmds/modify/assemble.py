# coding:utf-8

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command


@add_command("assemble", help="Modify assemble file")
def add_cmd_assemble(_arg: argp):
    pass


@run_command(add_cmd_assemble)
def run_cmd_assemble(cmds: commands) -> int:
    return 0
