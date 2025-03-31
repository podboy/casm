# coding:utf-8

from errno import ESRCH
from threading import Thread
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from casm.utils.podman import podman_container


def add_pos_containers(_arg: ArgParser):
    _arg.add_argument(dest="containers", type=str, nargs="*",
                      metavar="CONTAINER", action="extend",
                      choices=list(podman_container.list(all=True)) + [[]],
                      help="Specify containers, default ALL")


@CommandArgument("guard", help="Guard podman container")
def add_cmd_container_guard(_arg: ArgParser):
    _arg.add_opt_on("--daemon", dest="daemon", help="run in daemon mode")
    _arg.add_argument("--daemon-min-delay", type=int, metavar="SECONDS",
                      help="minimum delay interval in seconds for daemon mode",
                      dest="daemon_min_delay", default=30)
    _arg.add_argument("--daemon-max-delay", type=int, metavar="SECONDS",
                      help="maximum delay interval in seconds for daemon mode",
                      dest="daemon_max_delay", default=3600)
    add_pos_containers(_arg)


@CommandExecutor(add_cmd_container_guard)
def run_cmd_container_guard(cmds: Command) -> int:
    def guard_container(container: podman_container) -> int:
        cmds.logger.info("guard container %s begin", container.container_name)
        exit_code: int = container.guard()
        cmds.logger.info("guard container %s end, exit-code: %d",
                         container.container_name, exit_code)
        return exit_code

    container_names: Iterable[str] = cmds.args.containers or podman_container.list(all=True)  # noqa:E501
    containers: List[podman_container] = [podman_container(name) for name in container_names]  # noqa:E501
    if cmds.args.daemon:
        min_delay: int = cmds.args.daemon_min_delay
        max_delay: int = cmds.args.daemon_max_delay

        threads: Set[Thread] = set()
        for container in containers:
            thread: Optional[Thread] = container.daemon(block=False, min_delay=min_delay, max_delay=max_delay)  # noqa:E501
            assert isinstance(thread, Thread), f"failed to create container {container.container_name } daemon thread"  # noqa:E501
            threads.add(thread)

        for thread in threads:
            thread.join()
        return ESRCH
    else:
        for container in containers:
            if (exit_code := guard_container(container)) != 0:
                cmds.logger.error("failed to guard container %s",
                                  container.container_name)
                return exit_code
    return 0


@CommandArgument("container", help="Manage podman containers")
def add_cmd_container(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_container, add_cmd_container_guard)
def run_cmd_container(cmds: Command) -> int:
    return 0
