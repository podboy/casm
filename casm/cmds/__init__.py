# coding:utf-8

from errno import ENOENT
import os
from typing import Optional
from typing import Sequence

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ..utils import URL_PROG
from ..utils import __prog_name__
from ..utils import __version__
from ..utils import assemble_file
from .modify import add_cmd_modify
from .podman import add_cmd_system
from .podman import add_cmd_systemd
from .podman_compose import add_cmd_down
from .podman_compose import add_cmd_exec
from .podman_compose import add_cmd_logs
from .podman_compose import add_cmd_pause
from .podman_compose import add_cmd_pull
from .podman_compose import add_cmd_restart
from .podman_compose import add_cmd_start
from .podman_compose import add_cmd_stop
from .podman_compose import add_cmd_unpause
from .podman_compose import add_cmd_up
from .service import add_cmd_services

DEF_INSTANCE = assemble_file.DEF_CONFIG_FILE


@add_command(__prog_name__)
def add_cmd(_arg: argp):
    _arg.add_argument("--instance", type=str, nargs=1, metavar="INSTANC",
                      help=f"YAML format config file, default {DEF_INSTANCE}")
    _arg.add_argument("--template", type=str, nargs=1, metavar="TEMPLATE",
                      help="Specify template file")
    _arg.add_argument("--project-name", type=str, nargs=1, metavar="NAME",
                      help="Specify project name")


@run_command(add_cmd, add_cmd_pull, add_cmd_up, add_cmd_down,
             add_cmd_start, add_cmd_stop, add_cmd_restart,
             add_cmd_pause, add_cmd_unpause, add_cmd_exec, add_cmd_logs,
             add_cmd_system, add_cmd_systemd, add_cmd_services, add_cmd_modify)
def run_cmd(cmds: commands) -> int:
    instance: str = DEF_INSTANCE
    if isinstance(cmds.args.instance, list):
        instance = cmds.args.instance[0]
    assert isinstance(instance, str)

    filepath: str = os.path.abspath(instance)
    if os.path.exists(filepath) and not os.path.isfile(filepath):
        cmds.logger.error(f"No such file '{filepath}'")
        return ENOENT

    template_file: Optional[str] = None
    if isinstance(cmds.args.template, list):
        template_file = os.path.abspath(cmds.args.template[0])
    assert isinstance(template_file, str) or template_file is None

    project_name: Optional[str] = None
    if isinstance(cmds.args.project_name, list):
        project_name = cmds.args.project_name[0]
    assert isinstance(project_name, str) or project_name is None

    cmds.logger.info(f"load assemble file: '{filepath}'")
    asmf = assemble_file(filepath, project_name=project_name,
                         template_file=template_file)
    cmds.logger.debug(asmf.template.dump())
    cmds.args.assemble_file = asmf
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="assemble compose",
        epilog=f"For more, please visit {URL_PROG}.")
