# coding:utf-8

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command


@add_command("assemble", help="Modify assemble file")
def add_cmd_assemble(_arg: argp):
    pass


@run_command(add_cmd_assemble)
def run_cmd_assemble(cmds: commands) -> int:
    return 0
