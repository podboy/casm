# coding:utf-8

import os
from typing import List
from typing import Optional


class podman_compose_cmd:
    '''
    run podman_compose command
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
        def exec(*cmds: str) -> int:
            cmd = " ".join([c for c in cmds if c is not None])
            assert isinstance(cmd, str)
            return os.system(cmd)
        cmds = ["podman-compose", self.opt_file]
        cmds.extend([i for i in args if len(i) > 0])
        return exec(*cmds)

    def pull(self, *services: str) -> int:
        return self.run("pull", *services)

    def up(self, *services: str, detach: bool = False) -> int:
        cmds: List[str] = ["up"]
        if detach:
            cmds.append("--detach")
        cmds.extend(services)
        return self.run(*cmds)

    def down(self, *services: str) -> int:
        return self.run("down", *services)

    def start(self, *services: str) -> int:
        return self.run("start", *services)

    def stop(self, *services: str) -> int:
        return self.run("stop", *services)

    def restart(self, *services: str) -> int:
        return self.run("restart", *services)

    def pause(self, *services: str) -> int:
        return self.run("pause", *services)

    def unpause(self, *services: str) -> int:
        return self.run("unpause", *services)
