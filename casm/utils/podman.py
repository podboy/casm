# coding:utf-8

import os
from typing import List
from typing import Optional

SERVICE_NAME = "container-{name}.service"
SYSTEMD_PATH = "/etc/systemd/system/{service_name}"


class podman_cmd:
    '''
    Execute podman command
    '''

    def __init__(self):
        pass

    @classmethod
    def run(cls, *args: str) -> int:
        def exec(*cmds: Optional[str]) -> int:
            cmd = " ".join([c for c in cmds if c is not None])
            assert isinstance(cmd, str)
            return os.system(cmd)
        cmds: List[Optional[str]] = ["podman"]
        cmds.extend([i for i in args if len(i) > 0])
        return exec(*cmds)

    @classmethod
    def system_prune(cls, all: bool = False, external: bool = False,
                     force: bool = False, volumes: bool = False) -> int:
        return cls.run("system", "prune")

    @classmethod
    def stop_service(cls, name: str) -> int:
        assert isinstance(name, str)
        service_name = SERVICE_NAME.format(name=name)
        return os.system(f"systemctl stop {service_name}")

    @classmethod
    def enable_service(cls, name: str) -> int:
        assert isinstance(name, str)
        service_name = SERVICE_NAME.format(name=name)
        path = SYSTEMD_PATH.format(service_name=service_name)
        errno = os.system(f"podman generate systemd --name {name} > {path}")
        if errno != 0:
            if os.path.isfile(path):
                os.remove(path)
            return errno
        errno = os.system(f"systemctl enable --now {service_name}")
        if errno != 0:
            return errno
        return 0

    @classmethod
    def disable_service(cls, name: str) -> int:
        assert isinstance(name, str)
        service_name = SERVICE_NAME.format(name=name)
        errno = os.system(f"systemctl stop {service_name}")
        if errno != 0:
            return errno
        errno = os.system(f"systemctl disable {service_name}")
        if errno != 0:
            return errno
        path = SYSTEMD_PATH.format(service_name=service_name)
        if os.path.isfile(path):
            os.remove(path)
        return 0
