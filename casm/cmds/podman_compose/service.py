# coding:utf-8

import os
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.utils.assemble import assemble_file
from casm.utils.compose import compose_services
from casm.utils.yaml import safe_load_file

global_argv: Optional[List[str]] = None
global_svrs: Optional[List[Union[str, List[Any]]]] = None


def list_services() -> Optional[List[Union[str, List[Any]]]]:
    global global_argv
    global global_svrs
    local_argv = sys.argv

    if local_argv == global_argv:
        return global_svrs

    def get_template():

        try:
            idx: int = local_argv.index("--template")
            return local_argv[idx + 1]
        except ValueError:
            pass
        except IndexError:
            pass

        def get_instance():
            try:
                idx: int = local_argv.index("--instance")
                return local_argv[idx + 1]
            except ValueError:
                pass
            except IndexError:
                pass
            return assemble_file.DEF_CONFIG_FILE

        instance = get_instance()
        if os.path.isfile(instance):
            data = safe_load_file(instance)
            if isinstance(data, Dict):
                if assemble_file.KEY_TEMPLATE_FILE in data:
                    return data[assemble_file.KEY_TEMPLATE_FILE]
        return assemble_file.DEF_TEMPLATE_FILE

    template = get_template()
    if os.path.isfile(template):
        tmpl = safe_load_file(template)
        if isinstance(tmpl, Dict) and compose_services.KEY in tmpl:
            services = tmpl[compose_services.KEY]
            if isinstance(services, Dict):
                global_svrs = list({k for k in services if isinstance(k, str)})
                global_svrs.append([])

    global_argv = local_argv
    return global_svrs


def add_pos_services(_arg: ArgParser):
    _arg.add_argument(dest="services", type=str, nargs="*", metavar="SERVICE",
                      action="extend", choices=list_services(),
                      help="Specify services, default ALL")


def filter_services(assemble: assemble_file, services: List[str]) -> List[str]:
    names: List[str] = [s.title for s in assemble.template.services]
    return [s for s in names if s in services]


@CommandArgument("services", help="List all services")
def add_cmd_services(_arg: ArgParser):
    mgrp = _arg.add_mutually_exclusive_group()
    mgrp.add_argument("--service-name", action="store_true",
                      help="Only output service_name")
    mgrp.add_argument("--container-name", action="store_true",
                      help="Only output container_name")


@CommandExecutor(add_cmd_services)
def run_cmd_services(cmds: Command) -> int:
    assemble: assemble_file = cmds.args.assemble_file
    assert isinstance(assemble, assemble_file)
    for service in assemble.template.services:
        service_name: str = service.title
        container_name: str = assemble.safe_substitute(service.container_name)
        if cmds.args.service_name:
            cmds.stdout(service_name)
            continue
        if cmds.args.container_name:
            cmds.stdout(container_name)
            continue
        cmds.stdout(f"{service_name}: {container_name}")
    return 0
