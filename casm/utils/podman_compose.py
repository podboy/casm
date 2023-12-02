# coding:utf-8

import os
from typing import List
from typing import Optional


class podman_compose_cmd:
    '''
    Execute podman_compose command
    '''

    def __init__(self, compose_file: Optional[str]):
        if isinstance(compose_file, str):
            assert os.path.isfile(compose_file)
        else:
            assert compose_file is None
        self.__compose_file: Optional[str] = compose_file

    @property
    def opt_file(self) -> Optional[str]:
        if self.__compose_file is None:
            return None
        return f"--file {self.__compose_file}"

    def run(self, *args: str) -> int:
        def exec(*cmds: Optional[str]) -> int:
            cmd = " ".join([c for c in cmds if c is not None])
            assert isinstance(cmd, str)
            return os.system(cmd)
        cmds: List[Optional[str]] = ["podman-compose", self.opt_file]
        cmds.extend([i for i in args if len(i) > 0])
        return exec(*cmds)

    def pull(self, services: List[str]) -> int:
        return self.run("pull", *services)

    def up(self, services: List[str], detach: bool = False) -> int:
        cmds: List[str] = ["up"]
        if detach:
            cmds.append("--detach")
        cmds.extend(services)
        return self.run(*cmds)

    def down(self, services: List[str]) -> int:
        return self.run("down", *services)

    def start(self, services: List[str]) -> int:
        return self.run("start", *services)

    def stop(self, services: List[str]) -> int:
        return self.run("stop", *services)

    def restart(self, services: List[str]) -> int:
        return self.run("restart", *services)

    def pause(self, services: List[str]) -> int:
        return self.run("pause", *services)

    def unpause(self, services: List[str]) -> int:
        return self.run("unpause", *services)

    def exec(self, service: str, arguments: List[str], detach: bool = False,
             privileged: bool = False, user: Optional[str] = None,
             T: bool = False, index: Optional[int] = None) -> int:
        cmds: List[str] = ["exec"]
        if detach:
            cmds.append("--detach")
        if privileged:
            cmds.append("--privileged")
        if isinstance(user, str):
            cmds.append(f"--user {user}")
        if T:
            cmds.append("-T")
        if isinstance(index, int):
            cmds.append(f"--index {index}")
        cmds.append(service)
        cmds.extend(arguments)
        return self.run(*cmds)

    def logs(self, services: List[str], follow: bool = False,
             tail: Optional[int] = None) -> int:
        cmds: List[str] = ["logs"]
        if follow:
            cmds.append("--follow")
        if isinstance(tail, int):
            cmds.append(f"--tail {tail}")
        cmds.extend(services)
        return self.run(*cmds)
