# coding:utf-8

import os
from string import Template
from typing import Any
from typing import Dict
from typing import Optional
from typing import Sequence

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command
import yaml

from ..util import URL_PROG
from ..util import __prog_compose__
from ..util import __version__

DEF_INSTANCE = "assembler.yml"
KEY_VARIABLES = "variables"
KEY_PROJECT_NAME = "project-name"
KEY_TEMPLATE_FILE = "template-file"
DEF_TEMPLATE_FILE = "compose.yml"
KEY_COMPOSE_FILE = "compose-file"
DEF_COMPOSE_FILE = "docker-compose.yml"


def safe_dump(data: Any) -> str:
    return yaml.safe_dump(data, allow_unicode=True, indent=2, sort_keys=False)


def load_cfgs(instance: str) -> Dict[str, Any]:
    assert os.path.isfile(instance), f"No such file: '{instance}'"
    with open(instance, "r") as handle:
        cfgs = yaml.safe_load(handle)
        assert isinstance(cfgs, dict)
        cfgs.setdefault(KEY_TEMPLATE_FILE, DEF_TEMPLATE_FILE)
        cfgs.setdefault(KEY_COMPOSE_FILE, DEF_COMPOSE_FILE)
        return cfgs


def load_vars(vars_dict: Dict[str, str]) -> Dict[str, str]:
    assert type(vars_dict) is dict
    vars = {k: v for k, v in os.environ.items()}
    for k, v in vars_dict.items():
        assert v is not None, f'variable "{k}" not set'
        assert isinstance(v, str), f"{type(v)} not str"
        try:
            value = Template(v).substitute(vars)
        except KeyError:
            raise KeyError(f"variable {k}: {v}")
        vars[k] = value
    for k, v in vars.items():
        assert isinstance(k, str), f"{type(k)} not str"
        assert isinstance(v, str), f"{type(v)} not str"
    return vars


def load_tmpl(path: str, variables: Dict[str, str]) -> Any:
    assert type(path) is str
    assert os.path.isfile(path)
    with open(path, "r") as handle:
        source = handle.read()
        target = Template(source).substitute(variables)
        return yaml.safe_load(target)


def run_assembler(cmds: commands, instance: str) -> int:
    assert isinstance(instance, str)
    cmds.logger.info(f"load instance '{instance}'")
    cfgs = load_cfgs(instance)
    cmds.logger.debug(cfgs)
    vars = load_vars(vars_dict=cfgs[KEY_VARIABLES])
    data = load_tmpl(path=cfgs[KEY_TEMPLATE_FILE], variables=vars)
    pose = safe_dump(data)
    with open(cfgs[KEY_COMPOSE_FILE], "w") as output:
        cmds.logger.info(f"output to '{cfgs[KEY_COMPOSE_FILE]}'")
        cmds.logger.debug(pose)
        output.write(pose)
        return 0


def add_opt_instances(_arg: argp):
    _arg.add_argument(dest="instances", type=str, nargs="*",
                      action="extend", metavar="INSTANC",
                      help=f"YAML format config file, default {DEF_INSTANCE}")


@add_command("assembler")
def add_cmd_assembler(_arg: argp):
    _arg.add_opt_on("--no-timezone")
    _arg.add_opt_on("--no-localtime")
    add_opt_instances(_arg)


@run_command(add_cmd_assembler)
def run_cmd_assembler(cmds: commands) -> int:
    instances = cmds.args.instances
    assert isinstance(instances, list)
    if len(instances) == 0:
        instances.append(DEF_INSTANCE)
    for instance in instances:
        run_assembler(cmds, instance)
    return 0


@add_command(__prog_compose__)
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd, add_cmd_assembler)
def run_cmd(cmds: commands) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="assembler compose",
        epilog=f"For more, please visit {URL_PROG}.")
