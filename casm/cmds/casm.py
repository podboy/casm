# coding:utf-8

from errno import ENOENT
import os
from typing import Optional
from typing import Sequence

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.attribute import __project__
from casm.attribute import __urlhome__
from casm.attribute import __version__
from casm.cmds.modify import add_cmd_modify
from casm.cmds.podman.system import add_cmd_system
from casm.cmds.podman_compose.down import add_cmd_down
from casm.cmds.podman_compose.exec import add_cmd_exec
from casm.cmds.podman_compose.logs import add_cmd_logs
from casm.cmds.podman_compose.pause import add_cmd_pause
from casm.cmds.podman_compose.pull import add_cmd_pull
from casm.cmds.podman_compose.restart import add_cmd_restart
from casm.cmds.podman_compose.service import add_cmd_services
from casm.cmds.podman_compose.start import add_cmd_start
from casm.cmds.podman_compose.stop import add_cmd_stop
from casm.cmds.podman_compose.systemd import add_cmd_systemd
from casm.cmds.podman_compose.unpause import add_cmd_unpause
from casm.cmds.podman_compose.up import add_cmd_up
from casm.utils.assemble import assemble_file

DEF_INSTANCE = assemble_file.DEF_CONFIG_FILE


@CommandArgument(__project__)
def add_cmd(_arg: ArgParser):
    _arg.add_argument("--instance", type=str, nargs=1, metavar="INSTANC",
                      help=f"YAML format config file, default {DEF_INSTANCE}")
    _arg.add_argument("--template", type=str, nargs=1, metavar="TEMPLATE",
                      help="Specify template file")
    _arg.add_argument("--project-name", type=str, nargs=1, metavar="NAME",
                      help="Specify project name")
    _arg.add_argument("-e", "--env", type=str, nargs=1, metavar="STR",
                      dest="environments", action="extend",
                      help="Set environment variables")


@CommandExecutor(add_cmd, add_cmd_pull, add_cmd_up, add_cmd_down,
                 add_cmd_start, add_cmd_stop, add_cmd_restart,
                 add_cmd_pause, add_cmd_unpause, add_cmd_exec, add_cmd_logs,
                 add_cmd_system, add_cmd_systemd,
                 add_cmd_services, add_cmd_modify)
def run_cmd(cmds: Command) -> int:
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

    if isinstance(cmds.args.environments, list):
        for e in cmds.args.environments:
            assert asmf.variables.update(e)

    cmds.logger.debug(asmf.template.dump())
    cmds.args.assemble_file = asmf
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="assemble compose",
        epilog=f"For more, please visit {__urlhome__}.")
